"""version 4 of google analytics data"""

# pylint: disable=no-name-in-module
# pylint: disable=import-error
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    FilterExpressionList,
    Filter,
)
# pylint: enable=no-name-in-module
# pylint: enable=import-error

from google_analytics_module.enums import GoogleAuthenticationMethod
from google_analytics_module.repositories.google_analytics_repository_base import (
    GoogleAnalyticsRepositoryBase,
)
from google_analytics_module.dtos.google_analytics_filter_clause_dto import (
    GoogleAnalyticsFilterClause,
)
from google_analytics_module.dtos.google_analytics_request_config_dto import (
    GoogleAnalyticsRequestConfig,
)
from helpers.date_helper import DateHelper


class GoogleAnalyticsRepositoryV4(GoogleAnalyticsRepositoryBase):
    """google analytics version 4
    Reference: https://developers.google.com/analytics/devguides/reporting/data/v1/basics

    """

    def __init__(
        self,
        google_authentication_method=GoogleAuthenticationMethod.SERVICE_ACCOUNT,
        oauth_credentials_filepath: str = "./credentials/oauth_credentials.json",
        oauth_token_filepath: str = "./credentials/token.json",
    ) -> None:
        super().__init__(
            google_authentication_method,
            oauth_credentials_filepath,
            oauth_token_filepath,
        )
        self.date_helper = DateHelper()

    def get_data(
        self,
        property_id: str,
        request_config: GoogleAnalyticsRequestConfig,
        filter_clause: GoogleAnalyticsFilterClause,
    ):
        """Get data from google analytics api"""
        if self.google_authentication_method == GoogleAuthenticationMethod.OAUTH:
            self.refresh_oauth_token()

        client = BetaAnalyticsDataClient(credentials=self.creds)
        dimensions_list = [Dimension(name=d) for d in request_config.dimensions]
        metrics_list = [Metric(name=m) for m in request_config.metrics]

        start_date = self.date_helper.convert_date_to_yyyy_mm_dd(
            filter_clause.date_range.start_date
        )
        end_date = self.date_helper.convert_date_to_yyyy_mm_dd(
            filter_clause.date_range.end_date
        )

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions_list,
            metrics=metrics_list,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=250000,  # this is the maximum number of rows returned by api, default in 10000
            dimension_filter=FilterExpression(
                and_group=FilterExpressionList(
                    expressions=self.get_filter_expressions(filter_clause)
                )
            ),
        )

        response = client.run_report(request)
        return self.format_response(response)

    def get_filter_expressions(self, filter_clause: GoogleAnalyticsFilterClause):
        """contruct filter expressions"""
        filter_expressions = [
            FilterExpression(
                filter=Filter(
                    field_name="eventName",
                    string_filter=Filter.StringFilter(
                        value="trackCustomData",
                        match_type=Filter.StringFilter.MatchType.EXACT,
                    ),
                )
            )
        ]

        if not self.str_helper.is_null_or_whitespace(filter_clause.dataset_id):
            filter_expressions.append(
                FilterExpression(
                    filter=Filter(
                        field_name="customEvent:DatasetID",
                        string_filter=Filter.StringFilter(
                            value=filter_clause.dataset_id,
                            match_type=Filter.StringFilter.MatchType.EXACT,
                        ),
                    )
                )
            )

        if not self.str_helper.is_null_or_whitespace(filter_clause.organisation_id):
            filter_expressions.append(
                FilterExpression(
                    filter=Filter(
                        field_name="landingPage",
                        string_filter=Filter.StringFilter(
                            value=f"/org/{filter_clause.organisation_id}",
                            match_type=Filter.StringFilter.MatchType.BEGINS_WITH,
                        ),
                    )
                )
            )

        return filter_expressions

    def format_response(self, response):
        """Format response"""
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
