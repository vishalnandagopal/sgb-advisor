from os import getenv

from ..logger import logger
from ..models import SGB
from .common import write_table_html_to_file as write_table_html_to_file
from .email_sender import send_email as send_email
from .teleg import create_and_send_message, validate_telegram_envs


def notify(sgbs: list[SGB]) -> bool:
    """
    Tries to guess which channel(s) to notify the user through. Reads the "MODE" environment variable first. If empty, it tries to guess it by reading other environment variables like TELEGRAM_BOT_TOKEN and AWS_ACCESS_KEY

    Parameters
    ----------
    None

    Returns
    -------
    bool
        True if all modes of notification were successful. False if even one of the set modes fails

    Examples
    --------
    >>> notify(sgbs)
    True
    """

    MODE_OF_OPERATION: tuple[str, ...] = guess_mode_of_notification()

    success = True

    if "telegram" in MODE_OF_OPERATION:
        if not validate_telegram_envs() or not create_and_send_message(sgbs):
            success = False
    if "email" in MODE_OF_OPERATION:
        if not send_email(sgbs):
            success = False

    return success


def guess_mode_of_notification() -> tuple[str, ...]:
    """
    Tries to guess which channel(s) to notify the user through. Reads the "MODE" environment variable first. If empty, it tries to guess it by reading other environment variables like TELEGRAM_BOT_TOKEN and AWS_ACCESS_KEY

    Parameters
    ----------
    None

    Returns
    -------
    tuple[str, ...]
        The channel(s) to which the notify the user through

    Examples
    --------
    >>> guess_mode_of_notification()
    ("telegram", "email")
    """

    mode: tuple[str, ...] = (getenv("MODE", "").casefold(),)

    if mode == ("both",):
        mode = ("email", "telegram")

    if not mode:
        # Guessing mode by looking at which env variables are set. Telegram is checked first because it is the most likely to be set
        if getenv("TELEGRAM_BOT_TOKEN"):
            mode = ("telegram",)
        elif getenv("AWS_ACCESS_KEY"):
            mode = ("email",)

    if not mode:
        msg: str = (
            f'could not guess mode of operation. It is currently set as "{mode}"?'
        )
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info(f'mode of operation is set to "{mode}"')

    return mode
