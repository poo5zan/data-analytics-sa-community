"""
Helper methods for pandas library
"""

import pandas as pd


# pylint: disable=too-few-public-methods
class PandasHelper:
    """
    Pandas helper
    """

    def __init__(self) -> None:
        self.numeric_columns = ["sessions"]
        self.date_time_columns = ["start_date", "end_date"]

    def convert_data_types(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """convert data types"""
        for num_col in self.numeric_columns:
            if num_col in dataframe.columns:
                dataframe[num_col] = pd.to_numeric(dataframe[num_col])

        for date_col in self.date_time_columns:
            if date_col in dataframe.columns:
                dataframe[date_col] = pd.to_datetime(dataframe[date_col])

        return dataframe


# pylint: enable=too-few-public-methods
