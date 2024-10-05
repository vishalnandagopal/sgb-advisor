from datetime import date, datetime
from pyxirr import xirr

from .data import SGB


def calculate_sgb_xirr(sgb: SGB):
    maturity = sgb.maturity_date
    today: date = datetime.now().date()

    interest_dates: list[date] = list()

    other_interest_payment_month: int = (
        maturity.month + 6 if maturity.month <= 6 else maturity.month - 6
    )

    for year, month in zip(
        range(today.year, maturity.year + 1),
        [other_interest_payment_month, maturity.month]
        * (maturity.year - today.year + 1),
    ):
        _date_to_check = datetime(maturity.day, month, year).date()
        if today < _date_to_check < maturity:
            interest_dates.append(_date_to_check)

    print(interest_dates)

    interest_amounts = [sgb.issue_price * sgb.interest_rate / 100] * len(interest_dates)

    return xirr(interest_dates, interest_amounts)
