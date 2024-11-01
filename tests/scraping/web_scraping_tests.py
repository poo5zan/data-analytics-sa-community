import sys
import os
# insert current path to system path, so that we can import python file
sys.path.insert(1, os.getcwd())

from scraping.web_scraping import WebScraping

web_scraping = WebScraping()
URL = "http://abr.business.gov.au/SearchByAbn.aspx?SearchText=22048756072"
resp = web_scraping.scrape_url(URL)