import os
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient, DESCENDING
from datetime import datetime
import time
# # added for analysis using wordcloud 
#import wordcloud
#import matplotlib.pyplot as plt 
#import pandas

from modules.scraper import scraper
from settings.settings import BASE_URL


app = Flask("DataGovernance" , template_folder='code2/templates', static_folder='code2/static' )


# To change accordingly 
print(os.environ)
client = MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
#client = MongoClient('localhost', 27017)
db = client.appdb

# index
@app.route("/")
@app.route("/home")
def home():
    _items = db.appdb.find()
    items = [items for items in _items]
    return render_template("home.html", items=items)

    # CODE FOR WORD CLOUD used for data analysis (not integrated in this POC)
    #wc = wordcloud.WordCloud(background_color='black', max_words=100, 
    #                     max_font_size=35)
    #webstring2 = """Organizations that are already taking an exclusion to a requirement in their ISO 9001:2008-based QMS should be able to determine the requirement still no longer applies when they transition to ISO 9001:2015.
    #         Risk-based thinking Another concept that has been integrated into ISO 9001:2015 is risk-based thinking. Although risk was implied in previous versions of ISO 9001, the word “risk” is now actually used in ISO 9001:2015. Using risk-based thinking allows an organization to determine the level of controls needed for certain requirements, thereby reducing some requirements that were seen as more prescriptive than others.
    #         In alignment with risk-based thinking, ISO 9001:2015 doesn’t use the term “preventive action.” The language in the standard looks at how an organization determines the risks and opportunities that need to be addressed as part of an effective QMS. Subclause 6.1, Actions to address risks and opportunities, includes requirements to ensure that the QMS can achieve its intended outputs. It also addresses taking action appropriate to the potential effect of conformity of products and services and preventing the occurrence of potential issues.
    #         Understanding the change Subclause 6.1 includes a note that"""                     
    #wc = wc.generate(str(webstring2))
    #fig = plt.figure(num=1)
    #plt.axis('off')
    #plt.imshow(wc, cmap=None)
    #obj=plt.show()
    
    #return render_template("index.html", obj)

# /new
@app.route("/new", methods=["POST"])
def new():

    # getting the last index
    last_doc = db.appdb.find_one( sort=[( '_id', DESCENDING )])
    last_int = int(last_doc["serial_num"]) + 1

    data = {
        "serial_num": last_int,
        "date_ran": datetime.today().strftime('%Y-%m-%d'),
        "url": BASE_URL,
        "scraping_score": "",
        "time_taken": "",
    }

    # call to scraprer
    start_time = time.perf_counter()
    scraping_score = scraper()
    scraping_score_percent = "{:.2%}".format(scraping_score)
    end_time = time.perf_counter()
 
    data["time_taken"] = f'{end_time - start_time:.2f}'
    data["scraping_score"] = scraping_score_percent
    #data["scraping_score"] = f'{scraping_score:.2f}'

    db.appdb.insert_one(data)

    return redirect(url_for("home"))

@app.route("/about")
def about():
    return "<h1>POC on a Data Governance Platform in Cloud</h1>"

@app.route("/login")
def login():
    return "<h1>Ooops !!  Page under construction :)</h1>"

@app.route("/register")
def register():
    return "<h1>Ooops !!  Page under construction :)</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

