import re
import logging
import pandas as pd
from requests.utils import quote
import requests
from bs4 import BeautifulSoup
from dtos.get_data_from_url_request_dto import GetDataFromUrlRequestDto
from helpers.file_helper import FileHelper
from helpers.settings_helper import SettingsHelper
from helpers.string_helper import StringHelper
from joblib import Parallel, delayed
from scraping.html_helper import HtmlHelper
from scraping.find_council_by_address_response import FindCouncilByAddressResponse
from threading import Semaphore, Thread

from scraping.web_scraping import WebScraping


class CouncilNameScrapingService:
    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self.settings_helper = SettingsHelper()
        self.string_helper = StringHelper()
        self.file_helper = FileHelper()
        self.html_helper = HtmlHelper()
        self.web_scraping = WebScraping()

    def extract_value_replacing_prefix(self, text_array, prefix):
        """
        Extract only the value by removing the prefix
        """
        values = [t for t in text_array if t.startswith(prefix)]
        if len(values) > 0:
            return values[0].replace(prefix, "").strip()

        return ""

    def find_council_by_address(
        self, address: str, timeout_in_seconds=600, is_headless=True
    ) -> FindCouncilByAddressResponse:
        """
        Finds council by address
        address: address where organization is located
        timeout_in_seconds: timeout in seconds until which the program will
        wait before returning None
        is_headless: if False, a chrome browser will popup,
        else the operation will be done in background
        """
        if address is None or address == "":
            raise ValueError("address is required")

        error_message = ""
        has_error = False
        try:
            address_encoded = quote(address)
            app_id = "db6cce7b773746b4a1d4ce544435f9da"
            base_url = "https://lga-sa.maps.arcgis.com/apps/instant/lookup/index.html"
            url = f"{base_url}?appid={app_id}&find={address_encoded}"
            self.logger.info("Fetching council for %s", address)
            to_exclude = ["Results:1", "", "Loading..."]
            text = self.web_scraping.get_data_from_url(
                GetDataFromUrlRequestDto(
                    url,
                    is_headless,
                    to_exclude,
                    timeout_in_seconds,
                    '//*[@id="resultsPanel"]',
                    '//*[@id="noResults"]/calcite-tip/div/div',
                )
            )

            council_name = ""
            electoral_ward = ""
            if text != "":
                text_array = text.splitlines()

                council_name = self.extract_value_replacing_prefix(
                    text_array, "Council Name"
                )
                electoral_ward = self.extract_value_replacing_prefix(
                    text_array, "Electoral Ward"
                )

        except Exception as ex:
            has_error = True
            error_message = str(ex)
            self.logger.error("find_council_by_address", ex)

        return FindCouncilByAddressResponse(
            address, council_name, electoral_ward, text, has_error, error_message
        )

    def find_councils_by_addresses(
        self, addresses: list, is_headless=True, timeout_in_seconds=600
    ):
        """
        Find councils by addresses in parallel
        Example:
        # with less timeout, to check test timeout feature.
        # Without timeout, there is possibility of infinite loop
        # print(find_council_by_address("130 L'Estrange Street, Glenunga", 2))

        # with default timeout, this generally gives data
        # print('council details ', find_council_by_address("130 L'Estrange Street, Glenunga"))
        """
        # maximum number of concurrent requests at a time
        semaphore = Semaphore(
            self.settings_helper.get_web_scraping_maximum_concurrent_requests()
        )

        threads = []

        def find_council(address, all_councils):
            with semaphore:
                try:
                    council = self.find_council_by_address(
                        address, timeout_in_seconds, is_headless
                    )
                    all_councils.append(council)
                except Exception as ex:
                    # simply log the exception, don't raise it further
                    self.logger.error(ex, exc_info=True)
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

    def find_address_from_sacommunity_website(
        self, url: str, is_headless=True, timeout_in_seconds=600
    ):
        """
        Find address from sa community website
        """
        xpath = (
            '//*[@id="content-area"]/div/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[2]'
        )
        return self.web_scraping.get_data_from_url(
            GetDataFromUrlRequestDto(
                url, is_headless, [], timeout_in_seconds, xpath, ""
            )
        )

    # getting council name from sacommunity website based on xpath is not achievable,
    # because the xpath differs based on the contents
    # As the time of this writing, this urls
    # https://sacommunity.org/org/208832-Burnside_Youth_Club and
    # https://sacommunity.org/org/196519-Sturt_Badminton_Club_Inc. has xpath of
    # //*[@id="content-area"]/div/div[4]
    # //*[@id="content-area"]/div/div[5]
    # So it's okay for now to get the council name based on regular expression,
    # thus used beautiful soup
    # test function, useful while debugging
    # url = 'https://sacommunity.org/org/208832-Burnside_Youth_Club'
    # find_address_in_sacommunity(url, False)
    def get_council_from_sacommunity_website(self, url):
        """
        Get council from sacommunity website
        """
        timeout = self.settings_helper.get_web_scraping_timeout_in_seconds()
        url_response = requests.get(url, timeout=timeout)
        soup = BeautifulSoup(url_response.content)
        council_identifier = "Council:"
        council_text = soup.find("div", string=re.compile(council_identifier))
        # print('council text ', council_text)
        council_name = ""
        if council_text is not None:
            council_text = str(council_text)
            start_index = council_text.index(council_identifier)
            council_name = (
                council_text[start_index:]
                .replace(council_identifier, "")
                .replace("</div>", "")
                .strip()
            )

        return council_name

    def find_addresses_from_sacommunity_website(
        self, urls: list, is_headless=True, timeout_in_seconds=600
    ):
        """
        Retrieves addresses from the sa-community website for given lists of urls in parallel
        """
        semaphore = Semaphore(
            self.settings_helper.get_web_scraping_maximum_concurrent_requests()
        )

        threads = []

        def find_addr(url, all_address):
            with semaphore:
                try:
                    addr = self.find_address_from_sacommunity_website(
                        url, is_headless, timeout_in_seconds
                    )
                    council = self.get_council_from_sacommunity_website(url)
                    all_address.append(
                        {
                            "url": url,
                            "address": addr,
                            "council_in_sacommunity_website": council,
                        }
                    )
                except Exception as ex:
                    self.logger.error(ex, exc_info=True)
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

    def scrape_council_name_based_on_cu_export_df(
        self, row_counter, total, row, output_records, output_file_path
    ):
        org_id = row["ID_19"]
        address = str(row["Street_Address_Line_1"]) + " " + str(row["Suburb"])
        council = row["Organisati_Council"]
        electorate_state = row["Organisati_Electorate_State_"]
        electorate_federal = row["Organisati_Electorate_Federal_"]

        existing_record = org_id in output_records
        if existing_record:
            print(
                f"Record exists: Skipping council for org {org_id}, address {address}. Progress {row_counter + 1} of {total}"
            )
            return None

        print(
            f"Scraping council for org {org_id}, address {address}. Progress {row_counter + 1} of {total}"
        )

        error_message = ""
        if self.string_helper.is_null_or_whitespace(address):
            error_message = "address is null or empty"
        else:
            address_cleaned = address.strip()
            council_by_address_response = self.find_council_by_address(address_cleaned)
            error_message = council_by_address_response.error_message

        scraped_council = {
            "org_id": org_id,
            "address": address,
            "council": council,
            "electorate_state": electorate_state,
            "electorate_federal": electorate_federal,
            "error_message": error_message,
            "has_error": council_by_address_response.has_error,
            "council_scraped": council_by_address_response.council_name,
            "electorate_state_scraped": council_by_address_response.electoral_ward,
            "is_council_correct": council == council_by_address_response.council_name,
            "scraped_text": council_by_address_response.text,
        }

        if not self.string_helper.is_null_or_whitespace(output_file_path):
            self.file_helper.write_jsonlines(output_file_path, scraped_council)

    def get_output_records_organisations(self, output_file_path):
        output_records = self.file_helper.read_jsonlines_all(output_file_path)
        return [o.get("org_id") for o in output_records]

    def scrape_council_names_based_on_cu_export_df(
        self, cu_export_df: pd.DataFrame, output_file_path: str = "", n_jobs=3
    ):
        total = len(cu_export_df)
        output_records = []
        if not self.string_helper.is_null_or_whitespace(
            output_file_path
        ) and self.file_helper.does_file_exist(output_file_path):
            self.logger.info("Reading output records")
            output_records = self.get_output_records_organisations(output_file_path)
            self.logger.info("Completed reading output records")

        scraped_councils = Parallel(n_jobs=n_jobs)(
            delayed(self.scrape_council_name_based_on_cu_export_df)(
                row_counter, total, row, output_records, output_file_path
            )
            for row_counter, row in cu_export_df.iterrows()
        )

        return [s for s in scraped_councils if s is not None]

    def do_council_scraping_output_require_retry(self, output):
        # No Results found
        if output.get("scraped_text").startswith("No results found."):
            return True

        # Exceptions
        if output.get(
            "has_error", False
        ) and not self.string_helper.is_null_or_whitespace(output.get("address")):
            return True

        return False

    def retry_failed_scraping_of_council_name(
        self,
        output_record,
        new_output_file_path: str,
        existing_records,
        row_counter,
        total,
    ):
        existing_record = output_record.get("org_id") in existing_records
        if existing_record:
            return

        if self.do_council_scraping_output_require_retry(output_record):
            print(
                f'Scraping council for org {output_record.get("org_id")}, address {output_record.get("address")}. Progress {row_counter + 1} of {total}'
            )
            response = self.find_council_by_address(output_record.get("address"))
            output_record["error_message"] = response.error_message
            output_record["has_error"] = response.has_error
            output_record["council_scraped"] = response.council_name
            output_record["electorate_state_scraped"] = response.electoral_ward
            output_record["is_council_correct"] = (
                output_record["council"] == response.council_name
            )
            output_record["scraped_text"] = response.text

        self.file_helper.write_jsonlines(new_output_file_path, output_record)

    def retry_failed_scraping_of_council_names(
        self, output_file_path: str, new_output_file_path: str, n_jobs=3
    ):
        output_records = self.file_helper.read_jsonlines_all(output_file_path)

        total = len(output_records)
        existing_records = []
        if self.file_helper.does_file_exist(new_output_file_path):
            existing_records = self.get_output_records_organisations(
                new_output_file_path
            )
        Parallel(n_jobs=n_jobs)(
            delayed(self.retry_failed_scraping_of_council_name)(
                output_record,
                new_output_file_path,
                existing_records,
                row_counter,
                total,
            )
            for row_counter, output_record in enumerate(output_records)
        )
