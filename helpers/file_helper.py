"""File helpers"""

import os
import shutil
from datetime import date
import pandas as pd
import jsonlines

from helpers.enums import DataModule
from helpers.settings_helper import SettingsHelper
from helpers.string_helper import StringHelper


class FileHelper:
    """helper methods for file handling"""

    def __init__(self) -> None:
        self.settings_helper = SettingsHelper()
        self.string_helper = StringHelper()

    def create_directory(self, dir_path: str):
        """create directory"""
        os.makedirs(dir_path, exist_ok=True)

    def create_directory_excluding_filename(self, file_path):
        """create directory excluding filename"""
        self.create_directory(os.path.dirname(file_path))

    def save_list_to_csv(self, data: list, file_path):
        """save list of data as csv"""
        self.create_directory(os.path.dirname(file_path))
        dataframe = pd.DataFrame(data)
        dataframe.to_csv(file_path, index=False)

    def get_data_path_in_current_directory(
        self, data_frequency_name, module_name, date_obj: date
    ):
        """get data path in current directory"""
        return self.get_data_path(".", data_frequency_name, module_name, date_obj)

    def get_file_name_based_on_date(self, date_obj: date):
        """get file name based on date"""
        month_str = str(date_obj.month).zfill(2)
        day_str = str(date_obj.day).zfill(2)
        return f"{date_obj.year}_{month_str}_{day_str}"

    def get_data_path(
        self, root_dir, data_frequency_name: str, module_name: str, date_obj: date
    ):
        """get data path
        Note: cannot have DataFrequency object because of circular dependency
        """
        month_str = str(date_obj.month).zfill(2)
        day_str = str(date_obj.day).zfill(2)
        data_dir_path = os.path.join(
            root_dir,
            "data",
            data_frequency_name,
            module_name,
            str(date_obj.year),
            month_str,
            day_str,
        )
        file_name = f"{date_obj.year}_{month_str}_{day_str}.csv"
        full_path = os.path.join(data_dir_path, file_name)
        return full_path

    def remove_directory(self, file_path):
        """removes directory with file contents"""
        dir_name = os.path.dirname(file_path)
        shutil.rmtree(dir_name)

    def save_df_to_csv(self, dataframe: pd.DataFrame, file_path: str):
        """save dataframe to csv"""
        self.create_directory_excluding_filename(file_path)
        dataframe.to_csv(file_path, index=False)

    def get_run_file_path(self, run_id: str, module: DataModule):
        """get run file path"""
        file_name = f"{module.name.lower()}.csv"
        root_dir = self.settings_helper.get_file_storage_root_folder()
        return os.path.join(root_dir, "data", run_id, file_name)

    def save_run_file_to_csv(
        self, dataframe: pd.DataFrame, run_id: str, module: DataModule
    ):
        """save run file dataframe to csv"""
        file_path = self.get_run_file_path(run_id, module)
        self.save_df_to_csv(dataframe, file_path)

    def read_run_file(self, run_id: str, module: DataModule):
        """read run file"""
        file_path = self.get_run_file_path(run_id, module)
        return pd.read_csv(file_path)

    def write_jsonlines(self, file_path: str, data_obj):
        """
        Append json to jsonl
        """
        self.make_directories_from_file_path(file_path)
        with jsonlines.open(file_path, "a") as writer:
            writer.write(data_obj)

    def read_jsonlines(self, file_path: str):
        """
        Read from jsonlines file
        """

        with jsonlines.open(file_path) as reader:
            for obj in reader:
                yield obj

    def read_jsonlines_all(self, file_path: str):
        """
        Read from jsonlines without yield
        """
        lines = []
        for line in self.read_jsonlines(file_path):
            lines.append(line)

        return lines

    def extract_directory_path(self, file_path: str):
        """
        Extract directory path from the full file path
        """
        self.validate_file_path(file_path)
        return os.path.dirname(file_path)

    def make_directories(self, dir_path: str):
        """Make directories"""
        os.makedirs(dir_path, exist_ok=True)

    def make_directories_from_file_path(self, file_path: str):
        """Make directories from file path"""
        self.make_directories(self.extract_directory_path(file_path))

    def validate_file_path(self, file_path: str):
        """Validate file path"""
        if self.string_helper.is_null_or_whitespace(file_path):
            raise ValueError("File path is null or empty")

    def does_file_exist(self, file_path: str):
        """Check if file exists"""
        return os.path.exists(file_path)
