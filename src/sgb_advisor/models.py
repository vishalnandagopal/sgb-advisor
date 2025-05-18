from datetime import date


class SGB:
    """A class that holds all necessary info to do or calculate anything with an SGB"""

    __slots__ = {
        "nse_symbol",
        "ltp",
        "issue_price",
        "interest_rate",
        "maturity_date",
        "xirr",
    }

    def __init__(
        self,
        nse_symbol: str,
        ltp: float | int,
        issue_price: float | int,
        interest_rate: float | int,
        maturity_date: date,
    ):
        """
        Initialize an SGB class

        Parameters
        ----------
        nse_symboL : str
            Ticker on the National Stock Exchange
        ltp : float | int
            Last traded price on NSE
        issue_price : float | int
            Price at which RBI has issued the bond. The interest is calculated on this.
        interest_rate : float | int
            The rate of interest on the bond, paid on self.issue_price
        maturity_date: datetime.date
            The date of maturity of the bond

        Returns
        -------
        SGB object

        Examples
        --------
        >>> SGB(
        ...     "SGBSEP27",
        ...     7900.02,
        ...     5400,
        ...     datetime.date(2020, 9, 1),
        ... )
        SGB_Object


        """
        self.nse_symbol = nse_symbol
        """Ticker on the National Stock Exchange"""

        self.ltp = ltp
        """Last traded price on NSE"""

        self.issue_price = issue_price
        """Price at which RBI has issued the bond. The interest is calculated on this."""

        self.interest_rate = interest_rate
        """The rate of interest on the bond, paid on self.issue_price. 2.75% for older bonds, 2.5% for the newer ones"""

        self.maturity_date = maturity_date
        """The date of maturity of the bond"""

        self.xirr: float = 0
        """XIRR which can be calculated and set later"""

    def __str__(self) -> str:
        """
        Returns the string representation of the SGB object

        Parameters
        ----------
        None

        Returns
        -------
        str : String representation of the SGB object

        Examples
        --------
        >>> SGB.__str__()
        "SGBSEP27 - Issued at ₹5400 - LTP ₹7900.02 - 2.5% interest - 2024-09-01"
        """
        return f"{self.nse_symbol} - Issued at ₹{self.issue_price} - LTP ₹{self.ltp} - {self.interest_rate}% interest - {self.maturity_date}"

    def __repr__(self) -> str:
        """Look at SGB.__str__"""
        return f"<SGB [{str(self)}]>"

    def to_dict(self) -> dict[str, float | int | str]:
        return {
            "nse_symbol": self.nse_symbol,
            "ltp": self.ltp,
            "issue_price": self.issue_price,
            "interest_rate": self.interest_rate,
            "maturity_date": str(self.maturity_date),
            "xirr": self.xirr,
        }
