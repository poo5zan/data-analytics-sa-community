import os
from dotenv import load_dotenv

class EnvironmentHelper():
    def __init__(self) -> None:
        load_dotenv()

    def get(self, key: str):
        return os.environ.get(key)
    
    def get_or_default(self, key: str, default):
        return os.environ.get(key, default)
