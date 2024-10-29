'''
    Web scraping
'''
import re
import logging
import time
import pandas as pd
from datetime import datetime
from threading import Semaphore, Thread
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException
from selenium.common.exceptions import NoSuchElementException
from requests.utils import quote
import backoff
import requests
from bs4 import BeautifulSoup
from dtos.get_data_from_url_request_dto import GetDataFromUrlRequestDto
from helpers.file_helper import FileHelper
from helpers.settings_helper import SettingsHelper
from helpers.string_helper import StringHelper
from joblib import Parallel, delayed

class WebScraping():
    """web scraping"""
    def __init__(self) -> None:
        self.log = logging.getLogger()
        self.settings_helper = SettingsHelper()
        self.string_helper = StringHelper()
        self.file_helper = FileHelper()

    def extract_value_replacing_prefix(self, text_array, prefix):
        '''
        Extract only the value by removing the prefix
        '''
        values = [t for t in text_array if t.startswith(prefix)]
        if len(values) > 0:
            return values[0].replace(prefix, '').strip()

        return ''


    def get_chrome_options(self, is_headless):
        '''
        Get all the chrome options required for selenium
        '''
        options = webdriver.ChromeOptions()
        if is_headless:
            options.add_argument("--headless=new")

        return options


    def on_backoff_handler(self, details = None):
        '''
        Handler function when the backoff occurs. It simply logs the message
        '''
        print("on_backoff_handler details ", details)
        # self.log.debug(details)
        # web_scraping_logger.debug(
        #     f"Backing off {details.get('wait'):0.1f}
        #     seconds after {details.get('tries')}
        #     tries calling function {details.get('target')} with args {details.get('args')}
        #     and kwargs {details.get('kwargs')}")

    # backoff reference: https://pypi.org/project/backoff/
    # TODO, if the url is no longer valid, and the page redirects,
        # it will raise Timeout exception, because the element by xpath is not available
    # So, gracefully handle such scenario

    def find_element_by_xpath(self, driver, xpath):
        try:
            return driver.find_element(by=By.XPATH, value=xpath).text    
        except NoSuchElementException as ex:
            return ""

    @backoff.on_exception(backoff.expo,
                        SeleniumTimeoutException,
                        max_tries=3,
                        on_backoff=on_backoff_handler)
    def get_data_from_url(self, request_dto : GetDataFromUrlRequestDto):
        '''
        Get data from url. This is especially for javascript enabled websites.
        If we need data from static websites, simply use requests.get()
        '''
        if request_dto.url is None or request_dto.url == '':
            raise ValueError('url is required')
        start_time = datetime.now()
        default_wait_secs = 5

        options = self.get_chrome_options(request_dto.is_headless)
        with webdriver.Chrome(options=options) as driver:
            self.log.info('Fetching data from url %s', request_dto.url)
            driver.get(request_dto.url)
            text = ''
            while True:
                text = self.find_element_by_xpath(driver, request_dto.content_xpath)
                if not self.string_helper.is_null_or_whitespace(request_dto.no_content_xpath):
                    no_content = self.find_element_by_xpath(driver, request_dto.no_content_xpath)
                    
                    if not self.string_helper.is_null_or_whitespace(no_content):
                        return no_content

                # wait some seconds before next try
                sleep_timeout = default_wait_secs if \
                    request_dto.timeout_in_seconds > default_wait_secs \
                    else request_dto.timeout_in_seconds
                time.sleep(sleep_timeout)
                if text not in request_dto.to_exclude:
                    break

                # if we couldnot find data in timeout,
                # then simply ignore it, else there is possibility of infinite loop
                difference_time = datetime.now() - start_time
                if difference_time.total_seconds() > request_dto.timeout_in_seconds:
                    self.log.info(f'Wait Timeout of {request_dto.timeout_in_seconds} seconds exceeded')
                    break

        return text

    # Manual retry logic. I ended up using backoff library instead. Kept here just for reference
    # def get_data_from_url_with_retry(url: str, is_headless:
    #                       bool, to_exclude: list,
    #                       timeout_in_seconds: int,
    #                       xpath: str):
    #     MAX_RETRY_COUNT = 3

    #     for i in range(MAX_RETRY_COUNT):
    #         try:
    #             return get_data_from_url(url, is_headless, to_exclude, timeout_in_seconds, xpath)
    #         except SeleniumTimeoutException as te:
    #             print('Timeout occurred ', str(te))
    #             # TODO, wait for some time and try again
    #             print('Wait 3 seconds before retry. Retry count ', i)
    #             time.sleep(3)
    #         except Exception as ex:
    #             print('General Exception ', str(ex))
    #             print('Exception type ', type(ex))
    #             return None


    def find_council_by_address(self, address:str, timeout_in_seconds=600, is_headless=True):
        '''
        Finds council by address
        address: address where organization is located
        timeout_in_seconds: timeout in seconds until which the program will 
        wait before returning None
        is_headless: if False, a chrome browser will popup, 
        else the operation will be done in background
        '''
        if address is None or address == '':
            raise ValueError('address is required')

        address_encoded = quote(address)
        app_id = 'db6cce7b773746b4a1d4ce544435f9da'
        base_url = 'https://lga-sa.maps.arcgis.com/apps/instant/lookup/index.html'
        url = f'{base_url}?appid={app_id}&find={address_encoded}'
        self.log.info('Fetching council for %s', address)
        to_exclude = ['Results:1', '', 'Loading...']
        text = self.get_data_from_url(GetDataFromUrlRequestDto(
            url, is_headless, to_exclude,
            timeout_in_seconds, '//*[@id="resultsPanel"]',
            '//*[@id="noResults"]/calcite-tip/div/div'))
        
        council_name = ""
        electoral_ward = ""
        if text != '':
            text_array = text.splitlines()

            council_name = self.extract_value_replacing_prefix(text_array, "Council Name")
            electoral_ward = self.extract_value_replacing_prefix(
                text_array, "Electoral Ward")

        return {'address': address, 'council_name': council_name, 'electoral_ward': electoral_ward, 'text': text}


    def find_councils_by_addresses(self, addresses: list, is_headless=True, timeout_in_seconds=600):
        '''
        Find councils by addresses in parallel
        Example: 
        # with less timeout, to check test timeout feature. 
        # Without timeout, there is possibility of infinite loop
        # print(find_council_by_address("130 L'Estrange Street, Glenunga", 2))

        # with default timeout, this generally gives data
        # print('council details ', find_council_by_address("130 L'Estrange Street, Glenunga"))
        '''
        # maximum number of concurrent requests at a time
        semaphore = Semaphore(self.settings_helper.get_web_scraping_maximum_concurrent_requests())

        threads = []

        def find_council(address, all_councils):
            with semaphore:
                try:
                    council = self.find_council_by_address(
                        address, timeout_in_seconds, is_headless)
                    all_councils.append(council)
                except Exception as ex:
                    # simply log the exception, don't raise it further
                    self.log.error(ex, exc_info=True)
                    raise ex

        all_councils = []
        for address in addresses:
            thread = Thread(target=find_council, args=(address, all_councils))
            threads.append(thread)
            thread.start()

        # print('Wait for all threads to complete ')
        for thread in threads:
            thread.join()

        return all_councils


    def find_address_from_sacommunity_website(self,
                                              url: str,
                                              is_headless=True,
                                              timeout_in_seconds=600):
        '''
        Find address from sa community website
        '''
        xpath = '//*[@id="content-area"]/div/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[2]'
        return self.get_data_from_url(GetDataFromUrlRequestDto(
            url,
            is_headless,
            [],
            timeout_in_seconds,
            xpath,
            ""))

    # getting council name from sacommunity website based on xpath is not achievable,
    # because the xpath differs based on the contents
    # As the time of this writing, this urls
    # https://sacommunity.org/org/208832-Burnside_Youth_Club and
    # https://sacommunity.org/org/196519-Sturt_Badminton_Club_Inc. has xpath of
    # //*[@id="content-area"]/div/div[4]
    # //*[@id="content-area"]/div/div[5]
    # So it's okay for now to get the council name based on regular expression,
    # thus used beautiful soup


    def get_council_from_sacommunity_website(self, url):
        '''
        Get council from sacommunity website
        '''
        timeout = self.settings_helper.get_web_scraping_timeout_in_seconds()
        url_response = requests.get(url,
                                    timeout=timeout)
        soup = BeautifulSoup(url_response.content)
        council_identifier = "Council:"
        council_text = soup.find("div", string=re.compile(council_identifier))
        # print('council text ', council_text)
        council_name = ''
        if council_text is not None:
            council_text = str(council_text)
            start_index = council_text.index(council_identifier)
            council_name = council_text[start_index:].replace(
                council_identifier, '').replace("</div>", "").strip()

        return council_name


    # test function, useful while debugging
    # url = 'https://sacommunity.org/org/208832-Burnside_Youth_Club'
    # find_address_in_sacommunity(url, False)


    def find_addresses_from_sacommunity_website(self,
                                                urls: list,
                                                is_headless=True,
                                                timeout_in_seconds=600):
        '''
        Retrieves addresses from the sa-community website for given lists of urls in parallel
        '''
        semaphore = Semaphore(self.settings_helper.get_web_scraping_maximum_concurrent_requests())

        threads = []

        def find_addr(url, all_address):
            with semaphore:
                try:
                    addr = self.find_address_from_sacommunity_website(
                        url, is_headless, timeout_in_seconds)
                    council = self.get_council_from_sacommunity_website(url)
                    all_address.append(
                        {'url': url, 'address': addr, 'council_in_sacommunity_website': council})
                except Exception as ex:
                    self.log.error(ex, exc_info=True)
                    raise ex

        all_address = []
        for url in urls:
            thread = Thread(target=find_addr, args=(url, all_address))
            threads.append(thread)
            thread.start()

        # print('Wait for all threads to complete ')
        for thread in threads:
            thread.join()

        return all_address
    
    def scrape_council_name_based_on_cu_export_df(self,
                                                  row_counter,
                                                  total,
                                                  row,
                                                  output_records,
                                                  output_file_path):
        org_id = row["ID_19"]
        address = str(row["Street_Address_Line_1"]) + " " + str(row["Suburb"])
        council = row["Organisati_Council"]
        electorate_state = row["Organisati_Electorate_State_"]
        electorate_federal = row["Organisati_Electorate_Federal_"]

        existing_record = [o for o in output_records if o.get("org_id") == org_id]
        if len(existing_record) > 0:
            self.log.info(f"Record exists: Skipping council for org {org_id}, address {address}. Progress {row_counter + 1} of {total}")
            return None

        print(f"Scraping council for org {org_id}, address {address}. Progress {row_counter + 1} of {total}")

        error_message = ""
        has_error = False
        council_scraped = ""
        electorate_state_scraped = ""
        scraped_text = ""
        if self.string_helper.is_null_or_whitespace(address):
            error_message = "address is null or empty"
        else:
            address_cleaned = address.strip()
            try:
                council_by_address = self.find_council_by_address(address_cleaned)
                council_scraped = council_by_address.get("council_name", "")
                electorate_state_scraped = council_by_address.get("electoral_ward", "")
                scraped_text = council_by_address.get("text", "")
            except Exception as ex:
                has_error = True
                error_message = str(ex)
                self.log.error(ex)

        scraped_council = {
            "org_id": org_id,
            "address": address,
            "council": council,
            "electorate_state": electorate_state,
            "electorate_federal": electorate_federal,
            "error_message": error_message,
            "has_error": has_error,
            "council_scraped": council_scraped,
            "electorate_state_scraped": electorate_state_scraped,
            "is_council_correct": council == council_scraped,
            "is_electorate_state_correct": electorate_state == electorate_state_scraped,
            "scraped_text": scraped_text
        }

        if not self.string_helper.is_null_or_whitespace(output_file_path):
            self.file_helper.write_jsonlines(output_file_path, scraped_council)

    def scrape_council_names_based_on_cu_export_df(self,
                                                   cu_export_df : pd.DataFrame,
                                                   output_file_path: str = "",
                                                   n_jobs=3):
        total = len(cu_export_df)
        output_records = []
        if not self.string_helper.is_null_or_whitespace(output_file_path) and self.file_helper.does_file_exist(output_file_path):
            self.log.info("Reading output records")
            output_records = self.file_helper.read_jsonlines_all(output_file_path)
            self.log.info("Completed reading output records")
       
        scraped_councils = Parallel(n_jobs=n_jobs)(delayed(self.scrape_council_name_based_on_cu_export_df)(row_counter,
                                                  total,
                                                  row,
                                                  output_records,
                                                  output_file_path) for row_counter,row in cu_export_df.iterrows())

        return [s for s in scraped_councils if s is not None]
