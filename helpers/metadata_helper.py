"""Metadata helper module"""
from datetime import datetime, date, timedelta
import json
import os

# Comment these to run the methods from the current file as entry point
from helpers.enums import DataFrequency, DataModule, JobStatus
from helpers.file_helper import FileHelper
from helpers.date_helper import DateHelper

class JobConfig():
    """Job Config : data_frequency and data_module"""

    def __init__(self, data_frequency: DataFrequency,
                 data_module: DataModule) -> None:
        self.data_frequency = data_frequency
        self.data_module = data_module

    def to_dict(self):
        """returns dictionary representation of the jobConfig dto"""
        return self.__dict__

    @classmethod
    def from_dict(cls, dict_obj):
        """creates new instance of jobConfig dto from dictionary"""
        return cls(**dict_obj)

# Python DTO: https://hackernoon.com/dto-in-python-an-explanation


class MetadataDto():
    """Data Transfer Object (DTO) for Metadata"""

    def __init__(self, **kwargs) -> None:
        self.data_frequency = kwargs.get("data_frequency")
        self.module = kwargs.get("module")
        self.last_data_extraction_date = kwargs.get(
            "last_data_extraction_date")
        self.job_status = kwargs.get("job_status")
        self.failure_reason = kwargs.get("failure_reason")
        self.created_date = kwargs.get("created_date")

    def to_dict(self):
        """returns dictionary representation of the metadata dto"""
        return self.__dict__

    @classmethod
    def from_dict(cls, metadata_dict):
        """creates new instance of metadata dto from dictionary"""
        return cls(**metadata_dict)


class MetadataHelper():
    """metadata helper class"""
    def __init__(self, file_path = "./settings/metadata.json"):
        self.file_path = file_path
        self.file_helper = FileHelper()
        self.date_helper = DateHelper()

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def new_metadata(self,
                    data_frequency: DataFrequency,
                    module: DataModule,
                    last_data_extraction_date: date | datetime,
                    job_status: JobStatus,
                    failure_reason=''):
        """creates new object for metadata"""
        return {
            'data_frequency': {
                "value": data_frequency.value,
                "name": data_frequency.name
            },
            "module": {
                "value": module.value,
                "name": module.name
            },
            'last_data_extraction_date': self.date_helper.convert_date_to_yyyy_mm_dd(
                last_data_extraction_date),
            "job_status": {
                "value": job_status.value,
                "name": job_status.name
            },
            'failure_reason': failure_reason,
            "created_date": {
                "date_local": self.date_helper.convert_date_to_yyyy_mm_dd_hh_mm_ss(datetime.now()),
                "date_utc": self.date_helper.convert_date_to_yyyy_mm_dd_hh_mm_ss(datetime.utcnow())
            }
        }
    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-positional-arguments

    def sort_metadatas(self, metadatas):
        """sort metadata first by data_frequency and then by module"""
        return sorted(metadatas,
                    key=lambda x: (x.get("data_frequency").get("name"),
                                    x.get("module").get("name")))


    def load_all_metadata(self):
        """load all metadata"""
        metadata = []

        if not os.path.exists(self.file_path):
            return metadata

        with open(self.file_path, 'r', encoding='UTF-8') as file_obj:
            metadata = file_obj.read()

        if metadata is None or metadata == "":
            return []

        metadatas = json.loads(metadata)
        # sort
        return self.sort_metadatas(metadatas)


    def load_metadata(self, data_frequency: DataFrequency,
                    module: DataModule,
                    default_date: date = date(2021, 1, 1)) -> MetadataDto:
        """Load metadata"""
        all_metadata = self.load_all_metadata()
        metadatas = [m for m in all_metadata if m['module']['value'] ==
                    module.value and m['data_frequency']['value'] == data_frequency.value]

        if len(metadatas) > 0:
            metadata = MetadataDto.from_dict(metadatas[0])
            metadata.last_data_extraction_date = \
                self.date_helper.convert_yyyy_mm_dd_to_date(
                    metadata.last_data_extraction_date)
            metadata.created_date["date_local"] = \
                self.date_helper.convert_yyyy_mm_dd_hh_mm_ss_to_date(
                    metadata.created_date["date_local"])
            metadata.created_date['date_utc'] = \
                self.date_helper.convert_yyyy_mm_dd_hh_mm_ss_to_date(
                    metadata.created_date['date_utc'])

            return metadata

        if len(metadatas) == 0:
            self.save_metadata(JobConfig(data_frequency, module),
                        default_date,
                        JobStatus.DEFAULT,
                        failure_reason='')
            # call the saved data again
            print("Saved default first time start date, and returning the first date")
            return self.load_metadata(data_frequency, module)

        return None


    def save_metadata(self, job_config: JobConfig,
                    last_date_extraction_date: date | datetime,
                    status: JobStatus,
                    failure_reason=''):
        """Save metadata"""
        self.file_helper.create_directory_excluding_filename(self.file_path)
        all_metadata = self.load_all_metadata()
        other_metadata = [m for m in all_metadata if not
                        (m['module'].get('value') == job_config.data_module.value and
                        m['data_frequency'].get('value') == job_config.data_frequency.value)]
        metadata = self.new_metadata(job_config.data_frequency,
                                job_config.data_module,
                                last_date_extraction_date,
                                status,
                                failure_reason)
        other_metadata.append(metadata)
        new_metadatas_json = json.dumps(self.sort_metadatas(other_metadata))

        with open(self.file_path, 'w', encoding='UTF-8') as file_obj:
            file_obj.write(new_metadatas_json)


    def get_start_date(self, last_data_extraction_date: date | datetime,
                       job_status: JobStatus):
        """if the last job was success, then return the next day, 
        else return the same day to repeat the proecss"""
        if job_status.get('value') == JobStatus.SUCCESS.value:
            return last_data_extraction_date + timedelta(days=1)
        return last_data_extraction_date
