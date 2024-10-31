"""
Use this to send messages and photos (as documents) using Telegram API
"""

from datetime import datetime
from json import loads as json_loads
from os import getenv

from playwright.sync_api import sync_playwright
from requests import get as r_get
from requests import post as r_post

from ..logger import logger
from ..models import SGB
from .common import get_temp_file_path, write_table_html_to_file

TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "")
"""Telegram bot token. Get it from [BotFather](https://t.me/BotFather) on Telegram"""


TELEGRAM_CHAT_ID: int | str = getenv("TELEGRAM_CHAT_ID", 0)
"""Unique identifier for the target chat or username of the target channel (in the format @channelusername)"""


API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
"""The API URL to use, pre-configured with the bot token"""


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
            f'telegram bot is be authenticated and running at "@{response['result']['username']}"'
        )
        return True

    logger.error(
        f"telegram bot not able to authenticate. Error - {response['description']}"
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
            f'chat ID is valid and corresponds to username "@{response["result"]["username"]}".'
        )
        return True

    logger.error(
        f"could not find chat corresponding to chat_id - {chat_id}. Error - {response['description']}"
    )
    return False


def validate_telegram_envs() -> bool:
    return all((test_bot_status(), check_chat_id()))


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

    photo_path: str = generate_screenshot_of_html(sgbs=sgb_list)
    caption: str = get_top_3_sgbs_text(sgbs=sgb_list)
    return send_message_with_photo(caption, photo_path, TELEGRAM_CHAT_ID)


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
            f"succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
        )
        return True

    logger.error(
        f"could not sent message to {chat_id}. Error - {response['description']}"
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

    # Sending as document to preserve quality
    API_METHOD = "sendDocument"

    request_body = {
        "caption": photo_caption,
        "chat_id": chat_id,
        "parse_mode": "MarkdownV2",
    }

    photo_extension = photo_path.split(".")[-1]

    if photo_extension not in ["png"]:
        msg = f"photos of {photo_extension} format not allowed. Only png is supported"
        logger.error(msg)
        raise ValueError(msg)

    files = {
        "document": (
            f"{datetime.now().date()}.png",
            open(photo_path, "rb"),
            "image/.png",
            {"Expires": "0"},
        )
    }

    response = json_loads(
        r_post(f"{API_URL}/{API_METHOD}", data=request_body, files=files).text
    )

    if response["ok"]:
        logger.info(
            f"succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
        )
        return True

    logger.error(
        f"sould not sent message to {chat_id}. Error - {response['description']}"
    )
    return False


def generate_screenshot_of_html(sgbs: list[SGB]) -> str:
    html_file_path = write_table_html_to_file(sgbs)

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.goto(f"file://{html_file_path}")

        logger.info(f"taking screenshot of html file at {html_file_path}")

        photo_path = get_temp_file_path(".png")

        page.locator("#sgb-returns-table").screenshot(path=photo_path)

        logger.info(f"saved screnshot to {photo_path}")

        return photo_path


def get_top_3_sgbs_text(sgbs: list[SGB]):
    text = "Top 3 SGBs are: "

    for sgb in sgbs[:3]:
        # Replacing . in XIRR  with \. since . is reserved for some reason in the markdown mode in Telegram API
        text += f"\n\n`{sgb.nse_symbol}` \\- ₹{str(sgb.issue_price).replace(".","\\.")} \\- {str(sgb.xirr).replace(".","\\.")}%"

    return text
