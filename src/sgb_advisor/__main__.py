from os import getenv
from pathlib import Path

from dotenv import load_dotenv


def runner():
    # Need to load dotenv before importing/running any module file, since they use API keys from env modules
    SGB_ENV_FILE_PATH: Path = Path(
        getenv("SGB_ENV_FILE_PATH", str(Path.cwd() / ".env"))
    )
    load_dotenv(SGB_ENV_FILE_PATH)

    from .data import get_sgbs as get_sgbs
    from .logg import logger as logger
    from .notify import notify as notify

    if SGB_ENV_FILE_PATH.exists():
        logger.debug(f"Loaded environment variables from {SGB_ENV_FILE_PATH}")
    "Entry fuction for the script"

    sgbs = get_sgbs()
    notify(sgbs)


if __name__ == "__main__":
    runner()
