"""
Logging helper methods
"""

from logging import Logger


def log_error(logger: Logger, caller_name: str, exception: Exception):
    """
    Logs error with details of exception
    """
    logger.error(f"{caller_name} %s", exception, exc_info=True, stack_info=True)
