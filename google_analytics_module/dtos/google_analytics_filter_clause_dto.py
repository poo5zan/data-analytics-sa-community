"""filter for google analytics api request"""
from dtos.date_range_dto import DateRangeDto
from dtos.page_dto import PageDto
from helpers.enums import GoogleApiVersion


class GoogleAnalyticsFilterClause():
    """filter clauses"""

    def __init__(self) -> None:
        self.dataset_id: str = None
        self.date_range: DateRangeDto = None
        self.page_dto: PageDto = None
        self.council_name = ''
        self.api_version = GoogleApiVersion.DEFAULT

    def set_dataset_id(self, dataset_id: str):
        """set dataset id"""
        self.dataset_id = dataset_id

    def set_date_range(self, date_range: DateRangeDto):
        """set date range"""
        self.date_range = date_range

    def set_page_dto(self, page_dto: PageDto):
        """set page dto"""
        self.page_dto = page_dto

    def set_council_name(self, council_name: str):
        """set council name"""
        self.council_name = council_name

    def set_api_version(self, api_version: GoogleApiVersion):
        """set api version"""
        self.api_version = api_version

    def to_dict(self):
        """returns dictionary representation of dto"""
        return self.__dict__

    @classmethod
    def from_dict(cls, dict_obj):
        """creates new instance from dictionary"""
        return cls(**dict_obj)
