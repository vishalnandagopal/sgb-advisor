from json import loads as json_loads
from os import getenv

from requests import get as r_get
from requests import post as r_post

from ..logger import logger
from ..models import SGB

TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "")
"""Telegram bot token. Get it from [BotFather](https://t.me/BotFather) on Telegram"""


TELEGRAM_CHAT_ID: int | str = getenv("TELEGRAM_CHAT_ID", 0)
"""Unique identifier for the target chat or username of the target channel (in the format @channelusername)"""


API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
"""The API URL to use, pre-configured with the bot token"""


def markdown_table(sgbs: list[SGB]): ...


def get_message_body(sgbs: list[SGB]): ...


def create_and_send_message(
    sgb_list: list[SGB], chat_id: int | str = TELEGRAM_CHAT_ID
) -> bool:
    """
    Creates a message with the given SGB list and sends it on Telegram

    Parameters
    ----------
    sgb_list : list[SGB]
        The list of SGBs to include in the message
    chat_id : int | str
        Unique identifier for the target chat or username of the target channel (in the format @channelusername)

    Returns
    -------
    bool : True if successful

    Examples
    --------
    >>> create_and_send_message(sgbs, 123456789)
    True
    """
    ...


def send_message(message_content: str, chat_id: int | str = TELEGRAM_CHAT_ID) -> bool:
    """
    Sends a message on Telegram with the given content and chat ID.


    Parameters
    ----------
    message_content : str
        The content of the message to be sent
    chat_id : int | str
        Unique identifier for the target chat or username of the target channel (in the format @channelusername)

    Returns
    -------
    bool
        True if the message was successfully sent

    Examples
    --------
    >>> send_telegram_message("test", 123456789)
    True
    """

    API_METHOD = "sendMessage"

    request_body = {
        "text": message_content,
        "chat_id": chat_id,
        "parse_mode": "MarkdownV2",
    }

    response = json_loads(r_post(f"{API_URL}/{API_METHOD}", data=request_body).text)

    if response["ok"]:
        logger.info(
            f"Succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
        )
        return True

    logger.error(
        f"Could not sent message to {chat_id}. Error - {response['description']}"
    )
    return False


def send_message_with_photo(
    photo_caption: str,
    photo_path: str,
    chat_id: int | str = TELEGRAM_CHAT_ID,
) -> bool:
    """
    Sends a message with a photo on Telegram

    Parameters
    ----------
    photo_caption : str
        The caption for the photo
    photo_path : str
        The path to the photo to be sent
    chat_id : int | str
        Unique identifier for the target chat or username of the target channel (in the format @channelusername)


    Returns
    -------
    bool : True if successful

    Examples
    --------
    >>> send_message_with_photo(sgbs, "telegram.png", 123456789)
    True
    """

    API_METHOD = "sendPhoto"

    request_body = {
        "caption": photo_caption,
        "chat_id": chat_id,
        "parse_mode": "MarkdownV2",
    }

    photo_extension = photo_path.split(".")[-1]
    if not photo_extension in ["png", "jpg", "jpeg"]:
        msg = f"Photos of {photo_extension} format not allowed. Only .png, .jpg and .jpeg are supported"
        logger.error(msg)
        raise ValueError(msg)

    files = {
        "photo": (
            "t.png",
            open(photo_path, "rb"),
            f"image/{photo_extension}",
            {"Expires": "0"},
        )
    }

    response = json_loads(
        r_post(f"{API_URL}/{API_METHOD}", data=request_body, files=files).text
    )

    if response["ok"]:
        logger.info(
            f"Succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
        )
        return True

    logger.error(
        f"Could not sent message to {chat_id}. Error - {response['description']}"
    )
    return False


def test_bot_status() -> bool:
    """
    Tests if the bot is properly configured and can authenticate with the Telegram bot server by calling the `getMe` method

    Parameters
    ----------
    None

    Returns
    -------
    bool : True if successfully authenticated

    Examples
    --------
    >>> test_bot_status()
    True
    """
    API_METHOD = "getMe"

    response = json_loads(r_get(f"{API_URL}/{API_METHOD}").text)

    if response["ok"]:
        logger.info(
            f'Telegram bot is be authenticated and running at "@{response['result']['username']}"'
        )
        return True

    logger.error(
        f"Telegram bot not able to authenticate. Error - {response['description']}"
    )
    return False


def check_chat_id(chat_id: int | str = TELEGRAM_CHAT_ID) -> bool:
    """
    Checks if the chat ID given is valid.

    Parameters
    ----------
    chat_id : int | str
        Unique identifier for the target chat or username of the target channel (in the format @channelusername)

    Returns
    -------
    bool
        If the API returns it as a valid chat ID
    """
    API_METHOD = "getChat"

    response = json_loads(r_get(f"{API_URL}/{API_METHOD}?chat_id={chat_id}").text)

    if response["ok"]:
        logger.info(
            f'Chat ID is valid and corresponds to username "@{response["result"]["username"]}".'
        )
        return True

    logger.error(
        f"Could not find chat corresponding to chat_id - {chat_id}. Error - {response['description']}"
    )
    return False


def validate_telegram_envs() -> bool:
    return all((test_bot_status(), check_chat_id()))
