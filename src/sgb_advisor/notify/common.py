"""
Commons functions that can be used by all methods of notifications
"""

from datetime import datetime, timedelta, timezone
from functools import lru_cache
from os import getenv
from os.path import dirname
from pathlib import Path
from random import randint
from tempfile import gettempdir
from typing import Optional

from ..data import get_price_of_gold
from ..logg import logger
from ..models import SGB

tmp_folder = Path(f"{gettempdir()}/sgb_advisor")
tmp_folder.mkdir(parents=True, exist_ok=True)

SGB_ALREADY_HELD_SGBS: list[str] = str(getenv("SGB_ALREADY_HELD_SGBS", "")).split(",")
"""List of SGBs already held, which will be highlited in the screenshot"""


def get_temp_file_path(file_extension: Optional[str] = "html") -> Path:
    """
    Get a file path located at a folder in the the temp folder of the OS. Creates required parents folders if it doesn't exist.

    Paramters
    ---------
    file_extension : str
        The extension of the file, without the '.' prefix. Attached to the end of the file path. Defaults to "html".

    Returns
    -------
    Path
        The path object pointing to the temporary file

    Examples
    --------
    >>> get_temp_file_path()
    Path("E:/Code/sgb_advisor/tmp/sgb_advisor/1730403483.2583637-9432.html")
    """

    file_name = f"{datetime.now().date()} SGB Advisor Output {randint(10000, 99999)}.{file_extension}"

    p = Path(rf"{tmp_folder}/{file_name}")

    # if not p.is_file():
    #     raise RuntimeError("temp file doesn't seem to have been created properly")

    return p


def get_sgb_symbol_css() -> str:
    return 'style="color: red;"'


def get_table_row_html(sgb: SGB) -> str:
    """
    Get a <tr> element that can be used in any HTML template

    Parameters
    ----------
    sgb : SGB

    Returns
    -------
    str
        The string of the HTML of the table row, to place in the template

    Examples
    --------
    >>> get_html_table_row(SGB)
    "<tr>
    <td>SGBSEP27</td>
    <td>7979.00</td>
    <td>1 September 2024</td>
    <td>12.00%</td>
    </tr>"
    """

    return f"""<tr>
        <td {get_sgb_symbol_css() if sgb.nse_symbol in SGB_ALREADY_HELD_SGBS else ""}>{sgb.nse_symbol}</td>
        <td>{sgb.ltp}</td>
        <td>{sgb.maturity_date.day} {sgb.maturity_date.strftime("%B %Y")}</td>
        <td>{sgb.xirr}</td>
    </tr>\n"""


def get_table_html(sgbs: list[SGB]) -> str:
    gold_price = get_price_of_gold()
    dt = get_ist_time()
    if len(sgbs) > 0:
        return f"""<section id="app-generated-results-placeholder">
        <table id="sgb-returns-table">
            <caption>Estimated returns of each SGB</caption>
            <thead>
                <tr>
                    <th scope="col">NSE Symbol</th>
                    <th scope="col">LTP</th>
                    <th scope="col">Maturity Date</th>
                    <th scope="col">XIRR (%)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(get_table_row_html(sgb) for sgb in sgbs)}
                <tr>
                    <td class="tcb" colspan="3">Gold price: ₹{gold_price}</td>
                    <td class="tcb">{dt.date()}</td>
                </tr>
            </tbody>
        </table>
    </section>"""
    else:
        return '<section id="app-generated-results-placeholder"><h2>No recommendations<h2></section>'


def write_html_to_file(html: str) -> Path:
    """
    Writes the HTML to the a temporary output file and returns the path of the temp file.

    Parameters
    ----------
    html: str
        The HTML to write

    Returns
    -------
    Path
        The output file the HTML was written to

    Examples
    --------
    >>> write_html_to_file("<html></html>")
    Path("E:/Code/sgb_advisor/tmp/sgb_advisor/1730403483.2583637-9432.html")
    """

    output_file = get_temp_file_path("html")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
        return output_file

    msg = f'couldn\'t save output HTML file to "{output_file}"'

    logger.error(msg)
    raise RuntimeError(msg)


@lru_cache(maxsize=None)
def get_ist_time() -> datetime:
    """
    Get a datetime object that represents the current time in IST

    Parameters
    ----------
    None

    Returns
    -------
    datetime
        Time in IST

    Examples
    --------
    >>> get_ist_time()
    datetime.datetime(2024, 11, 20, 19, 50, 21, 802675, tzinfo=datetime.timezone.utc)
    """
    utc_now = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    return utc_now + ist_offset


def write_html_output(sgbs: list[SGB]) -> Path:
    """
    Write the HTML output showing all data to a file. Generates a string with all the SGBs and their returns. Calls the `write_html_to_file()` function to write the HTML

    Parameters
    ----------
    sgbs : list[SGB]
        The list of SGBs

    Returns
    -------
    Path
        The path of the output HTML file given by `write_html_to_file()`

    Examples
    --------
    >>> write_html_output(
    ...     [
    ...         SGB1,
    ...         SGB2,
    ...         SGB3,
    ...     ]
    ... )
    Path("E:/Code/sgb_advisor/tmp/sgb_advisor/1730403483.2583637-9432.html")
    """
    html = generate_html_from_template(sgbs)

    return write_html_to_file(html)


def generate_html_from_template(sgbs: list[SGB]):
    STRING_TO_REPLACE_IN_TEMPLATE = (
        '<section id="app-generated-results-placeholder"></section>'
    )

    with open(dirname(__file__) + "/../assets/template.html") as f:
        email_template = f.read()

    replacement_string = get_table_html(sgbs)

    return email_template.replace(STRING_TO_REPLACE_IN_TEMPLATE, replacement_string, 1)
