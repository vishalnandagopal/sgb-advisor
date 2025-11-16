from csv import reader as csv_reader
from datetime import datetime
from functools import lru_cache
from os import getenv
from os.path import dirname
from typing import Optional

from playwright.sync_api import ElementHandle
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .logg import logger
from .models import SGB
from .quick_mafs import calculate_sgb_xirr

NSE_SGB_URL = "https://www.nseindia.com/market-data/sovereign-gold-bond"

# RBI uses IBJA
IBJA_URL = "https://www.ibja.co/"
IBJA_BACKUP_URL = "https://ibjarates.com/"


class SiteNotLoadedError(PlaywrightTimeoutError):
    """
    Separate error class to use when site doesn't load, to avoid catching other types of errors. The NSE site fails to load a lot of times
    """

    def __init__(self, message):
        super().__init__(message)


def read_scrips_file() -> list[list[str]]:
    """
    Returns scrips.csv which is of the format

    Paramters
    ---------
    None

    Returns
    -------
    list[list[str]]
        Returns a list of rows in the CSV, with the format "Symbol NSE,Symbol BSE,Interest per annum,Interest payment dates,Maturity Date,Issue price"

    Examples
    --------
    >>> read_scrips_file()
    [
        [
            "Symbol NSE,Symbol BSE,Interest per annum,Interest payment dates,Maturity Date,Issue price"
        ],
        [
            "SGBMAR24", "SGB2016II", "2.75%", "29th March and September", "29/03/2024", "2916"
        ],
    ]

    File is taken from [TradingQnA](https://tradingqna.com/t/interest-payment-dates-for-sovereign-gold-bonds-sgbs/145120)
    """
    with open(dirname(__file__) + "/assets/scrips.csv") as f:
        csv_contents = csv_reader(f, delimiter=",")
        return list(csv_contents)


@lru_cache(maxsize=None)
def run_in_headless_mode() -> bool:
    """
    Returns whether the script should run in headless mode or not. Uses the SGB_HEADED_MODE environment variable to determine this.

    Parameters
    ----------
    None

    Returns
    -------
    bool
        `True` if the script should run in headless mode, `False` otherwise. Defaults to `True`.

    Examples
    --------
    >>> run_in_headless_mode()
    True
    """
    headed_mode = getenv("SGB_HEADED_MODE", "false").casefold() == "true"
    logger.debug(
        "Running playwright in headed mode"
        if {headed_mode}
        else "Running playwright in headless mode"
    )
    # opposite to return headless mode state
    return not headed_mode


def get_sgbs_from_nse_site(n_th: Optional[int] = 1) -> list[SGB]:
    """
    Fetch info for SGBs located at NSE_SGB_URL. Uses the [playwright](https://playwright.dev/python/) library.

    Parameters
    ----------
    n_th : Optional[int]
        The nth try going on. Used to print along with the logs. Defaults to 1

    Returns
    -------
    list[SGB]
        list of SGBs

    Examples
    --------
    >>> get_sgbs_from_nse_site(1)
    [SGB1, SGB2]
    """
    with sync_playwright() as p:
        # Was firefox before, but NSE website is very buggy with it
        browser = p.firefox.launch(headless=run_in_headless_mode())
        page = browser.new_page()
        current_user_agent: str = page.evaluate("navigator.userAgent")
        new_user_agent = current_user_agent.replace("Headless", "")
        if new_user_agent != current_user_agent:
            page.close()
            logger.info(f"Setting new user agent to {new_user_agent}")
            page = browser.new_page(user_agent=new_user_agent)
        logger.info(f"fetching NSE SGB page at {NSE_SGB_URL} - {n_th} time(s)")

        # For some weird ass reason, NSE website fails to load half the times if playwright opens it immediately after the browser has opened. Loading a URL first and after that switching to NSE site since it improves loading?
        # This could also be a firefox issue
        page.goto("https://www.vishalnandagopal.com")
        page.goto(NSE_SGB_URL, timeout=10000)

        SGBNAME_QUERY_SEL = "#sgbTable > tbody > tr > td:nth-child(1)"
        SGBLTP_QUERY_SEL = "#sgbTable > tbody > tr > td:nth-child(7)"
        SGBVOL_QUERY_SEL = "#sgbTable > tbody > tr > td:nth-child(11)"

        # NSE website loads info after page load. So wait for this to appear
        try:
            page.wait_for_selector(SGBLTP_QUERY_SEL, timeout=10000)
        except PlaywrightTimeoutError:
            msg: str = (
                f"could not fetch SGBs info from NSE site - tried {n_th} times(s)"
            )
            logger.warning(msg)
            raise SiteNotLoadedError(msg)

        sgb_ltp_results = page.query_selector_all(selector=SGBLTP_QUERY_SEL)
        sgb_name_results = page.query_selector_all(selector=SGBNAME_QUERY_SEL)
        sgb_volume_results = page.query_selector_all(selector=SGBVOL_QUERY_SEL)

        sgbs_trading: list[SGB] = list()

        csv_contents = read_scrips_file()

        name_element: ElementHandle
        price_element: ElementHandle
        volume_element: ElementHandle

        for name_element, price_element, volume_element in zip(
            sgb_name_results, sgb_ltp_results, sgb_volume_results
        ):
            try:
                name = name_element.text_content()
                price_str = price_element.text_content()
                volume_str = volume_element.text_content()
                if not (
                    (name and name.startswith("SGB"))
                    and (price_str)
                    and (volume_str and volume_str != "-")
                ):
                    continue

                row = list(filter(lambda x: x[0].strip() == name, csv_contents))[0]
                _issue_date = list(map(int, row[4].split("/")))
                if int(volume_str.replace(",", "")) > 0:
                    sgbs_trading.append(
                        SGB(
                            row[0],
                            float(price_str.replace(",", "")),
                            float(row[5]),
                            float(row[2].replace("%", "").strip()),
                            datetime(
                                _issue_date[2], _issue_date[1], _issue_date[0]
                            ).date(),
                        )
                    )

            except Exception as e:
                print(
                    f'Couldn\'t add "{name_element.text_content()}" to sgb_values - {e}'
                )

        browser.close()

    logger.info("fetched all SGB data from NSE website")
    logger.debug('sample SGB data from NSE- "{sgbs_trading[0]}"')
    return sgbs_trading


@lru_cache(maxsize=None)
def get_sgbs() -> list[SGB]:
    """
    Fetches the list of SGBs from the NSE site. Parent function to try until it succeeds, since the site is very unreliable. Tries a maximum of 10 times.

    Parameters
    ----------
    None

    Returns
    -------
    list[SGB]
        List of SGBs

    Examples
    --------
    >>> get_sgbs()
    [SGB1, SGB2, SGB3]
    """
    sgbs_trading: list[SGB] = list()
    i = 0
    # try till it succeeds?
    while not sgbs_trading and i < 10:
        i += 1
        try:
            sgbs_trading = get_sgbs_from_nse_site(i)
        except SiteNotLoadedError:
            pass

    if not sgbs_trading:
        msg = "could not fetch data from NSE website"
        logger.error(msg)
        raise RuntimeError(msg)

    current_gold_price: float = get_price_of_gold()

    for sgb in sgbs_trading:
        sgb.xirr = calculate_sgb_xirr(sgb, current_gold_price)

    # Sorts in descending order of XIRR
    sgbs_trading.sort(key=lambda x: x.xirr, reverse=True)

    return sgbs_trading


def fetch_price_of_gold_from_ibja(n_th: Optional[int] = 1) -> float:
    """
    Fetches the price of gold using the playwright library, from the site at IBJA_URL

    Parameters
    ----------
    n_th : Optional[int]
        The nth try going on. Used to print along with the logs. Defaults to 1

    Returns
    -------
    float
        The price of gold

    Examples
    --------
    >>> fetch_price_of_gold_from_ibja()
    7956.00
    """
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=run_in_headless_mode())
        page = browser.new_page(java_script_enabled=False)

        logger.info(f"fetching IBJA page at {IBJA_URL} - {n_th} time")
        page.goto(IBJA_URL, timeout=100000)

        FINE_GOLD_PRICE_QUERY_SEL = "#lblFineGold999"
        try:
            page.wait_for_selector(FINE_GOLD_PRICE_QUERY_SEL, timeout=50000)
        except PlaywrightTimeoutError:
            msg: str = (
                f"could not fetch price of gold from {IBJA_URL} - tried {n_th} times(s)"
            )
            logger.warning(msg)
            raise SiteNotLoadedError(msg)

        _gold_price_element = page.query_selector(selector=FINE_GOLD_PRICE_QUERY_SEL)

        _gold_price_str = (
            _gold_price_element.text_content() if _gold_price_element else ""
        )

        browser.close()

    gold_price = (
        float(_gold_price_str.replace("₹", "").strip()) if _gold_price_str else -1
    )
    return gold_price


def fetch_price_of_gold_from_ibja_backup(n_th: Optional[int] = 1) -> float:
    """
    Fetches the price of gold using the playwright library, from the site at IBJA_BACKUP_URL

    Parameters
    ----------
    n_th : Optional[int]
        The nth try going on. Used to print along with the logs. Defaults to 1

    Returns
    -------
    float
        The price of gold

    Examples
    --------
    >>> fetch_price_of_gold_from_ibja_backup()
    7956.00
    """
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=run_in_headless_mode())
        page = browser.new_page(java_script_enabled=False)

        logger.info(f"fetching IBJA page at {IBJA_BACKUP_URL} - {n_th} time")
        page.goto(IBJA_BACKUP_URL, timeout=100000)

        GOLD_PRICE_QUERY_SEL = "#GoldRatesCompare999"
        # No need to wait for selector since IBJA_BACKUP_URL returns the price in the inital HTML load itself
        # try:
        #     page.wait_for_selector(GOLD_PRICE_QUERY_SEL, timeout=50000)
        # except PlaywrightTimeoutError:
        #     msg: str = (
        #         f"could not fetch price from {IBJA_BACKUP_URL} - tried {n_th} times(s)"
        #     )
        #     logger.warning(msg)
        #     raise SiteNotLoadedError(msg)

        _gold_price_element = page.query_selector(selector=GOLD_PRICE_QUERY_SEL)

        _gold_price_str = (
            _gold_price_element.text_content() if _gold_price_element else ""
        )

        browser.close()

    gold_price = (
        float(_gold_price_str.replace("₹", "").strip()) if _gold_price_str else -1
    )
    return gold_price


@lru_cache(maxsize=None)
def get_price_of_gold() -> float:
    """
    Fetches the price of gold from the IBJA site. Parent function to try until it succeeds. Tries a maximum of 10 times.

    Parameters
    ----------
    None

    Returns
    -------
    float
        The price of gold

    Examples
    --------
    >>> get_price_of_gold()
    7956.00
    """

    gold_price: float = 0

    i = 0
    # try till it succeeds?
    while not gold_price and i < 10:
        i += 1
        try:
            gold_price = fetch_price_of_gold_from_ibja(i)
        except SiteNotLoadedError:
            try:
                gold_price = fetch_price_of_gold_from_ibja_backup(i)
            except SiteNotLoadedError:
                pass

    if not gold_price:
        msg = "could not fetch gold price from IBJA"
        logger.error(msg)
        raise RuntimeError(msg)

    logger.info(f"fetched price of gold from IBJA as {gold_price}")
    return gold_price
