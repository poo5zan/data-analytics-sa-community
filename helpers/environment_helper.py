"""
Environment Helper
"""

import os
from dotenv import load_dotenv


class EnvironmentHelper:
    """
    Environment helper
    """

    def __init__(self) -> None:
        load_dotenv()

    def get(self, key: str):
        """get the value of environment helper"""
        return os.environ.get(key)

    def get_or_default(self, key: str, default):
        """get the value of environment helper or return default"""
        return os.environ.get(key, default)
