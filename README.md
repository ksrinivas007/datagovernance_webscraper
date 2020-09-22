# scraping_flask_docker
This code scrapes web to read pdfs using beautiful soup, flask and docker. Tabula-py is used to convert pdfs to json/csv


## Use Case developed as part of POC
Scrape documents on standards using open-source technologies as part of a data governance platform in cloud. The goal is to demonstrate the following 
•	Scraping web (used regex with beautiful soup) 
•	Usage of python
•	Storage of data in an open source db (used mongodb)
•	Usage of docker and docker-compose 

## Approach: 
Browsed the web to find a decent link on ISO standards. www.nsai.ie was found to be a fit case for scraping as it had semi-structured data (pdfs). There were 48 pdfs in this link https://www.nsai.ie/standards/search-buy-standards/new-irish-standards-2020/
Used the national standards authority of Ireland website to scrape CEN / CENELEC /ISO and SR standards 

## Technical issues
•	Used tabula-py to read pdfs. I like the stability across various formats of pdfs multiple pages support to json pandas data frames etc. It has an issue with docker which I will explain in the next point. Tried pdfx as well but these pdfs did not do the core work of scraping in linux for these documents. It was treating it as an ocr image but they were generated using tableau (worked in windows)  

•	Had issues with running tabula-py in container. It’s a java package with a python wrapper.  Hence a java process had to be invoked by a python process. Installing java and python runtime env did not work as the two process can’t talk. Found a solution to this problem by using an image in dockerhub which had python and java engine running as a single process (first line). It’s a workaround since it supports python 3.6.6. There are other options available using multi-stage builds  which needs to be explored

•	Bulk load of documents : python creates a subprocess calling mongoimport which did not work in docker environment. This was expected. There is a solution by using mongodbtools. Need to be explored later. As a workaround the code loads documents into mongodb one by one sequentially.
