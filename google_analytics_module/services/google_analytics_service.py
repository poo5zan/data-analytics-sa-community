"""
Google analytics service
"""

from datetime import date
from joblib import Parallel, delayed
import pandas as pd
from dtos.date_range_dto import DateRangeDto
from google_analytics_module.dtos.google_analytics_filter_clause_dto import (
    GoogleAnalyticsFilterClause,
)
from google_analytics_module.dtos.google_analytics_request_config_dto import (
    GoogleAnalyticsRequestConfig,
)
from google_analytics_module.repositories.google_analytics_repository_v4 import (
    GoogleAnalyticsRepositoryV4,
)
from helpers.pandas_helper import PandasHelper
from helpers.settings_helper import SettingsHelper
from helpers.string_helper import StringHelper


class GoogleAnalyticsService:
    """Google analytics service"""

    def __init__(self, google_analytics_repository=None) -> None:
        if google_analytics_repository is None:
            self.google_analytics_repository = GoogleAnalyticsRepositoryV4()
        else:
            self.google_analytics_repository = google_analytics_repository
        self.settings_helper = SettingsHelper()
        self.property_id = self.settings_helper.get_google_analytics_view_id_v4()
        self.string_helper = StringHelper()
        self.pandas_helper = PandasHelper()

    # pylint: disable=too-many-arguments
    def get_data(
        self,
        dataset_id: str,
        start_date: date,
        end_date: date,
        dimensions,
        metrics,
        organisation_id: str = "",
    ):
        """Get data from google analytics"""
        filter_clause = GoogleAnalyticsFilterClause()
        filter_clause.set_dataset_id(dataset_id)
        filter_clause.set_date_range(
            DateRangeDto(start_date=start_date, end_date=end_date)
        )
        filter_clause.set_organisation_id(organisation_id)
        request_config = GoogleAnalyticsRequestConfig(dimensions, metrics)
        results = self.google_analytics_repository.get_data(
            property_id=self.property_id,
            request_config=request_config,
            filter_clause=filter_clause,
        )

        return results

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    def get_sessions_by_landing_page(
        self,
        dataset_id: str,
        start_date: date,
        end_date: date,
        organisation_id: str = "",
        additional_dimensions: list[str] = None,
        additional_metrics: list[str] = None,
    ):
        """get session data with landing page
        additional dimensions could be "eventName", "date"
        additional metrics could be "eventCount"
        """
        dimensions = ["customEvent:DatasetID", "landingPage"]
        if additional_dimensions:
            dimensions.extend(additional_dimensions)

        metrics = ["sessions"]
        if additional_metrics:
            metrics.extend(additional_metrics)

        return self.get_data(
            dataset_id,
            start_date,
            end_date,
            dimensions,
            metrics,
            organisation_id=organisation_id,
        )

    # pylint: enable=too-many-arguments

    def get_sessions_by_landing_page_as_df(
        self,
        dataset_id: str,
        start_date: date,
        end_date: date,
        organisation_id: str = "",
    ):
        """Get sessions by landing page as dataframe"""
        results = self.get_sessions_by_landing_page(
            dataset_id, start_date, end_date, organisation_id=organisation_id
        )
        results_df = pd.DataFrame(results)
        return self.pandas_helper.convert_data_types(results_df)

    # pylint: disable=too-many-arguments
    def get_sessions_by_organisation_id(
        self,
        start_date: date,
        end_date: date,
        organisation_id: str,
        row_count=None,
        total_count=None,
    ):
        """get sessions by organisation id"""
        if row_count and total_count:
            print(
                f"get_sessions_by_landing_page row_count {row_count}\
                    of {total_count}. organisation_id: {organisation_id}"
            )
        sessions = self.get_sessions_by_landing_page(
            "", start_date, end_date, organisation_id
        )
        sessions_count = 0
        for session in sessions:
            sessions_count += int(session.get("sessions", 0))

        return {"organisation_id": organisation_id, "sessions_count": sessions_count}

    # pylint: enable=too-many-arguments

    def get_sessions_by_organisation_ids(
        self, start_date: date, end_date: date, organisation_ids: list[str], n_jobs=5
    ):
        """get sessions by organisation ids"""
        total_count = len(organisation_ids)
        return Parallel(n_jobs=n_jobs)(
            delayed(self.get_sessions_by_organisation_id)(
                start_date, end_date, organisation_id, row_count, total_count
            )
            for row_count, organisation_id in enumerate(organisation_ids)
        )

    def get_sessions_by_organisation_ids_as_df(
        self,
        start_date: date,
        end_date: date,
        organisation_ids: list[str],
        n_jobs=5,
    ):
        """get sessions by organisation ids as dataframe"""
        sessions = self.get_sessions_by_organisation_ids(
            start_date=start_date,
            end_date=end_date,
            organisation_ids=organisation_ids,
            n_jobs=n_jobs,
        )
        return pd.DataFrame(sessions)

    def get_sessions_by_age(self, dataset_id: str, start_date: date, end_date: date):
        """get sessions data by age"""
        dimensions = ["customEvent:DatasetID", "userAgeBracket"]
        metrics = ["sessions"]

        return self.get_data(dataset_id, start_date, end_date, dimensions, metrics)

    def get_sessions_by_age_as_df(
        self, dataset_id: str, start_date: date, end_date: date
    ):
        """get sessions by age as dataframe"""
        results = self.get_sessions_by_age(dataset_id, start_date, end_date)
        return pd.DataFrame(results)

    def get_sessions_by_gender(self, dataset_id: str, start_date: date, end_date: date):
        """get session data by gender"""
        dimensions = ["customEvent:DatasetID", "userGender"]
        metrics = ["sessions"]

        return self.get_data(dataset_id, start_date, end_date, dimensions, metrics)

    def get_sessions_by_gender_as_df(
        self, dataset_id: str, start_date: date, end_date: date
    ):
        """get sessions by gender as dataframe"""
        results = self.get_sessions_by_gender(dataset_id, start_date, end_date)
        return pd.DataFrame(results)

    def get_sessions_by_source(self, dataset_id: str, start_date: date, end_date: date):
        """get session data by source"""
        dimensions = ["customEvent:DatasetID", "sessionSource"]
        metrics = ["sessions"]

        return self.get_data(dataset_id, start_date, end_date, dimensions, metrics)

    def get_sessions_by_source_as_df(
        self, dataset_id: str, start_date: date, end_date: date
    ):
        """get sessions by source as dataframe"""
        results = self.get_sessions_by_source(dataset_id, start_date, end_date)
        return pd.DataFrame(results)

    def get_sessions_by_medium(self, dataset_id: str, start_date: date, end_date: date):
        """get session data by source"""
        dimensions = ["customEvent:DatasetID", "sessionMedium"]
        metrics = ["sessions"]

        return self.get_data(dataset_id, start_date, end_date, dimensions, metrics)

    def get_sessions_by_medium_as_df(
        self, dataset_id: str, start_date: date, end_date: date
    ):
        """get sessions by medium as dataframe"""
        results = self.get_sessions_by_medium(dataset_id, start_date, end_date)
        return pd.DataFrame(results)
