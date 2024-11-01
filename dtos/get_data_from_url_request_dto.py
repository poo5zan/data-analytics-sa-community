"""get data from url request dto"""


class GetDataFromUrlRequestDto():
    """request config page size and page token"""
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def __init__(self,
                 url: str,
                 is_headless: bool,
                 to_exclude: list,
                 timeout_in_seconds: int,
                 content_xpath: str,
                 no_content_xpath: str) -> None:
        self.url = url
        self.is_headless = is_headless
        self.to_exclude = to_exclude
        self.timeout_in_seconds = timeout_in_seconds
        self.content_xpath = content_xpath
        self.no_content_xpath = no_content_xpath

    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-positional-arguments

    def to_dict(self):
        """returns dictionary representation of dto"""
        return self.__dict__

    @classmethod
    def from_dict(cls, dict_obj):
        """creates new instance from dictionary"""
        return cls(**dict_obj)
