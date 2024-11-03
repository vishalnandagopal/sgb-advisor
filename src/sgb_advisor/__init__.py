"""
A tool to analyse Sovereign Gold Bonds and compare their yields.
"""

from .data import get_price_of_gold as get_price_of_gold
from .data import get_sgbs as get_sgbs
from .logger import logger as logger
from .notify import notify as notify
from .quick_mafs import calculate_sgb_xirr as calculate_sgb_xirr
