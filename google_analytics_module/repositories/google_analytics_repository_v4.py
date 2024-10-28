"""version 4 of google analytics data"""
from google_analytics_module.enums import GoogleAuthenticationMethod
from google_analytics_module.repositories.google_analytics_repository_base import GoogleAnalyticsRepositoryBase
from dtos.date_range_dto import DateRangeDto
from google_analytics_module.dtos.google_analytics_filter_clause_dto import GoogleAnalyticsFilterClause
from google_analytics_module.dtos.google_analytics_request_config_dto import GoogleAnalyticsRequestConfig
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (DateRange, Dimension, Metric, RunReportRequest, FilterExpression, FilterExpressionList, Filter)

class GoogleAnalyticsRepositoryV4(GoogleAnalyticsRepositoryBase):
    """google analytics version 4
       Reference: https://developers.google.com/analytics/devguides/reporting/data/v1/basics

    """
    def __init__(self, google_authentication_method: GoogleAuthenticationMethod = GoogleAuthenticationMethod.OAUTH,
                 oauth_credentials_filepath: str = './credentials/oauth_credentials.json',
                 oauth_token_filepath: str = './credentials/token.json') -> None:
        super().__init__(google_authentication_method,
                         oauth_credentials_filepath,
                         oauth_token_filepath)
        
    def get_data(self,
                    property_id: str,
                    request_config: GoogleAnalyticsRequestConfig,
                    filter_clause: GoogleAnalyticsFilterClause):
        self.refresh_oauth_token()

        client = BetaAnalyticsDataClient(credentials=self.creds)
        
        dimensions_list = [Dimension(name=d)
                        for d in request_config.dimensions]
        
        metrics_list = [Metric(name=m)
                        for m in request_config.metrics]
        
        start_date = self.date_helper.convert_date_to_yyyy_mm_dd(filter_clause.date_range.start_date)
        end_date = self.date_helper.convert_date_to_yyyy_mm_dd(filter_clause.date_range.end_date)

        # if not self.str_helper.is_null_or_whitespace(filter_clause.dataset_id):
        # dimension_filter = FilterExpression(filter=Filter(
        #     field_name="customEvent:DatasetID",
        #     string_filter=Filter.StringFilter(value=filter_clause.dataset_id, match_type=Filter.StringFilter.MatchType.EXACT)))

        dimension_filter=FilterExpression(
            and_group=FilterExpressionList(
                expressions=[
                    FilterExpression(
                        filter=Filter(
                            field_name="customEvent:DatasetID",
                            string_filter=Filter.StringFilter(value=filter_clause.dataset_id, match_type=Filter.StringFilter.MatchType.EXACT),
                        )
                    ),
                    FilterExpression(
                        filter=Filter(
                            field_name="eventName",
                            string_filter=Filter.StringFilter(value="trackCustomData", match_type=Filter.StringFilter.MatchType.EXACT),
                        )
                    ),
                ]
            )
        )

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions_list,
            metrics=metrics_list,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=250000, #this is the maximum number of rows returned by api, default in 10000
            dimension_filter=dimension_filter
        )

        response = client.run_report(request)

        results = []
        for row in response.rows:
            result = {}
            for i, dimension_value in enumerate(row.dimension_values):
                dimension_name = response.dimension_headers[i].name
                result[dimension_name] = dimension_value.value

            for i, metric_value in enumerate(row.metric_values):
                metric_name = response.metric_headers[i].name
                result[metric_name] = metric_value.value
            
            results.append(result)

        return results
        
    def extract_data_from_response(self, response, date_range: DateRangeDto):
        """fomat response received from google analytics"""

        results = []
        for report in response.get('reports'):
            column_header = report.get('columnHeader')
            # if total is zero, continue to another
            if int(report.get('data').get('totals')[0]['values'][0]) == 0:
                # print('continue for loop to next item')
                continue
            dimensions = column_header.get('dimensions')
            dimensions_len = len(dimensions)
            metric_header = column_header.get('metricHeader')
            metrics = metric_header.get('metricHeaderEntries')
            metrics_len = len(metrics)

            if report.get('data').get('rows') is None:
                raise ValueError('No rows data')

            for row in report.get('data').get('rows'):
                result = {'start_date': date_range.start_date,
                            'end_date': date_range.end_date}
                for i in range(dimensions_len):
                    result[dimensions[i]] = row.get('dimensions')[i]

                metric_values = row.get('metrics')[0].get('values')
                for i in range(metrics_len):
                    result[metrics[i].get('name')] = metric_values[i]

                results.append(result)

        return results


