"""
Web scraping
"""

import logging
import time
from datetime import datetime
from http import HTTPStatus
import requests
import backoff
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

# pylint: disable=import-error
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

# pylint: enable=import-error
from dtos.get_data_from_url_request_dto import GetDataFromUrlRequestDto
from helpers.log_helper import log_error
from helpers.string_helper import StringHelper
from helpers.html_helper import HtmlHelper
from scraping.scraping_response import ScrapingResponse

# pylint: disable=broad-exception-caught


class WebScraping:
    """web scraping methods"""

    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self.string_helper = StringHelper()
        self.html_helper = HtmlHelper()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
              (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

    def validate_url(self, url):
        """validate url"""
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
        """
        Finds the element in the html by xpath
        """
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
                        "Wait Timeout of %s seconds exceeded",
                        request_dto.timeout_in_seconds,
                    )
                    break

        return text

    def get_errors(self, status_code: int):
        """
        Get error name and description for http status code
        """
        if status_code != HTTPStatus.OK.value:
            http_status = HTTPStatus(status_code)
            return http_status.name, http_status.description

        return "", ""

    def scrape_url_using_requests(
        self, url: str, timeout_seconds=60
    ) -> ScrapingResponse:
        """Scrap url using requests library"""
        self.validate_url(url)
        try:
            self.logger.info("scrape_url: %s", url)
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=timeout_seconds)
            error_name, error_message = self.get_errors(response.status_code)
            return ScrapingResponse(
                url=url,
                response_code=response.status_code,
                page_content=response.text,
                error_name=error_name,
                error_message=error_message,
            )
        except Exception as ex:
            log_error(self.logger, "scrape_url", ex)
            return ScrapingResponse(
                url=url,
                response_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                page_content="",
                error_name="Exception",
                error_message=str(ex),
            )

    async def scrape_url_using_playwright_async(self, url: str) -> ScrapingResponse:
        """
        Retrieves html of a webpage  using Playwright async
        """
        self.validate_url(url)

        try:
            async with async_playwright() as playwright:
                async with await playwright.chromium.launch() as browser:
                    page = await browser.new_page()
                    response = await page.goto(url, wait_until="domcontentloaded")
                    error_name, error_message = self.get_errors(response.status)
                    return ScrapingResponse(
                        url=url,
                        response_code=response.status,
                        page_content=page.content(),
                        error_name=error_name,
                        error_message=error_message,
                    )
        except Exception as ex:
            log_error(self.logger, "scrape_url_using_playwright_async", ex)
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
                    page = browser.new_context(user_agent=self.user_agent).new_page()
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
            log_error(self.logger, "scrape_url_using_playwright", ex)
            return ScrapingResponse(
                url=url,
                response_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                page_content="",
                error_name="Exception",
                error_message=str(ex),
            )

    def scrape_url_using_selenium(self, url: str, time_to_wait=5):
        """scrape url using selenium and returns html"""
        self.validate_url(url)

        page_source = ""
        response_code = None
        error_message = ""
        error_name = ""
        try:
            with webdriver.Chrome(options=self.get_chrome_options(True)) as driver:
                driver.implicitly_wait(time_to_wait)
                driver.get(url)
                page_source = driver.page_source
                response_code = HTTPStatus.OK.value
        except WebDriverException as wde:
            log_error(self.logger, "scrape_url WebDriverException", wde)
            error_name = "WebDriverException"
            if "ERR_NAME_NOT_RESOLVED" in wde.msg:
                response_code = HTTPStatus.NOT_FOUND.value
                error_message = HTTPStatus.NOT_FOUND.description
            else:
                response_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
                error_message = str(wde)
        except Exception as ex:
            error_name = "Exception"
            response_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
            error_message = str(ex)
            log_error(self.logger, "scrape_url Exception", ex)

        return ScrapingResponse(
            url=url,
            response_code=response_code,
            page_content=page_source,
            error_name=error_name,
            error_message=error_message,
        )

    def scrape_url(self, url) -> ScrapingResponse:
        """
        Scrape URL. The order of preference is
        1. requests library
        2. playwright
        3. selenium
        """
        self.validate_url(url)
        scraper_options = [
            self.scrape_url_using_requests,
            self.scrape_url_using_playwright,
            self.scrape_url_using_selenium,
        ]
        for scraper in scraper_options:
            response = scraper(url)
            if response.response_code == HTTPStatus.OK.value:
                return response

        # return the last response
        return response

    async def scrape_url_async(self, url: str) -> ScrapingResponse:
        """
        Scrape url asynchronously
        """
        response = self.scrape_url_using_requests(url)
        if response.response_code != HTTPStatus.OK.value:
            response = await self.scrape_url_using_playwright_async(url)

        return response


# pylint: enable=broad-exception-caught
