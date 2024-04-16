"""get data from url request dto"""


class GetDataFromUrlRequestDto():
    """request config page size and page token"""
    # pylint: disable=too-many-arguments
    def __init__(self,
                 url: str,
                 is_headless: bool,
                 to_exclude: list,
                 timeout_in_seconds: int,
                 xpath: str) -> None:
        self.url = url
        self.is_headless = is_headless
        self.to_exclude = to_exclude
        self.timeout_in_seconds = timeout_in_seconds
        self.xpath = xpath

    # pylint: enable=too-many-arguments

    def to_dict(self):
        """returns dictionary representation of dto"""
        return self.__dict__

    @classmethod
    def from_dict(cls, dict_obj):
        """creates new instance from dictionary"""
        return cls(**dict_obj)
