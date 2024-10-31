from http import HTTPStatus
from helpers.string_helper import StringHelper
from scraping.html_helper import HtmlHelper
from scraping.scraping_response import ScrapingResponse
from scraping.web_scraping import WebScraping


class UrlChecker():
    def __init__(self) -> None:
        self.string_helper = StringHelper()
        self.html_helper = HtmlHelper()
        self.web_scraping = WebScraping()

    def check_urls_status(self, base_url: str) -> list[ScrapingResponse]:
        self.string_helper.validate_null_or_empty(base_url, "base_url")
        scraping_response = self.web_scraping.scrape_url(base_url)
        responses = [scraping_response]
        if scraping_response.response_code != HTTPStatus.OK.value:
            return responses
        
        urls = self.html_helper.find_urls(scraping_response.page_content)
        for url in urls:
            response = self.web_scraping.scrape_url(url)
            responses.append(response)

        return responses
