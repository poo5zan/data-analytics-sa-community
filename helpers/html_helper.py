from bs4 import BeautifulSoup

from helpers.string_helper import StringHelper

class HtmlHelper():
    def __init__(self) -> None:
        self.string_helper = StringHelper()

    def is_valid_url(self, url: str):
        if self.string_helper.is_null_or_whitespace(url):
            return False
        
        url = url.strip()
        if not url.startswith("http"):
            return False
        
        return True

    def find_urls(self, html: str):
        self.string_helper.validate_null_or_empty(html, "html")
        soup = BeautifulSoup(html, "html.parser")
        anchor_tags = soup.findAll('a')
        return list({a.get("href") for a in anchor_tags if self.is_valid_url(a.get("href"))})
