"""Google analytics response dto"""
# pylint: disable=too-few-public-methods
class GoogleAnalyticsResponse():
    """DTO for google analytics response"""
    def __init__(self, page_token, total_results, results) -> None:
        self.page_token = page_token
        self.total_results = total_results
        self.results = results

# pylint: enable=too-few-public-methods
