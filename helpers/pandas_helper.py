import pandas as pd

class PandasHelper():
    def convert_data_types(
        self,
        dataframe: pd.DataFrame,
        numeric_columns=["sessions"],
        date_time_columns = ["start_date", "end_date"]
    ) -> pd.DataFrame:
        """convert data types"""
        for num_col in numeric_columns:
            if num_col in dataframe.columns:
                dataframe[num_col] = pd.to_numeric(dataframe[num_col])

        
        for date_col in date_time_columns:
            if date_col in dataframe.columns:
                dataframe[date_col] = pd.to_datetime(dataframe[date_col])

        return dataframe
