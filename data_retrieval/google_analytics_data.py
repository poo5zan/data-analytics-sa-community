"""Retrieve and save google analytics data"""
import sys
import os

sys.path.insert(1, os.getcwd())
print(os.getcwd())

# pylint: disable=wrong-import-position
import uuid
import logging
import pandas as pd
from data_retrieval.google_analytics_api_retrieval import GoogleAnalyticsFilterClause,\
    GoogleAnalyticsApiRetrieval, GoogleAuthenticationMethod, PageDto
from helpers.file_helper import save_run_file_to_csv
from helpers.settings_helper import get_google_analytics_view_id_from_settings,\
    get_file_storage_root_folder_from_settings
from helpers.enums import DataModule
# pylint: enable=wrong-import-position

class GoogleAnalyticsData():
    """google analytics data"""
    def __init__(self, oauth_credentials_filepath: str, oauth_token_filepath: str) -> None:
        self.ga_data_log = logging.getLogger(__name__)
        self.oauth_credentials_filepath = oauth_credentials_filepath
        self.oauth_token_filepath = oauth_token_filepath

    def group_data(self, dataframe: pd.DataFrame,
                   select_columns: list[str],
                   grp_columns: list[str]) -> pd.DataFrame:
        """group data"""
        df_s = dataframe[select_columns]
        df_grp = df_s.groupby(by=grp_columns, as_index=False).sum()
        return df_grp

    def filter_data_by_dataset_id(self, dataframe: pd.DataFrame, data_set_id: str):
        """filter data by dataset id"""
        return dataframe[dataframe['dataset_id'] == data_set_id]

    def save_data(self, filter_clause: GoogleAnalyticsFilterClause):
        """save data: device category, source/medium, landing page, age, gender"""
        root_dir = get_file_storage_root_folder_from_settings()
        self.ga_data_log.info('root_dir to store data is %s', root_dir)
        run_id = str(uuid.uuid4())
        self.ga_data_log.info('Run id %s', run_id)

        google_analytics_api = GoogleAnalyticsApiRetrieval(
            google_authentication_method=GoogleAuthenticationMethod.OAUTH,
            oauth_credentials_filepath=self.oauth_credentials_filepath,
            oauth_token_filepath=self.oauth_token_filepath,
            view_id=get_google_analytics_view_id_from_settings())

        # 1, 2, 3. Data for device category, source medium and landing page
        self.ga_data_log.info('Getting data for landing page')
        data_df = google_analytics_api.get_sessions_by_landing_page(filter_clause)

        # 1 device category
        device_category_df = self.group_data(data_df, ["dataset_id", "device_category","sessions"],
                                             ["dataset_id", "device_category"])
        save_run_file_to_csv(device_category_df, run_id, DataModule.DEVICE_CATEGORY)

        # 2 source medium
        source_medium_df = self.group_data(data_df, ["dataset_id", "source_medium","sessions"],
                                           ["dataset_id", "source_medium"])
        save_run_file_to_csv(source_medium_df, run_id, DataModule.SOURCE_MEDIUM)

        # 3 landing page
        landing_page_df = self.group_data(data_df, ["dataset_id", "landing_page","sessions"],
                                          ["dataset_id", "landing_page"])
        save_run_file_to_csv(landing_page_df, run_id, DataModule.LANDING_PAGE)

        # 4 Age
        self.ga_data_log.info("Getting age data")
        filter_clause.set_page_dto(PageDto(10000, None))
        age_df = google_analytics_api.get_sessions_by_age(filter_clause)
        save_run_file_to_csv(age_df, run_id, DataModule.AGE)

        # 5 gender
        self.ga_data_log.info("Getting gender data")
        filter_clause.set_page_dto(PageDto(10000, None))
        gender_df = google_analytics_api.get_sessions_by_gender(filter_clause)
        save_run_file_to_csv(gender_df, run_id, DataModule.GENDER)

        return run_id