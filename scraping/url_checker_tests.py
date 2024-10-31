import sys
import os
# insert current path to system path, so that we can import python file
sys.path.insert(1, os.getcwd())
from scraping.url_checker import UrlChecker
import pandas as pd

url_checker = UrlChecker()
url = "https://sacommunity.org/node/1123"
urls = [url, "https://sacommunity.org/org/194023"]
# resp = url_checker.check_urls_status(url)
resp = url_checker.check_urls_statuses(urls)
resp_df = pd.DataFrame(resp)
resp_df.to_csv("./data/url_checker.csv", index=False, escapechar="\\")