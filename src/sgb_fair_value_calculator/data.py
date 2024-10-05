from csv import reader as csv_reader
from datetime import date, datetime
from os.path import dirname

from playwright.sync_api import sync_playwright
from typing_extensions import TypeIs


class SGB:
    def __init__(
        self,
        nse_symbol: str,
        ltp: float,
        issue_price: float | int,
        interest_rate: float,
        maturity_date: date,
    ):
        self.nse_symbol = nse_symbol
        """Symbol with which it trades on NSE"""

        self.ltp = ltp
        """Last traded price, parsed from the URL given in NSE_SGB_URL"""

        self.issue_price = issue_price
        """Price at which RBI issued the bond. Used to calculate interest that will be paid"""

        self.interest_rate = interest_rate
        """Fixed interest rate paid twice a year. 2.75% for older bonds, 2.5% for the newer ones"""

        self.maturity_date = maturity_date
        """The date on which the bond will mature. Used for calculating XIRR"""

    def __str__(self) -> str:
        return f"{self.nse_symbol} - Issue Price ₹{self.issue_price} - LTP ₹{self.ltp} - {self.interest_rate}% interest - {self.maturity_date}"

    def __repr__(self) -> str:
        return str(self)


def read_scrips_file() -> list[list[str]]:
    """Returns scrips.csv which is of the format

    Symbol NSE,Symbol BSE,Interest per annum,Interest payment dates,Maturity Date,Issue price
    """
    # File is taken from TradingQnA - https://tradingqna.com/t/interest-payment-dates-for-sovereign-gold-bonds-sgbs/145120

    with open(dirname(__file__) + "/assets/scrips.csv") as f:
        csv_contents = csv_reader(f, delimiter=",")
        return list(csv_contents)


def get_sgbs() -> list[SGB]:
    NSE_SGB_URL: str = "https://www.nseindia.com/market-data/sovereign-gold-bond"

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()

        page.goto(NSE_SGB_URL, timeout=100000)

        SGBLTP_QUERY_SEL = "#sgbTable > tbody > tr > td:nth-child(7)"
        SGBNAME_QUERY_SEL = "#sgbTable > tbody > tr > td:nth-child(1)"

        # NSE website loads info after page load. So wait for this to appear
        page.wait_for_selector(SGBLTP_QUERY_SEL)

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

                ...
            except Exception as e:
                print(f'Couldn\'t add "{name}" to sgb_values - {e}')

        browser.close()

    return sgbs_trading


def get_price_of_gold() -> float:
    # RBI uses IBJA
    IBJA_URL = "https://www.ibja.co/"

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()

        page.goto(IBJA_URL, timeout=100000)

        FINE_GOLD_PRICE_QUERY_SEL = "#lblFineGold999"

        page.wait_for_selector(FINE_GOLD_PRICE_QUERY_SEL)

        _gold_price_element = page.query_selector(selector=FINE_GOLD_PRICE_QUERY_SEL)

        _gold_price_str = (
            _gold_price_element.text_content() if _gold_price_element else ""
        )

        browser.close()

    return float(_gold_price_str.replace("₹", "").strip()) if _gold_price_str else -1
