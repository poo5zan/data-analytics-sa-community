"""
URL Checker
"""

from http import HTTPStatus
import pandas as pd
from joblib import Parallel, delayed
from helpers.settings_helper import SettingsHelper
from helpers.string_helper import StringHelper
from helpers.html_helper import HtmlHelper
from scraping.scraping_response import ScrapingResponse
from scraping.web_scraping import WebScraping


class UrlChecker:
    """
    Url Checker. checks if the url is accessible or the is link broken
    """

    def __init__(self) -> None:
        self.string_helper = StringHelper()
        self.html_helper = HtmlHelper()
        self.web_scraping = WebScraping()
        self.settings_helper = SettingsHelper()

    def check_urls_status(self, base_url: str) -> list[ScrapingResponse]:
        """
        Check url statuses for a single base url
        """
        self.string_helper.validate_null_or_empty(base_url, "base_url")
        scraping_response = self.web_scraping.scrape_url(base_url)
        scraping_response_dict = scraping_response.__dict__
        scraping_response_dict["base_url"] = base_url
        responses = [scraping_response_dict]
        if scraping_response.response_code != HTTPStatus.OK.value:
            return responses

        urls = self.html_helper.find_urls(scraping_response.page_content)
        for url in urls:
            response = self.web_scraping.scrape_url(url)
            response_dict = response.__dict__
            response_dict["base_url"] = base_url
            responses.append(response_dict)

        return responses

    def check_urls_statuses(
        self, base_urls: list[str], n_jobs=3
    ) -> list[ScrapingResponse]:
        """
        Check url statuses for multiple urls
        """
        responses = Parallel(n_jobs=n_jobs)(
            delayed(self.check_urls_status)(base_url) for base_url in base_urls
        )
        responses_flat = []
        for response_list in responses:
            responses_flat.extend(response_list)

        return responses_flat

    def check_urls_for_cu_export_data(self, cu_export_file_path: str):
        """
        Check url response statuses with cu_export file path as input
        """
        cu_export_df = pd.read_csv(cu_export_file_path)
        sa_community_url = self.settings_helper.get_sacommunity_url()
        cu_export_df["url"] = f"{sa_community_url}/org/" + cu_export_df["ID_19"].apply(
            str
        )
        urls = cu_export_df["url"].tolist()
        return self.check_urls_statuses(urls)
