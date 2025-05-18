"""
Logger object for all files. Prints and writes logs to the file `sgb_advisor.log`
"""

from sys import stdout
from os import getenv

from loguru import logger

log_level = getenv("SGB_LOG_LEVEL", "INFO").upper() or "INFO"
logger.remove()
logger.level(log_level)
logger.add("sgb_advisor.log", level=log_level)
logger.add(stdout, level=log_level)
logger.debug(f"Log level set to {log_level}")
