"""
Logger object for all files. Prints and writes logs to the file `sgb_advisor.log`
"""

from os import getenv

from loguru import logger as log

logger = log
logger.add("sgb_advisor.log")
log_level = getenv("SGB_LOG_LEVEL", "INFO").upper()
logger.level(log_level)
log.info(f"Log level set to {log_level}")
