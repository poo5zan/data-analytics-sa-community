# """version 3 google api"""
# import pandas as pd
# from data_retrieval.google_analytics_api_retrieval import GoogleAnalyticsApiRetrieval
# from dtos.google_analytics_filter_clause_dto import GoogleAnalyticsFilterClause
# from dtos.google_analytics_request_config_dto import GoogleAnalyticsRequestConfig

# class GoogleAnalyticsApiRetrievalV3(GoogleAnalyticsApiRetrieval):
#     """google api version 3"""
#     def get_sessions_by_gender(self,
#                                filter_clause: GoogleAnalyticsFilterClause):
#         """get session data by gender"""
#         dimensions = ['customVarValue1', 'userGender']
#         metrics = ["sessions"]
#         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
#             dimensions, metrics),
#             filter_clause=filter_clause)

#         # create dataframe
#         data_df = pd.DataFrame(data)
#         # rename columns
#         data_df = data_df.rename(columns={
#             'ga:customVarValue1': 'dataset_id',
#             'ga:sessions': 'sessions',
#             'ga:userGender': 'gender'
#         })

#         return self.convert_data_types(data_df)

#     def get_sessions_by_landing_page(self,
#                                      filter_clause: GoogleAnalyticsFilterClause):
#         """get session data with landing page"""
#         dimensions = ['customVarValue1', 'landingPagePath',
#                       'deviceCategory', 'sourceMedium']
#         metrics = ["sessions"]
#         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
#                              dimensions, metrics),
#                              filter_clause=filter_clause)

#         # create dataframe
#         data_df = pd.DataFrame(data)
#         # rename columns
#         data_df = data_df.rename(columns={
#             'ga:customVarValue1': 'dataset_id',
#             'ga:landingPagePath': 'landing_page',
#             'ga:deviceCategory': 'device_category',
#             'ga:sourceMedium': 'source_medium',
#             'ga:sessions': 'sessions'
#         })

#         return self.convert_data_types(data_df)

#     def get_sessions_by_age(self,
#                             filter_clause: GoogleAnalyticsFilterClause):
#         """get sessions data by age"""
#         dimensions = ['customVarValue1', 'userAgeBracket']
#         metrics = ["sessions"]
#         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
#             dimensions, metrics),
#             filter_clause=filter_clause)

#         # create dataframe
#         data_df = pd.DataFrame(data)
#         # rename columns
#         data_df = data_df.rename(columns={
#             'ga:customVarValue1': 'dataset_id',
#             'ga:sessions': 'sessions',
#             'ga:userAgeBracket': 'age_bracket'
#         })

#         return self.convert_data_types(data_df)

#     def get_page_views_and_sessions(self, filter_clause: GoogleAnalyticsFilterClause):
#         """get page views"""
#         dimensions = ['customVarValue1', 'customVarValue2', 'customVarValue3',
#                       'customVarValue4', 'customVarValue5', 'landingPagePath']
#         metrics = ["pageviews", "sessions"]
#         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
#                              dimensions, metrics),
#                              filter_clause=filter_clause)

#         data_df = pd.DataFrame(data)
#         # rename columns
#         data_df = data_df.rename(columns={
#             'ga:customVarValue1': 'dataset_id',
#             'ga:customVarValue2': 'post_code',
#             'ga:customVarValue3': 'state',
#             'ga:customVarValue4': 'subject',
#             'ga:customVarValue5': 'org_type',
#             'ga:sessions': 'sessions',
#             'ga:landingPagePath': 'landing_page',
#             'ga:pageviews': 'page_views'
#         })
#         return data_df


    # def get_data(self,
    #             request_config: GoogleAnalyticsRequestConfig,
    #             filter_clause: GoogleAnalyticsFilterClause,
    #             property_id):
    #     """get all data"""
    #     results = []
    #     page_token = filter_clause.page_dto.page_token

    #     while True:
    #         new_page_dto = PageDto(filter_clause.page_dto.page_size, page_token)
    #         filter_clause.set_page_dto(new_page_dto)
    #         response = self.google_analytics_repository.get_batch_data(property_id=property_id,
    #                                     request_config=request_config,
    #                                     filter_clause=filter_clause)
    #         self.log.debug('request_config %s, date_range %s,\
    #                                     page_dto %s, filter_clause %s, response %s',
    #                                 request_config.to_dict(),
    #                                 filter_clause.date_range.to_dict(),
    #                                 filter_clause.page_dto.to_dict(),
    #                                 filter_clause.to_dict(),
    #                                 response)
    #         results.extend(self.extract_data_from_response(
    #             response, filter_clause.date_range))
    #         page_token = response['reports'][0].get('nextPageToken')

    #         total_rows = response.get('reports')[0].get(
    #             'data').get('totals')[0]['values'][0]
    #         self.log.debug(
    #             "Retrieved %s of %s ", len(results), total_rows)

    #         if page_token is None:
    #             self.log.debug("All data has been retrieved")
    #             break

    #     return results