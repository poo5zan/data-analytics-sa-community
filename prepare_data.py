# """prepare data"""
# import pandas as pd

# from dtos.settings_dto import SettingsDto
# from helpers.cu_dataset_reader import CuDatasetReader
# from helpers.string_helper import StringHelper
# from helpers.enums import DataModule
# from helpers.file_helper import FileHelper
# from google_analytics_module.google_analytics_data import GoogleAnalyticsData
# from data_transform.clean_landing_page import CleanLandingPage


# def get_cu_dataset_reader_instance(file_path):
#     """create instance of CuDatasetReader"""
#     if StringHelper().is_null_or_whitespace(file_path):
#         return CuDatasetReader()

#     return CuDatasetReader(file_path)


# def prepare_sessions_data(settings_dto: SettingsDto,
#                           filter_clause: GoogleAnalyticsFilterClause):
#     """prepare sessions data"""
#     cu_dataset_reader = get_cu_dataset_reader_instance(
#         settings_dto.cu_dataset_file_path)

#     dataset = cu_dataset_reader.search_dataset_id_from_council_name(
#         filter_clause.council_name)
#     if dataset is None or len(dataset) == 1:
#         raise ValueError('Council not found for search string: ',
#                          filter_clause.council_name)
#     dataset_id = ''
#     council_name = ''
#     if dataset is None:
#         print('dataset not found for ', filter_clause.council_name)
#         return None

#     dataset_id = dataset['dataset_id']
#     council_name = dataset['council_name']

#     print('Council Name ', council_name)
#     print('dataset id ', dataset_id)

#     filter_clause.set_dataset_id(dataset_id)

#     ga_data = GoogleAnalyticsData(settings_dto.client_secret_file_path,
#                                   settings_dto.token_file_path)

#     run_id = ga_data.save_data(filter_clause=filter_clause)
#     print('run id ', run_id)

#     file_helper = FileHelper()
#     landing_page_df = file_helper.read_run_file(
#         run_id, DataModule.LANDING_PAGE)
#     cu_export_df = pd.read_csv(settings_dto.sa_community_export_file_path)

#     clean_landing_page = CleanLandingPage()
#     processed_data_df = clean_landing_page.process_data(
#         landing_page_df, cu_export_df)

#     file_helper = FileHelper()
#     # these records are problematic, they are found in google analytics,
#     # but not in sacommunity council based export
#     # Check these records manually, why it is not available in sacommunity db
#     # One posible reason is that the record in sacommunity is invalid,
#     # the council name could be wrong
#     # Later, will try to automate on how to get the exact council name from selenium
#     landing_page_errors_df = processed_data_df[processed_data_df\
#                                                ["is_record_available_in_sacommunity_db"] is False]
#     file_helper.save_run_file_to_csv(
#         landing_page_errors_df, run_id, DataModule.LANGING_PAGE_ERRORS)

#     landing_page_cleaned_df = processed_data_df[processed_data_df\
#                                                 ["is_record_available_in_sacommunity_db"] is True]
#     file_helper.save_run_file_to_csv(
#         landing_page_cleaned_df, run_id, DataModule.LANDING_PAGE_CLEANED)

#     return run_id
