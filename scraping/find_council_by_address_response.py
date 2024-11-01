"""DTO for Find Council By Address"""


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
class FindCouncilByAddressResponse:
    """DTO for Find Council By Address"""

    def __init__(
        self,
        address: str,
        council_name: str,
        electoral_ward: str,
        text: str,
        has_error: bool,
        error_message: str,
    ) -> None:
        self.address = address
        self.council_name = council_name
        self.electoral_ward = electoral_ward
        self.text = text
        self.has_error = has_error
        self.error_message = error_message


# pylint: enable=too-few-public-methods
# pylint: enable=too-many-arguments
# pylint: enable=too-many-positional-arguments
