from datetime import date


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

        self.xirr: float = 0
        """XIRR which will be calculated and set later"""

    def __str__(self) -> str:
        return f"{self.nse_symbol} - Issue Price ₹{self.issue_price} - LTP ₹{self.ltp} - {self.interest_rate}% interest - {self.maturity_date}"

    def __repr__(self) -> str:
        return str(self)
