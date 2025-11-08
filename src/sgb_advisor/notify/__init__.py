from os import getenv

from ..logg import logger
from ..models import SGB
from .common import tmp_folder
from .email_sender import AWS_ACCESS_KEY_ENV, send_mail
from .teleg import (
    TELEGRAM_BOT_TOKEN_ENV,
    create_and_send_message,
    validate_telegram_envs,
)

SGB_MODE_ENV: str = "SGB_MODE"
TELEGRAM_MODE: str = "telegram"
EMAIL_MODE: str = "email"
BOTH_MODE: str = "both"
NONE_MODE: str = "none"


def notify(sgbs: list[SGB]) -> None:
    """
    Send notifications via all set modes.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Examples
    --------
    >>> notify(sgbs)
    None
    """

    MODE_OF_OPERATION: set[str] = guess_mode_of_notification()

    if NONE_MODE in MODE_OF_OPERATION:
        logger.info(
            f'not sending any notifications since mode is set to {NONE_MODE}. Output will only be written to the folder "{tmp_folder}".'
        )
        return

    if TELEGRAM_MODE in MODE_OF_OPERATION:
        if not validate_telegram_envs():
            err = "could not send message via telegram"
            logger.error(err)
            raise RuntimeError(err)
        create_and_send_message(sgbs)
    if EMAIL_MODE in MODE_OF_OPERATION:
        if not send_mail(sgbs):
            err = "could not send email via AWS SES"
            logger.error(err)
            raise RuntimeError(err)


def guess_mode_of_notification() -> set[str]:
    """
    Tries to guess which channel(s) to notify the user through. Reads the "MODE" environment variable first. If empty, it tries to guess it by reading other environment variables like TELEGRAM_BOT_TOKEN and AWS_ACCESS_KEY

    Parameters
    ----------
    None

    Returns
    -------
    set[str]
        The mode(s) to which the notify the user through

    Examples
    --------
    >>> guess_mode_of_notification()
    {"telegram", "email"}
    """

    mode: set[str] = set(getenv(SGB_MODE_ENV, "").casefold().split(","))

    if NONE_MODE in mode:
        mode = {NONE_MODE}
    elif BOTH_MODE in mode:
        mode = {EMAIL_MODE, TELEGRAM_MODE}
    elif mode == {""}:
        mode = set()
        # Guessing mode(s) by looking at which env variables are set
        if getenv(TELEGRAM_BOT_TOKEN_ENV):
            mode.add(TELEGRAM_MODE)
        if getenv(AWS_ACCESS_KEY_ENV):
            mode.add(EMAIL_MODE)
    elif EMAIL_MODE not in mode and TELEGRAM_MODE not in mode:
        mode = set()

    if not mode:
        msg: str = f"could not guess mode of operation. ENV {SGB_MODE_ENV} is set as {getenv(SGB_MODE_ENV)}"

        logger.error(msg)
        raise RuntimeError(msg)

    logger.info(f"SGB mode is current set to {mode}")

    return mode
