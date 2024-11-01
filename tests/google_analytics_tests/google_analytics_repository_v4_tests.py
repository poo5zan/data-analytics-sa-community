import sys
import os
from datetime import date
# insert current path to system path, so that we can import python file
sys.path.insert(1, os.getcwd())

from dtos.date_range_dto import DateRangeDto
from dtos.page_dto import PageDto
from google_analytics_module.dtos.google_analytics_filter_clause_dto import GoogleAnalyticsFilterClause
from google_analytics_module.dtos.google_analytics_request_config_dto import GoogleAnalyticsRequestConfig
from google_analytics_module.repositories.google_analytics_repository_v4 import GoogleAnalyticsRepositoryV4
from helpers.settings_helper import SettingsHelper

# council_name = "burnside"
start_date = date(2024,4,1)
end_date = date(2024,5,1)
settings_helper = SettingsHelper()
property_id = settings_helper.get_google_analytics_view_id_v4()

google_analytics_repository = GoogleAnalyticsRepositoryV4()
filter_clause = GoogleAnalyticsFilterClause()
# filter_clause.set_council_name(council_name)
filter_clause.set_dataset_id("0QK91R12")
filter_clause.set_date_range(DateRangeDto(start_date=start_date, end_date=end_date))
page_size = SettingsHelper().get_google_analytics_page_size()
filter_clause.set_page_dto(PageDto(page_size, None))

# Landing Page
dimensions = ["customEvent:DatasetID",  "landingPage"]
metrics = ["sessions"]
request_config=GoogleAnalyticsRequestConfig(dimensions, metrics)
response = google_analytics_repository.get_data(property_id=property_id,
                                                      request_config=request_config,
                                                      filter_clause=filter_clause)

p = 0