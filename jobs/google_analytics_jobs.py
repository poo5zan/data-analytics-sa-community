"""Google Analytics Jobs Module"""
import logging
from datetime import date, timedelta
from google_analytics_module.repositories.google_analytics_api_retrieval_v3 import GoogleAnalyticsApiRetrievalV3
from dtos.date_range_dto import DateRangeDto

from google_analytics_module.dtos.google_analytics_filter_clause_dto import GoogleAnalyticsFilterClause
from dtos.page_dto import PageDto
from helpers.enums import DataFrequency, DataModule, GoogleAuthenticationMethod, JobStatus
from helpers.metadata_helper import JobConfig, MetadataHelper
from helpers.file_helper import FileHelper
from helpers.settings_helper import SettingsHelper

ga_jobs_log = logging.getLogger(__name__)

class GoogleAnalyticsJobs():
    """Google Analytics Jobs"""
    def __init__(self, credentials_file_path='./credentials/credentials.json',
                 token_file_path='./credentials/token.json') -> None:
        self.credentials_file_path = credentials_file_path
        self.token_file_path = token_file_path
        self.metadata_helper = MetadataHelper()
        self.settings_helper = SettingsHelper()
        self.file_helper = FileHelper()

    def run_job(self, data_frequency: DataFrequency,
                data_module: DataModule,
                end_date: date):
        """Run Job"""
        job_log = f'data frequency: {data_frequency.name}, data module: {data_module.name}'
        metadata = self.metadata_helper.load_metadata(data_frequency, data_module)
        if metadata.job_status.get('value') == JobStatus.IN_PROGRESS.value:
            ga_jobs_log.info("Another job is in progress for %s", job_log)
            return
        start_date = self.metadata_helper.get_start_date(
            metadata.last_data_extraction_date, metadata.job_status)
        try:
            # of the current job is in progress, then don't run another job
            while start_date < end_date:
                google_analytics_api = GoogleAnalyticsApiRetrievalV3(
                    GoogleAuthenticationMethod.OAUTH,
                    self.credentials_file_path,
                    self.token_file_path)
                ga_jobs_log.info("Running job %s for start date %s", job_log, start_date)
                self.metadata_helper.save_metadata(JobConfig(data_frequency, data_module),
                              start_date,
                              JobStatus.IN_PROGRESS)
                filter_clause = GoogleAnalyticsFilterClause()
                filter_clause.set_date_range(DateRangeDto(start_date, start_date))
                filter_clause.set_page_dto(PageDto(
                    self.settings_helper.get_google_analytics_page_size(),
                    None))
                data = None
                if data_module.value == DataModule.AGE.value:
                    data = google_analytics_api.get_sessions_by_age(filter_clause)
                elif data_module.value == DataModule.GENDER.value:
                    data = google_analytics_api.get_sessions_by_gender(filter_clause)
                elif data_module.value == DataModule.LANDING_PAGE.value:
                    data = google_analytics_api.get_sessions_by_landing_page(filter_clause)
                else:
                    raise ValueError(f'Invalid data module {data_module.value}')

                file_path = self.file_helper.get_data_path(
                    self.settings_helper.get_file_storage_root_folder(),
                    data_frequency.name,
                    data_module.name,
                    start_date)
                print('saving file to ', file_path)
                self.file_helper.save_list_to_csv(data, file_path)

                self.metadata_helper.save_metadata(
                    JobConfig(data_frequency, data_module),
                    start_date,
                    JobStatus.SUCCESS)

                start_date = start_date + timedelta(days=1)
        except Exception as ex:
            failure_reason = str(ex)
            ga_jobs_log.error(ex)
            self.metadata_helper.save_metadata(
                JobConfig(data_frequency, data_module),
                start_date,
                JobStatus.FAILED,
                failure_reason=failure_reason)
            raise ex

    def age_daily(self, end_date: date):
        """Job: Age, Daily Data"""
        self.run_job(DataFrequency.DAILY, DataModule.AGE, end_date)

    def gender_daily(self, end_date: date):
        """Job: Gender, Daily Data"""
        self.run_job(DataFrequency.DAILY, DataModule.GENDER, end_date)

    def landing_page_daily(self, end_date: date):
        """Job: Landing Page, Daily Data"""
        self.run_job(DataFrequency.DAILY, DataModule.LANDING_PAGE, end_date)
