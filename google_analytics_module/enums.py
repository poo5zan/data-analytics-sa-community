"""Enums"""
from enum import Enum


class GoogleAuthenticationMethod(Enum):
    """Authentication methods"""
    OAUTH = 1
    SERVICE_ACCOUNT = 2
