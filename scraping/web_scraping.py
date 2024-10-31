"""
Web scraping
"""

import logging
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException
from selenium.common.exceptions import NoSuchElementException
import backoff
import requests
from dtos.get_data_from_url_request_dto import GetDataFromUrlRequestDto
from helpers.file_helper import FileHelper
from helpers.settings_helper import SettingsHelper
from helpers.string_helper import StringHelper
from http import HTTPStatus
from playwright.sync_api import sync_playwright
from scraping.html_helper import HtmlHelper
from scraping.scraping_response import ScrapingResponse


class WebScraping:
    """web scraping methods"""

    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self.settings_helper = SettingsHelper()
        self.string_helper = StringHelper()
        self.file_helper = FileHelper()
        self.html_helper = HtmlHelper()
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

    def validate_url(self, url):
        if self.string_helper.is_null_or_whitespace(url):
            raise ValueError("url is required")

        if not self.html_helper.is_valid_url(url):
            raise ValueError(f"Invalid url {url}")

    def get_chrome_options(self, is_headless):
        """
        Get all the chrome options required for selenium
        """
        options = webdriver.ChromeOptions()
        if is_headless:
            options.add_argument("--headless=new")

        return options

    def find_element_by_xpath(self, driver, xpath):
        try:
            return driver.find_element(by=By.XPATH, value=xpath).text
        except NoSuchElementException as ex:
            self.logger.warning("find_element_by_xpath %s", ex)
            return ""

    @backoff.on_exception(backoff.expo, SeleniumTimeoutException, max_tries=3)
    def get_data_from_url(self, request_dto: GetDataFromUrlRequestDto):
        """
        Get data from url. This is especially for javascript enabled websites.
        If we need data from static websites, simply use requests.get()
        """
        self.validate_url(request_dto.url)
        start_time = datetime.now()
        default_wait_secs = 5

        options = self.get_chrome_options(request_dto.is_headless)
        with webdriver.Chrome(options=options) as driver:
            self.logger.info("Fetching data from url %s", request_dto.url)
            driver.get(request_dto.url)
            text = ""
            while True:
                text = self.find_element_by_xpath(driver, request_dto.content_xpath)
                if not self.string_helper.is_null_or_whitespace(
                    request_dto.no_content_xpath
                ):
                    no_content = self.find_element_by_xpath(
                        driver, request_dto.no_content_xpath
                    )

                    if not self.string_helper.is_null_or_whitespace(no_content):
                        return no_content

                # wait some seconds before next try
                sleep_timeout = (
                    default_wait_secs
                    if request_dto.timeout_in_seconds > default_wait_secs
                    else request_dto.timeout_in_seconds
                )
                time.sleep(sleep_timeout)
                if text not in request_dto.to_exclude:
                    break

                # if we couldnot find data in timeout,
                # then simply ignore it, else there is possibility of infinite loop
                difference_time = datetime.now() - start_time
                if difference_time.total_seconds() > request_dto.timeout_in_seconds:
                    self.logger.info(
                        f"Wait Timeout of {request_dto.timeout_in_seconds} seconds exceeded"
                    )
                    break

        return text

    def get_errors(self, status_code: int):
        if status_code != HTTPStatus.OK.value:
            http_status = HTTPStatus(status_code)
            return http_status.name, http_status.description
        else:
            return "", ""

    def scrape_url_using_requests(self, url: str) -> ScrapingResponse:
        self.validate_url(url)
        try:
            self.logger.info(f"scrape_url: {url}")
            response = requests.get(url)
            error_name, error_message = self.get_errors(response.status_code)
            return ScrapingResponse(
                url=url,
                response_code=response.status_code,
                page_content=response.text,
                error_name=error_name,
                error_message=error_message,
            )
        except Exception as ex:
            self.logger.error("scrape_url %s", ex)
            return ScrapingResponse(
                url=url,
                response_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                page_content="",
                error_name="Exception",
                error_message=str(ex),
            )

    def scrape_url_using_playwright(self, url: str) -> ScrapingResponse:
        """
        Retrieves html of a webpage using Playwright
        """
        self.validate_url(url)

        try:
            with sync_playwright() as playwright:
                with playwright.chromium.launch() as browser:
                    page = browser.new_context(user_agent=self.USER_AGENT).new_page()
                    response = page.goto(url, wait_until="domcontentloaded")
                    error_name, error_message = self.get_errors(response.status)
                    return ScrapingResponse(
                        url=url,
                        response_code=response.status,
                        page_content=page.content(),
                        error_name=error_name,
                        error_message=error_message,
                    )
        except Exception as ex:
            self.logger.error("scrape_url_using_playwright", ex)
            return ScrapingResponse(
                url=url,
                response_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                page_content="",
                error_name="Exception",
                error_message=str(ex),
            )

    def scrape_url(self, url) -> ScrapingResponse:
        response = self.scrape_url_using_requests(url)
        if response.response_code != HTTPStatus.OK.value:
            response = self.scrape_url_using_playwright(url)

        return response
