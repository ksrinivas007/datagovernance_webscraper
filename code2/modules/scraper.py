from posix import listdir
import requests
from bs4 import BeautifulSoup
import re
from typing import List
import tabula
import csv
import subprocess
import os
import glob
import pandas as pd
from pymongo import MongoClient


from pprint import pprint

from settings.settings import BROWSER_HEADERS, BASE_URL, PDF_FOLDER
from classes.Standards import Standards
from classes.StandardsPDFs import StandardsPDFs
from modules.to_csv import data_to_csv

# while using docker 
client = MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
# while development locally
#client = MongoClient('localhost', 27017)
db = client.appdb

def get_html(url: str) -> str:
    """[summary]

    Args:
        url (str): [description]

    Returns:
        str: [description]
    """
    successful = False
    while not successful:

        try:
            headers = {"User-Agent": BROWSER_HEADERS}
            page_html = requests.get(url, headers=headers)

        except Exception as e:
            print(f"Error: {e}")

        if page_html.status_code == 200:
            successful = True
        else:
            print(page_html.status_code)
            print("retring...")
            sleep(10)

    return page_html.text


def parser(page_html: str) -> List:
    """[summary]

    Args:
        page_html (str): [description]

    Returns:
        list: [description]
    """

    soup = BeautifulSoup(page_html, 'html.parser')
    
    data = []

    table = soup.find('table')
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    
    for row in rows[:-1]:       # hack the last row of the table is always empty
        td = row.find_all('td')
        link = row.find('a', attrs={'href': re.compile("^https://")}).get('href')

        standard = Standards()

        standard.set_date(td[0].text.strip()) 
        standard.set_no_published(td[1].text.strip()) 
        standard.set_standard(td[2].text.strip()) 
        standard.set_link(link)

        data.append(standard) 

    return data
    

def download_pdfs(data: List) -> None:
    """[summary]

    Args:
        data (List): [description]
    """
    for ele in data: 

        filename = PDF_FOLDER + str(ele.link.split('/')[-1])
        
        # open in binary mode
        with open(filename, "wb") as file:
            # get request
            response = requests.get(ele.link)
            # write to file
            file.write(response.content)


def parse_pdfs(data: List) -> None:
    """[summary]

    Args:
        data (List): [description]
    """
  
    print(data[0])
    print(len(data))
    for ele in data:
        
        try:
            # LOAD PDF DIRECTLY TO MONGDO WITHOUT CONVERTING TO CSN
            pdf_name = str(ele.link.split('/')[-1])

            filename = PDF_FOLDER + pdf_name

            # tables = tabula.read_pdf(filename, pages = "all", multiple_tables = True)
            table = tabula.read_pdf(filename, pages='all', multiple_tables = True, encoding='utf-8')

            if table:
                dt = table[0]

            # dt.to_csv()
            csv = dt.to_csv(sep="_")

            csv_list = csv.split('\n')

            parsed_pdf = {
                "filename": pdf_name,
                "status": "ok",
                "number of entries": len(csv_list),
                "data": []
            }

            parsed_data_dict_list = []
            for line in csv_list[2:-2]:
                
                data = line.split('_')

                try:
                    # print(data)
                    temp ={
                            "index": data[0],
                            "Reference": data[1],
                            "Title En": data[2],
                            "Origin Body": data[3],
                            "Publication D": data[4],       
                    }

                    parsed_data_dict_list.append(temp)
                
                except Exception as e:
                    print("error parsing pdf:", pdf_name, e)
                    parsed_pdf["status"] = "error"
                    temp = None

                parsed_pdf["data"] = parsed_data_dict_list

            # create csv
            if parsed_pdf["status"] == "ok":
                data_to_csv(parsed_pdf["data"], pdf_name)

            db.parsed_pdfs.insert_one(parsed_pdf)
        
            
            
        except:
            print("pdf parse error")
            print(pdf_name)
            pass

def bulk_load_to_db() -> None:
    # Tried bulk load of documents. works locally but does not work in container due to subprocess command used in mongoimport
    # preparing the file for bulk load. need to remove the title record

    filenamecsv = str(ele.link.split('/')[-1])
    fullfilename = PDF_FOLDER + filenamecsv
    df = tabula.read_pdf(fullfilename, pages='all', multiple_tables = True)
    csvfilename = filenamecsv+".csv"
    fullcsvfilename = PDF_FOLDER + 'csv/' + csvfilename
    df[0].to_csv(fullcsvfilename , encoding='utf-8')

    # use with docker. did not work. there is a solution by importing mongodbtools
    client = MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
    # use locally 
    #client = MongoClient('localhost', 27017)
    db = client.appdb
    #path = '/root/sk_govern9/sk_9/code2loc/code2loc/pdf/csv/'
    path = PDF_FOLDER+'csv/'

    for infile in glob.glob(os.path.join(path, '*.csv')):
        print ("currently uploading: " + infile)
        # # remove the title of the pdf present as the first row
        subprocess.call(["sed", "-i", "1d", infile])
        # # load the csv to mongo
        p=subprocess.Popen(['mongoimport', '--type','csv','-d', 'appdb',
                  '-c', 'pdfdata7','--headerline',
                  '--file', infile],
                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print (line)
        retval = p.wait()

def generate_scraping_score(data: List) -> None:
    """[summary]

    Args:
        data (List): [description]
    """
    global final_weighted_scraping_score
    total_weighted_scraping_score = 0.0
    # holds the list of 200+ synonyms for the word 'change'
    list_of_synonyms_transition=['change','evolution','progression','shift','transformation','adaptation','adjustment','conversion','development','gradation','growth','modification','move','mutation','passage','progress','switch','transfiguration','alteration','amendment','jump','leap','metamorphosis','metastasis','modulation','realignment','reformation','remodelingUS','remodellingUK','reshaping','revision','changeover','crossing','departure','deviation','flux','passing','transit','transmogrification','transmutation','turn','turning point','upheaval','course','difference','diversification','makeover','metanoia','motion','operation','path','process','procession','rearrangement','variance','variation','vicissitude','revolution','permutation','about-face','advance','reversal','reconstruction','correction','transfer','translation','innovation','refinement','recasting','movement','transubstantiation','turnover','tempering','addition','diversity','variety','novelty','break','refashioning','reworking','flip-flop','revamping','reordering','reorganizationUS','journey','reorganisationUK','compression','contraction','surrogate','distortion','sea change','fluctuation','moving','remaking','swap','mutability','remouldingUK','rebuilding','remoldingUS','redoing','substitution','renewal','flow','restyling','readjustment','regeneration','transportation','conveyance','swing','redesign','redevelopment','relocation','oscillation','traverse','turnaround','crossover','alternation','revolutionizingUS','turning','rejigging','transporting','transference','journeying','transposition','about-turn','morph','reshuffling','renovation','revolutionisingUK','changing','altering','rise','renewing','advancement','metasis','evolvement','U-turn','mid-course correction','turning around','rapid transition','shuffle','specialisationUK','replacement','interchange','vagary','cross','vacillation','redirection','improvement','reverse','veering','newfangledness','innovativeness','specializationUS','diversion','downturn','switchover','retraction','stirring','wavering','rowback','change of direction','yaw','deflection','bend','stir','cutover','resolution','see the light','exchange','born again','resolving','qualification','reclamation','transport','go over','transferal','transplanting','carriage','travel','change of fortune','pass','shipment','shifting','migration','overhaul','instability','inconstancy','transferral','displacement','repositioning','haulage','travellingUK','freightage','rebirth','fluidity','transfigurement','portage','unsteadiness','fitfulness','variability','irregularity','changeability','changeableness','unpredictability','flight','withdrawal','voyaging','unrest','fickleness','unreliability','continuous change','carrying','osmosis','travelingUS','infiltration','penetration','permeation','complete change','radical change','see-sawing','yo-yoing','revolutionary change','rising and falling','rise and fall','march','spread','proceeding','advent','unfolding','expedition','stride','drift','going','buildup','headway','nearing','forward movement','encroachment','stepping forward','momentum','furtherance','promotion','gain','stream','onrush','voyage','expansion','arrival','increase','coming','review','revise','rectification','restructuring','amelioration','betterment','tailoring','reform','enhancement','editing','shake-up','refitting','emendation','revamp','re-examination','rewriting','arrangement','redrafting','rephrasing','rethink','rehab','restoration','accommodation','rehabilitation','evolving','redraft','rectifying','maturation','repair','acclimation','fixing','mending','modernization','customizationUS','converting','regulation','reassessment','maturing','reconsideration','re-evaluation','organizationUS','redistribution','regrouping','customisationUK','reappraisal','overhauling','refining','clarification','rationalizationUS','settlement','rewording','growing','orientation','fitting','adaption','reconciliation','customizingUS','fruition','reshuffle','rewrite','copy-editing','retrospect','organisationUK','maturity','customisingUK','rationalisationUK','flowering','redaction','ripening','shakedown','coming-of-age','revisal','enlargement','selection','rendering','redecoration','refurnishing','refurbishing','beautification','cosmetic treatment','varying','reforming','restriction','rotation','manipulation','rethinking','reconstitution','reassembling','transspecific evolution','redesigning','drastic','shakeout','repetition','adoption','tweak','reorganizingUS','remake','reorienting','divergence','nuance','updating','switch-over','reorientation','natural process','volte-face','reorganisingUK']
    
    # holds the list of 200+ synonyms for the word 'construction' 
    list_of_synonyms_construction=['building','assembly','creation','development','erection','fabrication','making','composition','establishment','manufacture','origination','production','raising','structure','contriving','erecting','fabricating','fashioning','formation','arrangement','casting','constitution','invention','architecture','conception','elevation','figuration','format','forming','foundation','putting up','setting up','formulation','manufacturing','inception','putting together','design','institution','devising','initiation','forging','shaping','modellingUK','inauguration','generation','engineering','produce','modelingUS','fitting together','founding','genesis','organizationUS','product','preparation','joining','introduction','installation','start','connection','laying down','producing','mass-production','planning','piecing together','organisationUK','composing','preparing','assembling','concoction','mouldingUK','occasioning','causation','moldingUS','engendering','mass production','imagination','connecting','coupling','compilation','provision','constructing','contrivance','junction','attachment','joint','hatching','jointure','join','juncture','induction','nascency','set-up','drawing up','getting going','linking','thinking up','laborUS','handiwork','realizationUS','output','labourUK','realisationUK','build','setting-up','architectonics','assemblage','completion','doing','tooling','finishing','accomplishment','planting','construct','industry','innovation','discovery','incorporation','masterminding','pioneering','spawning','causing','nativity','interpretation','rendering','framing','writing','prefabrication','triggering','kindling','prompting','inspiration','emergence']
    print(len(data))
    count = 1
    # step 1 - count of synoynms for word 'transition'
    length_synonyms_transition = len(list_of_synonyms_transition)

    # step 1 - count of synoynms for word 'construction'
    constantfactor=150
    length_synonyms_construction = len(list_of_synonyms_construction)
    for ele in data:
        
        try:
            filename = str(ele.link.split('/')[-1])
            
            csvfilename = filename+".csv"
            fullcsvfilename = PDF_FOLDER + 'csv/' + csvfilename
            with open(fullcsvfilename,"r")as file:
                csvdata=file.read()
                # algorithm to derive weighted score on  'changes in construction standards'
                # step 1 - count of match
                count_match = len(re.findall(r"(?=("+'|'.join(list_of_synonyms_transition)+r"))",csvdata))
                # step 2 - apply weighted score algorithm
                weighted_score_transition = (0.2*(count_match/length_synonyms_transition) + 0.8*(count_match/len(csvdata)))
                # step 3 - count of match for word 'transition'
                count_match = len(re.findall(r"(?=("+'|'.join(list_of_synonyms_construction)+r"))",csvdata))
                # step 4 - count of match for word 'construction'
                weighted_score_construction = (0.2*(count_match/length_synonyms_construction) + 0.8*((count_match*constantfactor)/len(csvdata)))
                #weighted_score_construction = (0.2*(count_match/length_synonyms) + 0.8*(count_match/len(csv)))
                file_weighted_scraping_score = weighted_score_transition + weighted_score_construction
                print(file_weighted_scraping_score)
                total_weighted_scraping_score = total_weighted_scraping_score + file_weighted_scraping_score
                      
            
        except:
            print("CSV FILENAME error")
            print(csvfilename)
            pass
    
    final_weighted_scraping_score = total_weighted_scraping_score/len(data)
    print("FINAL")
    print (final_weighted_scraping_score)

def scraper() -> float:
    """[summary]

    Returns:
        [type]: [description]
    """
    ## 1. BUILD URL
    url = BASE_URL

    ## 2. GET WEBPAGE
    page_html = get_html(url=url)
    
    ## 3. PARSE WEB
    data = parser(page_html=page_html)

    ## 4. DOWNLOAD PDFs
    download_pdfs(data=data)

    ## 5. PARSE PDFs
    parse_pdfs(data=data)

    ## 6. BULK LOAD to DB
    #bulk_load_to_db()

  
    ## 7. DERIVE SCRAPING SCORE (usecase - scrape 'changes' to  standards in 'construction industry')
    ## 7.1 Step 1 - get LIST OF SYNYONYMS of the word 'change' and 'construction' from web
    ## 7.2 Step 2 - regex  COUNT OF MATCH for the above synonyms 
    ## 7.3 Step 3 - apply a weighted score algorithm
    ## 7.4 Step 4 (NEXT STEPS not in this POC) - apply NLP to decipher named entities , perfrom sentiment analysis , train the model
    ## 7.5 Step 5 (NEXT STEPS not in this POC) - add Redis Queue or Celery for asynchronouse processing of multiple scraping links
    generate_scraping_score(data=data)

    #return final scraping score
    return final_weighted_scraping_score