"""dto for google analytics request config"""
class GoogleAnalyticsRequestConfig():
    """Request Config: dimensions and metrics"""

    def __init__(self, dimensions, metrics) -> None:
        self.dimensions = dimensions
        self.metrics = metrics

    def to_dict(self):
        """returns dictionary representation of dto"""
        return self.__dict__

    @classmethod
    def from_dict(cls, dict_obj):
        """creates new instance from dictionary"""
        return cls(**dict_obj)
