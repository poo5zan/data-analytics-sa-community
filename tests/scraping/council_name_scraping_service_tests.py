import sys
import os
# insert current path to system path, so that we can import python file
sys.path.insert(1, os.getcwd())
import logging
import pandas as pd
from scraping.council_name_scraping_service import CouncilNameScrapingService
logger = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(message)s")

# The cu export file depends on your use case, whether you want all data or specific to council
# download the data from sacommunity.org/export
cu_export_df = pd.read_csv("./data/cu_export_all.csv")
#get the street addresses
# org_id_address_df = cu_export_df[["ID_19", "Street_Address_Line_1","Suburb","Organisati_Council","Organisati_Electorate_State_","Organisati_Electorate_Federal_"]]
council_name_scraping_service = CouncilNameScrapingService()
scraped_councils = council_name_scraping_service.scrape_council_names_based_on_cu_export_df(
    cu_export_df.head(5),
    "./data/cu_export_all_scraped_again.jsonl",
    n_jobs=1)
scraped_councils_df = pd.DataFrame(scraped_councils)
scraped_councils_df