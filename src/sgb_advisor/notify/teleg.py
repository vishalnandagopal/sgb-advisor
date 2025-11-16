"""
Send messages and files using the Telegram API
"""

from json import dumps as json_dumps
from json import loads as json_loads
from os import getenv
from pathlib import Path

from playwright.sync_api import sync_playwright
from requests import get as r_get
from requests import post as r_post

from ..data import get_price_of_gold
from ..logg import logger
from ..models import SGB
from .common import get_ist_time, get_temp_file_path, write_html_output

TELEGRAM_BOT_TOKEN_ENV = "SGB_TELEGRAM_BOT_TOKEN"
TELEGRAM_BOT_TOKEN = getenv(TELEGRAM_BOT_TOKEN_ENV, "")
"""Telegram bot token. Get it from [BotFather](https://t.me/BotFather) on Telegram"""


TELEGRAM_CHAT_IDS: list[str] = getenv("SGB_TELEGRAM_CHAT_IDS", "").split(",")
"""Unique identifier for the target chat or username of the target channel (in the format @channelusername)"""


API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
"""The API URL to use, pre-configured with the bot token"""

RESERVED_CHARACTERS = {
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
}
# Characters that must be escaped before using it in a MarkdownV2 style message - https://core.telegram.org/bots/api#markdownv2-style


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
        logger.debug(
            f'telegram bot is be authenticated and running at "@{response["result"]["username"]}"'
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
    >>> check_chat_ids(
    ...     [
    ...         1234567,
    ...     ]
    ... )
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
            logger.debug(
                f'chat ID {chat_id} is valid and corresponds to username "@{response["result"]["username"]}".'
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
    return test_bot_status() and check_chat_ids()


def escape_reserved_characters(msg: str) -> str:
    """
    Escapes characters that are reserved in the telegram API

    Parameters
    ----------
    msg: str
        The message to process

    Returns
    -------
    str
        The message with reserved characters escaped

    Examples
    --------
    >>> escape_reserved_characters("test.")
    "test\\."
    """
    for char in RESERVED_CHARACTERS:
        msg = msg.replace(char, f"\\{char}", -1)
    return msg


def create_and_send_message(
    sgbs: list[SGB],
    chat_ids: list[str] = TELEGRAM_CHAT_IDS,
) -> None:
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
    None

    Examples
    --------
    >>> create_and_send_message(
    ...     sgbs,
    ...     [
    ...         123456789,
    ...     ],
    ... )
    None
    """

    photo_path: Path = generate_screenshot_of_html(sgbs)
    caption: str = get_telegram_caption(sgbs)
    send_message_with_files(
        files=[photo_path, get_json_file(sgbs)],
        photo_captions=[caption, ""],
        chat_ids=chat_ids,
    )


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
    None

    Examples
    --------
    >>> send_telegram_message(
    ...     "test",
    ...     123456789,
    ... )
    None
    """

    API_METHOD = "sendMessage"

    message_content = escape_reserved_characters(message_content)

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
            logger.debug(
                f"succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
            )

    if not success:
        logger.warning("could not send message to all chat IDs")
    else:
        logger.info(f"message sent to all chat IDs: {', '.join(chat_ids)}")
    return success


def send_message_with_files(
    files: list[Path],
    photo_captions: list[str] | str,
    chat_ids: list[str] = TELEGRAM_CHAT_IDS,
) -> None:
    """
    Sends a message with a photo on Telegram

    Parameters
    ----------
    files : list[Path]
        The files to send to every chat_id. Sent as individual messages
    photo_captions : list[str]
        The captions for every file. If the length of the captions list is not the same as the length of the files list, then the first caption is used for every file
    chat_ids : list[str]
        List of unique identifiers for the target chat or username of the target channel (in the format @channelusername)


    Returns
    -------
    None

    Examples
    --------
    >>> send_message_with_photo(
    ...     sgbs,
    ...     "telegram.png",
    ...     123456789,
    ... )
    None
    """

    # Sending as document to preserve quality
    API_METHOD = "sendDocument"

    success = True

    if len(photo_captions) != len(files):
        photo_captions = [photo_captions[0] * len(files)]

    for file, caption in zip(files, photo_captions):
        caption = escape_reserved_characters(caption)
        file_id = ""
        if file.suffix not in [".png", ".json"]:
            msg = f'Only json and png files are allowed. "{file.suffix}" format not allowed.'
            logger.error(msg)
            raise ValueError(msg)

        file_mime_type: str = "application/octet-stream"

        if file.suffix == ".png":
            file_mime_type = "image/png"
        elif file.suffix == ".json":
            file_mime_type = "application/json"

        for chat_id in chat_ids:
            request_body = {
                "caption": caption,
                "chat_id": chat_id,
                "parse_mode": "MarkdownV2",
            }

            if not file_id:
                document = (
                    file.stem + file.suffix,
                    open(file, "rb"),
                    file_mime_type,
                    {"Expires": "0"},
                )

                response = json_loads(
                    r_post(
                        f"{API_URL}/{API_METHOD}",
                        data=request_body,
                        files={"document": document},
                    ).text
                )
            else:
                request_body["document"] = file_id

                response = json_loads(
                    r_post(
                        f"{API_URL}/{API_METHOD}",
                        data=request_body,
                    ).text
                )

            if not response["ok"]:
                logger.error(
                    f"could not sent message to {chat_id}. Error - {response['description']}"
                )
                success = False

            else:
                logger.debug(
                    f"succesfully sent message to @{response['result']['chat']['username']} with message_id {response['result']['message_id']}"
                )
                if not file_id:
                    file_id = response["result"]["document"]["file_id"]

    if not success:
        logger.warning("could not send message to all chat IDs")
    else:
        logger.info("message sent to all chat IDs")


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

    html_file_path = write_html_output(sgbs)

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.goto(f"file://{html_file_path}")

        logger.debug(f"taking screenshot of html file at {html_file_path}")

        photo_path = get_temp_file_path("png")

        page.locator("#sgb-returns-table").screenshot(path=photo_path)

        logger.info(f"saved screnshot to {photo_path}")

        return photo_path


def get_telegram_caption(sgbs: list[SGB], n: int = 3) -> str:
    """
    Returns a caption for the telegram post

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
        text += f"\n\n`{sgb.nse_symbol}` - ₹{sgb.ltp} - {sgb.xirr}%"

    disclaimer_text = "\n[Disclaimers](https://github.com/vishalnandagopal/sgb-advisor/blob/master/README.md#disclaimers)"

    gold_price_text = f"\nGold price - ₹{get_price_of_gold()}"

    text += gold_price_text + disclaimer_text

    return text


def get_json_file(sgbs: list[SGB]) -> Path:
    json_path = get_temp_file_path("json")

    with open(json_path, "w") as f:
        f.write(get_json_representation(sgbs))

    logger.info(f"saved json to {json_path}")

    return json_path


def get_json_representation(sgbs: list[SGB]) -> str:
    d = {
        "time": str(get_ist_time()),
        "gold_price": get_price_of_gold(),
        "disclaimer": "https://github.com/vishalnandagopal/sgb-advisor/blob/master/README.md#disclaimers",
        "sgbs": [sgb.to_dict() for sgb in sgbs],
    }
    return json_dumps(d, indent=None)
