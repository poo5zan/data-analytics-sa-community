import sys
import os
# insert current path to system path, so that we can import python file
sys.path.insert(1, os.getcwd())
from scraping.url_checker import UrlChecker


url_checker = UrlChecker()
resp = url_checker.check_urls_status("https://sacommunity.org/node/1123")
p = 0