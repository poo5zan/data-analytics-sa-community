from datetime import date
import pandas as pd
from dtos.date_range_dto import DateRangeDto
from google_analytics_module.dtos.google_analytics_filter_clause_dto import GoogleAnalyticsFilterClause
from google_analytics_module.dtos.google_analytics_request_config_dto import GoogleAnalyticsRequestConfig
from google_analytics_module.repositories.google_analytics_repository_v4 import GoogleAnalyticsRepositoryV4
from helpers.settings_helper import SettingsHelper

class GoogleAnalyticsService():
    def __init__(self, google_analytics_repository = None) -> None:
        if google_analytics_repository is None:
            self.google_analytics_repository = GoogleAnalyticsRepositoryV4()
        else:
            self.google_analytics_repository = google_analytics_repository
        self.settings_helper = SettingsHelper()
        self.property_id = self.settings_helper.get_google_analytics_view_id_v4()

    def get_data(self, dataset_id: str, start_date: date, end_date:date, dimensions, metrics):
        filter_clause = GoogleAnalyticsFilterClause()
        filter_clause.set_dataset_id(dataset_id)
        filter_clause.set_date_range(DateRangeDto(start_date=start_date, end_date=end_date))
        request_config=GoogleAnalyticsRequestConfig(dimensions, metrics)
        results = self.google_analytics_repository.get_data(property_id=self.property_id,
                                                            request_config=request_config,
                                                            filter_clause=filter_clause)
        
        for result in results:
            result['start_date'] = start_date
            result['end_date'] = end_date

        return results

    def get_sessions_by_gender(self):
        """get session data by gender"""
        return None
    
    def get_sessions_by_landing_page(self, dataset_id:str, start_date:date, end_date:date):
        """get session data with landing page"""
        dimensions = ["customEvent:DatasetID",  "landingPage"]
        metrics = ["sessions"]
        
        return self.get_data(dataset_id, start_date, end_date, dimensions, metrics)
    
    def get_sessions_by_landing_page_as_df(self, dataset_id:str, start_date:date, end_date:date):
        results = self.get_sessions_by_landing_page(dataset_id, start_date, end_date)
        return pd.DataFrame(results)

    def get_sessions_by_age(self):
        """get sessions data by age"""
        return None

    def get_page_views_and_sessions(self):
        """get page views"""
        return None
