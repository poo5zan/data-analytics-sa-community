# # """version 3 google api"""
# # import pandas as pd
# # from data_retrieval.google_analytics_api_retrieval import GoogleAnalyticsApiRetrieval
# # from dtos.google_analytics_filter_clause_dto import GoogleAnalyticsFilterClause
# # from dtos.google_analytics_request_config_dto import GoogleAnalyticsRequestConfig

# # class GoogleAnalyticsApiRetrievalV3(GoogleAnalyticsApiRetrieval):
# #     """google api version 3"""
# #     def get_sessions_by_gender(self,
# #                                filter_clause: GoogleAnalyticsFilterClause):
# #         """get session data by gender"""
# #         dimensions = ['customVarValue1', 'userGender']
# #         metrics = ["sessions"]
# #         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
# #             dimensions, metrics),
# #             filter_clause=filter_clause)

# #         # create dataframe
# #         data_df = pd.DataFrame(data)
# #         # rename columns
# #         data_df = data_df.rename(columns={
# #             'ga:customVarValue1': 'dataset_id',
# #             'ga:sessions': 'sessions',
# #             'ga:userGender': 'gender'
# #         })

# #         return self.convert_data_types(data_df)

# #     def get_sessions_by_landing_page(self,
# #                                      filter_clause: GoogleAnalyticsFilterClause):
# #         """get session data with landing page"""
# #         dimensions = ['customVarValue1', 'landingPagePath',
# #                       'deviceCategory', 'sourceMedium']
# #         metrics = ["sessions"]
# #         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
# #                              dimensions, metrics),
# #                              filter_clause=filter_clause)

# #         # create dataframe
# #         data_df = pd.DataFrame(data)
# #         # rename columns
# #         data_df = data_df.rename(columns={
# #             'ga:customVarValue1': 'dataset_id',
# #             'ga:landingPagePath': 'landing_page',
# #             'ga:deviceCategory': 'device_category',
# #             'ga:sourceMedium': 'source_medium',
# #             'ga:sessions': 'sessions'
# #         })

# #         return self.convert_data_types(data_df)

# #     def get_sessions_by_age(self,
# #                             filter_clause: GoogleAnalyticsFilterClause):
# #         """get sessions data by age"""
# #         dimensions = ['customVarValue1', 'userAgeBracket']
# #         metrics = ["sessions"]
# #         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
# #             dimensions, metrics),
# #             filter_clause=filter_clause)

# #         # create dataframe
# #         data_df = pd.DataFrame(data)
# #         # rename columns
# #         data_df = data_df.rename(columns={
# #             'ga:customVarValue1': 'dataset_id',
# #             'ga:sessions': 'sessions',
# #             'ga:userAgeBracket': 'age_bracket'
# #         })

# #         return self.convert_data_types(data_df)

# #     def get_page_views_and_sessions(self, filter_clause: GoogleAnalyticsFilterClause):
# #         """get page views"""
# #         dimensions = ['customVarValue1', 'customVarValue2', 'customVarValue3',
# #                       'customVarValue4', 'customVarValue5', 'landingPagePath']
# #         metrics = ["pageviews", "sessions"]
# #         data = self.get_data(request_config=GoogleAnalyticsRequestConfig(
# #                              dimensions, metrics),
# #                              filter_clause=filter_clause)

# #         data_df = pd.DataFrame(data)
# #         # rename columns
# #         data_df = data_df.rename(columns={
# #             'ga:customVarValue1': 'dataset_id',
# #             'ga:customVarValue2': 'post_code',
# #             'ga:customVarValue3': 'state',
# #             'ga:customVarValue4': 'subject',
# #             'ga:customVarValue5': 'org_type',
# #             'ga:sessions': 'sessions',
# #             'ga:landingPagePath': 'landing_page',
# #             'ga:pageviews': 'page_views'
# #         })
# #         return data_df


#     # def get_data(self,
#     #             request_config: GoogleAnalyticsRequestConfig,
#     #             filter_clause: GoogleAnalyticsFilterClause,
#     #             property_id):
#     #     """get all data"""
#     #     results = []
#     #     page_token = filter_clause.page_dto.page_token

#     #     while True:
#     #         new_page_dto = PageDto(filter_clause.page_dto.page_size, page_token)
#     #         filter_clause.set_page_dto(new_page_dto)
#     #         response = self.google_analytics_repository.get_batch_data(property_id=property_id,
#     #                                     request_config=request_config,
#     #                                     filter_clause=filter_clause)
#     #         self.log.debug('request_config %s, date_range %s,\
#     #                                     page_dto %s, filter_clause %s, response %s',
#     #                                 request_config.to_dict(),
#     #                                 filter_clause.date_range.to_dict(),
#     #                                 filter_clause.page_dto.to_dict(),
#     #                                 filter_clause.to_dict(),
#     #                                 response)
#     #         results.extend(self.extract_data_from_response(
#     #             response, filter_clause.date_range))
#     #         page_token = response['reports'][0].get('nextPageToken')

#     #         total_rows = response.get('reports')[0].get(
#     #             'data').get('totals')[0]['values'][0]
#     #         self.log.debug(
#     #             "Retrieved %s of %s ", len(results), total_rows)

#     #         if page_token is None:
#     #             self.log.debug("All data has been retrieved")
#     #             break

#     #     return results


#     # def extract_data_from_response(self, response, date_range: DateRangeDto):
#     #     """fomat response received from google analytics"""

#     #     results = []
#     #     for report in response.get('reports'):
#     #         column_header = report.get('columnHeader')
#     #         # if total is zero, continue to another
#     #         if int(report.get('data').get('totals')[0]['values'][0]) == 0:
#     #             # print('continue for loop to next item')
#     #             continue
#     #         dimensions = column_header.get('dimensions')
#     #         dimensions_len = len(dimensions)
#     #         metric_header = column_header.get('metricHeader')
#     #         metrics = metric_header.get('metricHeaderEntries')
#     #         metrics_len = len(metrics)

#     #         if report.get('data').get('rows') is None:
#     #             raise ValueError('No rows data')

#     #         for row in report.get('data').get('rows'):
#     #             result = {'start_date': date_range.start_date,
#     #                       'end_date': date_range.end_date}
#     #             for i in range(dimensions_len):
#     #                 result[dimensions[i]] = row.get('dimensions')[i]

#     #             metric_values = row.get('metrics')[0].get('values')
#     #             for i in range(metrics_len):
#     #                 result[metrics[i].get('name')] = metric_values[i]

#     #             results.append(result)

#     #     return results

#     # def construct_filter(self, dimension_name: str, operator: str, expression: str):
#     #     """construct filter object"""
#     #     return {
#     #         'dimensionName': dimension_name,
#     #         'operator': operator,
#     #         'expressions': [expression]
#     #     }

#     def get_batch_data(self,
#                        view_id: str,
#                        request_config: GoogleAnalyticsRequestConfig,
#                        filter_clause: GoogleAnalyticsFilterClause):
#         """get batch data"""
#         self.refresh_oauth_token()
#         analytics = build('analyticsreporting', 'v4', credentials=self.creds)

#         metrics_list = [{'expression': m}
#                         for m in request_config.metrics]
#         dimensions_list = [{'name': d}
#                            for d in request_config.dimensions]

#         request = {
#                     'pageSize': filter_clause.page_dto.page_size,
#                     'pageToken': filter_clause.page_dto.page_token,
#                     'viewId': view_id,
#                     'dateRanges': [
#                         {
#                             'startDate': self.date_helper.convert_date_to_yyyy_mm_dd(
#                                 filter_clause.date_range.start_date),
#                             'endDate': self.date_helper.convert_date_to_yyyy_mm_dd(
#                                 filter_clause.date_range.end_date)
#                         }],
#                     'metrics': metrics_list,
#                     'dimensions': dimensions_list,
#                 }

#         if filter_clause is not None:
#             filters = []
#             if not self.str_helper.is_null_or_whitespace(filter_clause.dataset_id):
#                 filters.append(self.construct_filter('ga:customVarValue1',
#                                                      'EXACT',
#                                                      filter_clause.dataset_id))

#             if len(filters) > 0:
#                 request['dimensionFilterClauses'] = [
#                     {
#                         'filters' : filters
#                     }
#                 ]
#         request_body = {
#             'reportRequests': [
#                 request
#             ]
#         }

#         # pylint: disable=no-member
#         return analytics.reports().batchGet(body=request_body).execute()
#         # pylint: enable=no-member

# def get_data(self,
#              request_config: GoogleAnalyticsRequestConfig,
#              filter_clause: GoogleAnalyticsFilterClause):
#     """get all data"""
#     results = []
#     page_token = filter_clause.page_dto.page_token

#     view_id = ''
#     if filter_clause.api_version == GoogleApiVersion.VERSION_3:
#         view_id = self.settings_helper.get_google_analytics_view_id_v3()
#     elif filter_clause.api_version == GoogleApiVersion.VERSION_4:
#         view_id = self.settings_helper.get_google_analytics_view_id_v4()
#     else:
#         raise ValueError(f'GoogleApiVersion: {filter_clause.api_version} is not supported')

#     while True:
#         new_page_dto = PageDto(filter_clause.page_dto.page_size, page_token)
#         filter_clause.set_page_dto(new_page_dto)
#         # response = self.get_batch_data(view_id=view_id,
#         #                                request_config=request_config,
#         #                                filter_clause=filter_clause)

#         response = self.get_batch_data_v4(property_id=view_id,
#                                        request_config=request_config,
#                                        filter_clause=filter_clause)
#         self.log.debug('request_config %s, date_range %s,\
#                                     page_dto %s, filter_clause %s, response %s',
#                                    request_config.to_dict(),
#                                    filter_clause.date_range.to_dict(),
#                                    filter_clause.page_dto.to_dict(),
#                                    filter_clause.to_dict(),
#                                    response)
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

# def get_columns_to_rename(self, version: GoogleApiVersion):
#     """returns columns to rename"""
#     if version == GoogleApiVersion.VERSION_3:
#         return {
#             "ga:sessions": "sessions",
#             "ga:userGender": "gender",
#             "ga:landingPagePath": "landing_page",
#             "ga:deviceCategory": "device_category",
#             "ga:sourceMedium": "source_medium",
#             "ga:userAgeBracket": "age_bracket",
#             "ga:customVarValue1": "dataset_id",
#             "ga:customVarValue2": "post_code",
#             "ga:customVarValue3": "state",
#             "ga:customVarValue4": "subject",
#             "ga:customVarValue5": "org_type",
#             "ga:pageviews": "page_views"
#         }
#     elif version == GoogleApiVersion.VERSION_4:
#         return {
#             "ga:customVarValue1": "dataset_id",
#             "ga:customVarValue2": "post_code",
#             "ga:customVarValue3": "state",
#             "ga:customVarValue4": "subject",
#             "ga:customVarValue5": "org_type",
#             "ga:sessions": "sessions",
#             "ga:landingPagePath": "landing_page",
#             "ga:pageviews": "page_views"
#         }

#     raise ValueError(f"google Api Version {version} is Invalid.")

# def get_data_as_df(self,
#              request_config: GoogleAnalyticsRequestConfig,
#              filter_clause: GoogleAnalyticsFilterClause):
#     data = self.get_data(request_config, filter_clause)

#     data_df = pd.DataFrame(data)
#     # rename columns

#     columns_to_rename = self.get_columns_to_rename(filter_clause.api_version)
#     for key, value in columns_to_rename.items():
#         if key in data_df.columns:
#             data_df = data_df.rename(columns={key:value})

#     return self.convert_data_types(data_df)
