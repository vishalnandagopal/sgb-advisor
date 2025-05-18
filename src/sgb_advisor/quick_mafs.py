from calendar import monthrange
from datetime import date, datetime

from pyxirr import xirr

from .logg import logger
from .models import SGB


def calculate_sgb_xirr(sgb: SGB, current_gold_price: float) -> float:
    """
    Calculates the XIRR on an SGB. It assumes you are buying at the last traded price and that the RBI will redeem it only at the current price set by IBJA.

    Parameters
    ----------
    sgb : SGB
        The SGB object
    current_gold_price: float
        The price of gold

    Returns
    -------
    float
        Returns the calculated XIRR in percentage terms, rounded to 3 digits

    Examples
    --------
    >>> calculate_sgb_xirr(SGB_object, 7490)
    13.90
    """
    maturity = sgb.maturity_date
    today: date = datetime.now().date()

    payment_dates: list[date] = list()

    other_interest_payment_month: int = (
        maturity.month + 6 if maturity.month <= 6 else maturity.month - 6
    )

    for year, month in zip(
        # Iterating over the years and months of the interest payment dates
        range(today.year, maturity.year + 1),
        [other_interest_payment_month, maturity.month]
        * (maturity.year - today.year + 1),
    ):
        if maturity.day <= monthrange(year, month)[1]:
            day = maturity.day
        else:
            day = monthrange(year, month)[1]
        _date_to_check = datetime(year, month, day).date()
        # Final interest is paid on maturity, so checking <= for maturity
        if today < _date_to_check <= maturity:
            payment_dates.append(_date_to_check)

    amounts = [sgb.issue_price * sgb.interest_rate / 100] * len(payment_dates)

    # Since you are buying the bond now at it's LTP, the cashflow is negative as it is flowing out of your pocket.
    # Concept of true value does not come in here since you have already decided to buy the SGB, and the only choice is to buy it at it's current traded price.
    amounts.append(-sgb.ltp)
    payment_dates.append(today)

    # Assuming it will mature at the same price as today, which is it's true value, cashflow on that day will be positive since it is coming back into your wallet.
    # Concept of true value comes in here since RBI will only pay the you redemption price as per the price set by IBJA and not the price at which it is trading
    amounts.append(current_gold_price)
    payment_dates.append(maturity)

    # Thanks to the pyxirr module for making XIRR calculations really easy
    x: float | None = xirr(payment_dates, amounts)

    if not x:
        logger.error(f"couldn't calculate XIRR for {sgb.nse_symbol}")
        logger.debug(
            f"Dump for {sgb.nse_symbol}:-\npayment_dates : {payment_dates}\namounts : {amounts}"
        )
        return 0

    return round(x * 100, 3)
