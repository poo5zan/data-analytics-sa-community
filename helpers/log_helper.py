from logging import Logger

def log_error(logger: Logger, caller_name: str, exception: Exception):
    logger.error(f"{caller_name} %s", exception, exc_info=True, stack_info=True)