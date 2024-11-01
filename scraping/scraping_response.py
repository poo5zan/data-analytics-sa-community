"""
Data transfer object for Scraping Response
"""


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
class ScrapingResponse:
    """
    Data transfer object for Scraping Response
    """

    def __init__(
        self,
        url: str,
        response_code: int,
        page_content: str,
        error_name: str,
        error_message: str,
    ) -> None:
        self.url = url
        self.response_code = response_code
        self.page_content = page_content
        self.error_name = error_name
        self.error_message = error_message


# pylint: enable=too-few-public-methods
# pylint: enable=too-many-arguments
# pylint: enable=too-many-positional-arguments
