"""
Send messages and files using the Telegram API
"""

from json import loads as json_loads
from os import getenv
from pathlib import Path

from playwright.sync_api import sync_playwright
from requests import get as r_get
from requests import post as r_post

from ..logger import logger
from ..models import SGB
from .common import get_temp_file_path, write_table_html_to_file

TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "")
"""Telegram bot token. Get it from [BotFather](https://t.me/BotFather) on Telegram"""


TELEGRAM_CHAT_IDS: list[str] = getenv("TELEGRAM_CHAT_IDS", "0").split(",")
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
    bool
        True if successfully authenticated

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


def check_chat_ids(chat_ids: list[str] = TELEGRAM_CHAT_IDS) -> bool:
    """
    Checks if the chat ID given is valid.

    Parameters
    ----------
    chat_ids : list[str]
        Unique identifier for the target chat or username of the target channel (in the format @channelusername)

    Returns
    -------
    bool
        If the API returns it as a valid chat ID

    Examples
    --------
    >>> check_chat_ids([1234567,])
    True
    """
    API_METHOD = "getChat"

    success = True

    for chat_id in chat_ids:
        response = json_loads(r_get(f"{API_URL}/{API_METHOD}?chat_id={chat_id}").text)

        if not response["ok"]:
            success = False
            logger.error(
                f"could not find chat corresponding to chat_id - {chat_id}. Error - {response['description']}"
            )
        else:
            logger.info(
                f'chat ID is valid and corresponds to username "@{response["result"]["username"]}".'
            )

    return success


def validate_telegram_envs() -> bool:
    """
    Checks whether the env variables required for sending a message are both present and valid.

    Parameters
    ----------
    None

    Returns
    -------
    bool
        If succesfully validated

    Examples
    --------
    >>> validate_telegram_envs()
    True
    """
    return all((test_bot_status(), check_chat_ids()))


def create_and_send_message(
    sgb_list: list[SGB], chat_ids: list[str] = TELEGRAM_CHAT_IDS
) -> bool:
    """
    Creates a message with the given SGB list and sends it on Telegram

    Parameters
    ----------
    sgb_list : list[SGB]
        The list of SGBs to include in the message
    chat_ids : list[SGB]
        List of unique identifiers for the target chat or username of the target channel (in the format @channelusername)

    Returns
    -------
    bool : True if successful

    Examples
    --------
    >>> create_and_send_message(sgbs, [123456789,])
    True
    """

    photo_path: Path = generate_screenshot_of_html(sgbs=sgb_list)
    caption: str = get_top_n_sgbs_text(sgbs=sgb_list)
    return send_message_with_photo(caption, photo_path, chat_ids)


def send_message(message_content: str, chat_ids: list[str] = TELEGRAM_CHAT_IDS) -> bool:
    """
    Sends a message on Telegram with the given content and chat ID.


    Parameters
    ----------
    message_content : str
        The content of the message to be sent
    chat_ids : list[str]
        Unique identifier for the target chat or username of the target channel (in the format @channelusername)

    Returns
    -------
    bool
        True if the message was successfully sent to all chat IDs

    Examples
    --------
    >>> send_telegram_message("test", 123456789)
    True
    """

    API_METHOD = "sendMessage"

    success = True
    for chat_id in chat_ids:
        request_body = {
            "text": message_content,
            "chat_id": chat_id,
            "parse_mode": "MarkdownV2",
        }

        response = json_loads(r_post(f"{API_URL}/{API_METHOD}", data=request_body).text)

        if not response["ok"]:
            logger.error(
                f"could not sent message to {chat_id}. Error - {response['description']}"
            )
            success = False

        else:
            logger.info(
                f"succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
            )

    return success


def send_message_with_photo(
    photo_caption: str,
    photo_path: Path,
    chat_ids: list[str] = TELEGRAM_CHAT_IDS,
) -> bool:
    """
    Sends a message with a photo on Telegram

    Parameters
    ----------
    photo_caption : str
        The caption for the photo
    photo_path : str | Path
        The path to the photo to be sent
    chat_ids : list[str]
        List of unique identifiers for the target chat or username of the target channel (in the format @channelusername)


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

    success = True

    for chat_id in chat_ids:
        request_body = {
            "caption": photo_caption,
            "chat_id": chat_id,
            "parse_mode": "MarkdownV2",
        }

        if photo_path.suffix not in [".png"]:
            msg = f"photos of {photo_path.suffix} format not allowed. Only png is supported"
            logger.error(msg)
            raise ValueError(msg)

        files = {
            "document": (
                photo_path.stem + photo_path.suffix,
                open(photo_path, "rb"),
                "image/.png",
                {"Expires": "0"},
            )
        }

        response = json_loads(
            r_post(f"{API_URL}/{API_METHOD}", data=request_body, files=files).text
        )

        if not response["ok"]:
            logger.error(
                f"sould not sent message to {chat_id}. Error - {response['description']}"
            )
            success = False

        else:
            logger.info(
                f"succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
            )

    return success


def generate_screenshot_of_html(sgbs: list[SGB]) -> Path:
    """
    Given a list of SGBs, generates a screnshot of an HTML page showing their returns using the [playwright](https://playwright.dev/python/) library.

    Parameters
    ----------
    sgbs: list[SGB]
        List of SGBs

    Returns
    -------
    Path
        Screenshot path

    Examples
    --------
    >>> generate_screenshot_of_html(sgbs)
    Path("E:\\Code\\sgb_advisor\\tmp\\1730403483.2583637-9432.png")
    """

    html_file_path = write_table_html_to_file(sgbs)

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.goto(f"file://{html_file_path}")

        logger.info(f"taking screenshot of html file at {html_file_path}")

        photo_path = get_temp_file_path("png")

        page.locator("#sgb-returns-table").screenshot(path=photo_path)

        logger.info(f"saved screnshot to {photo_path}")

        return photo_path


def get_top_n_sgbs_text(sgbs: list[SGB], n: int = 3) -> str:
    """
    Get text with just top n SGBs.

    Parameters
    ----------
    sgbs : list[SGB]
        List of SGBs

    n : int
        The number of SGGs to generate text for (top n)

    Returns
    -------
    str
        Text showing data for top n SGBs

    Examples
    --------
    >>> get_top_n_sgbs_text(sgbs, 3)
    \"\"\"Top 3 SGBs are:\n
    SGBJUN31I - ₹5926.0 - 0.687%\n
    SGBAUG28V - ₹5334.0 - 0.558%\n
    SGBJU29III - ₹4889.0 - 0.556%\"\"\"
    """
    text = "Top 3 SGBs are: "

    for sgb in sgbs[:n]:
        # Replacing . in XIRR  with \. since . is reserved for some reason in the markdown mode in Telegram API
        text += f"\n\n`{sgb.nse_symbol}` \\- ₹{str(sgb.issue_price).replace(".","\\.")} \\- {str(sgb.xirr).replace(".","\\.")}%"

    text += (
        "\n[Disclaimers](https://github.com/vishalnandagopal/sgb-advisor/blob/master/README.md#disclaimers)"
    )

    return text
