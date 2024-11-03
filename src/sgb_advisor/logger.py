"""
Logger object for all files. Prints and writes logs to the file `sgb_advisor.log`
"""

from loguru import logger as log

logger = log
logger.add("sgb_advisor.log")
