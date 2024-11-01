"""
HTML helper methods
"""

from bs4 import BeautifulSoup

from helpers.string_helper import StringHelper


class HtmlHelper:
    """
    HTML Helper
    """

    def __init__(self) -> None:
        self.string_helper = StringHelper()

    def is_valid_url(self, url: str):
        """
        Check if url is valid
        """
        if self.string_helper.is_null_or_whitespace(url):
            return False

        url = url.strip()
        if not url.startswith("http"):
            return False

        return True

    def find_urls(self, html: str):
        """
        Find urls from the html
        """
        self.string_helper.validate_null_or_empty(html, "html")
        soup = BeautifulSoup(html, "html.parser")
        anchor_tags = soup.findAll("a")
        return list(
            {a.get("href") for a in anchor_tags if self.is_valid_url(a.get("href"))}
        )
