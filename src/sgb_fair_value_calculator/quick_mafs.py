from calendar import monthrange
from datetime import date, datetime
from logging import info as log_info, error as log_error

from pyxirr import xirr

from .data import SGB


def calculate_sgb_xirr(sgb: SGB, current_gold_price: float):
    maturity = sgb.maturity_date
    today: date = datetime.now().date()

    payment_dates: list[date] = list()

    other_interest_payment_month: int = (
        maturity.month + 6 if maturity.month <= 6 else maturity.month - 6
    )

    for year, month in zip(
        range(today.year, maturity.year + 1),
        [other_interest_payment_month, maturity.month]
        * (maturity.year - today.year + 1),
    ):
        if maturity.day <= monthrange(year, month)[1]:
            day = maturity.day
        else:
            day = monthrange(year, month)[1]
        _date_to_check = datetime(year, month, day).date()
        if today < _date_to_check < maturity:
            payment_dates.append(_date_to_check)

    amounts = [sgb.issue_price * sgb.interest_rate / 100] * len(payment_dates)

    amounts.append(-sgb.ltp)
    payment_dates.append(today)
    amounts.append(current_gold_price)
    payment_dates.append(maturity)

    x: float | None = xirr(payment_dates, amounts)

    if not x:
        log_error(f"Couldn't calculate XIRR for {sgb.nse_symbol}")
        return 0

    log_info(f"Calculated XIRR of {sgb.nse_symbol} as {round(x,3)}")

    return round(x, 3)
