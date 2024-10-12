from csv import reader as csv_reader
from datetime import datetime
from functools import lru_cache
from os.path import dirname

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from typing_extensions import TypeIs

from .logger import logging
from .models import SGB
from .quick_mafs import calculate_sgb_xirr

NSE_SGB_URL: str = "https://www.nseindia.com/market-data/sovereign-gold-bond"


def read_scrips_file() -> list[list[str]]:
    """Returns scrips.csv which is of the format

    Symbol NSE,Symbol BSE,Interest per annum,Interest payment dates,Maturity Date,Issue price
    """
    # File is taken from TradingQnA - https://tradingqna.com/t/interest-payment-dates-for-sovereign-gold-bonds-sgbs/145120

    with open(dirname(__file__) + "/assets/scrips.csv") as f:
        csv_contents = csv_reader(f, delimiter=",")
        return list(csv_contents)


@lru_cache(maxsize=None)
def get_sgbs() -> list[SGB]:
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()

        page.goto(NSE_SGB_URL, timeout=100000)

        SGBLTP_QUERY_SEL = "#sgbTable > tbody > tr > td:nth-child(7)"
        SGBNAME_QUERY_SEL = "#sgbTable > tbody > tr > td:nth-child(1)"

        # NSE website loads info after page load. So wait for this to appear
        try:
            page.wait_for_selector(SGBLTP_QUERY_SEL, timeout=100000)
        except PlaywrightTimeoutError:
            # Sometimes it fails but succeeds on 2nd try.
            logging.warning(
                "Failed to fetch SGB info from NSE site when trying for the first time. Trying again"
            )
            try:
                page.wait_for_selector(SGBLTP_QUERY_SEL, timeout=200000)
            except PlaywrightTimeoutError:
                # If it fails again we are letting it
                logging.error("Could not fetch SGBs info from NSE site")
                exit()

        sgb_ltp_results = page.query_selector_all(selector=SGBLTP_QUERY_SEL)
        sgb_name_results = page.query_selector_all(selector=SGBNAME_QUERY_SEL)

        def valid_sgb_checker(to_check: str | None) -> TypeIs[str]:
            if to_check:
                return to_check.startswith("SGB")
            return False

        _sgb_values_str: map[str] = map(
            lambda x: x.replace(",", ""),
            filter(None, map(lambda x: x.text_content(), sgb_ltp_results)),
        )

        _sgb_names_str: filter[str] = filter(
            valid_sgb_checker,
            map(lambda x: x.text_content(), sgb_name_results),
        )

        sgbs_trading: list[SGB] = list()

        csv_contents = read_scrips_file()

        for name, price in zip(_sgb_names_str, _sgb_values_str):
            try:
                row = list(filter(lambda x: x[0].strip() == name, csv_contents))[0]
                _issue_date = list(map(int, row[4].split("/")))
                sgbs_trading.append(
                    SGB(
                        row[0],
                        float(price),
                        float(row[5]),
                        float(row[2].replace("%", "").strip()),
                        datetime(_issue_date[2], _issue_date[1], _issue_date[0]).date(),
                    )
                )

            except Exception as e:
                print(f'Couldn\'t add "{name}" to sgb_values - {e}')

        browser.close()

    logging.info(f'Fetched all SGB data from NSE website. Sample - "{sgbs_trading[0]}"')

    for sgb in sgbs_trading:
        sgb.xirr = calculate_sgb_xirr(sgb, current_gold_price)

    # Sorts in descending order of XIRR
    sgbs_trading.sort(key=lambda x: x.xirr, reverse=True)

    return sgbs_trading


@lru_cache(maxsize=None)
def get_price_of_gold() -> float:
    # RBI uses IBJA
    IBJA_URL = "https://www.ibja.co/"

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()

        page.goto(IBJA_URL, timeout=100000)

        FINE_GOLD_PRICE_QUERY_SEL = "#lblFineGold999"

        try:
            page.wait_for_selector(FINE_GOLD_PRICE_QUERY_SEL, timeout=100000)
        except PlaywrightTimeoutError:
            page.wait_for_selector(FINE_GOLD_PRICE_QUERY_SEL, timeout=200000)

        _gold_price_element = page.query_selector(selector=FINE_GOLD_PRICE_QUERY_SEL)

        _gold_price_str = (
            _gold_price_element.text_content() if _gold_price_element else ""
        )

        browser.close()

    gold_price = (
        float(_gold_price_str.replace("₹", "").strip()) if _gold_price_str else -1
    )
    logging.info(f"Fetched price of gold from IBJA as {gold_price}")
    return gold_price


current_gold_price = get_price_of_gold()
