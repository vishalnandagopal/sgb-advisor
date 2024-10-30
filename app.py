from dotenv import load_dotenv

load_dotenv(".env")

from os import getenv

from src.sgb_advisor import get_sgbs, logger, notify

all_sgbs = get_sgbs()

notify(all_sgbs)
