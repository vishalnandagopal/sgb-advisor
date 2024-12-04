from os import getenv

from ..logger import logger
from ..models import SGB
from .common import write_html_output as write_html_output
from .email_sender import send_mail as send_mail
from .teleg import create_and_send_message, validate_telegram_envs


def notify(sgbs: list[SGB]) -> None:
    """
    Tries to guess which channel(s) to notify the user through. Reads the "MODE" environment variable first. If empty, it tries to guess it by reading other environment variables like TELEGRAM_BOT_TOKEN and AWS_ACCESS_KEY

    Parameters
    ----------
    None

    Returns
    -------
    None

    Examples
    --------
    >>> notify(sgbs)
    True
    """

    MODE_OF_OPERATION: set[str] = guess_mode_of_notification()

    if "telegram" in MODE_OF_OPERATION:
        if not validate_telegram_envs() or not create_and_send_message(sgbs):
            logger.error("could not send message via telegram")
    if "email" in MODE_OF_OPERATION:
        if not send_mail(sgbs):
            logger.error("could not send email")


def guess_mode_of_notification() -> set[str]:
    """
    Tries to guess which channel(s) to notify the user through. Reads the "MODE" environment variable first. If empty, it tries to guess it by reading other environment variables like TELEGRAM_BOT_TOKEN and AWS_ACCESS_KEY

    Parameters
    ----------
    None

    Returns
    -------
    set[str]
        The channel(s) to which the notify the user through

    Examples
    --------
    >>> guess_mode_of_notification()
    {"telegram", "email"}
    """

    mode: set[str] = {getenv("SGB_MODE", "").casefold()}

    if "both" in mode:
        mode = {"email", "telegram"}

    if mode == {""}:
        mode.remove("")
        # Guessing mode by looking at which env variables are set. Telegram is checked first because it is the most likely to be set
        if getenv("SGB_TELEGRAM_BOT_TOKEN"):
            mode.add("telegram")
        if getenv("SGB_AWS_ACCESS_KEY"):
            mode.add("email")

    if not mode:
        msg: str = f'could not guess mode of operation . It is currently set as "{mode}". Output will only be written to file and not sent anywhere.'

        logger.error(msg)
        raise RuntimeError(msg)

    logger.info(f"Mode is current set to {mode}")

    return mode
