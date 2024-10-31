from os import makedirs
from os.path import dirname
from random import randint
from tempfile import gettempdir
from time import time

from ..data import SGB
from ..logger import logger


def get_temp_file_path(file_extension: str = ".html") -> str:
    tmp_folder = f"{gettempdir()}/sgb_advisor"
    makedirs(tmp_folder, exist_ok=True)

    return rf"{tmp_folder}/{time()}-{randint(0, 10000)}.{file_extension}"


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
        <td>{sgb.nse_symbol}</td>
        <td>{sgb.ltp}</td>
        <td>{sgb.maturity_date.day} {sgb.maturity_date.strftime("%B %Y")}</td>
        <td>{sgb.xirr}</td>
    </tr>
"""


def get_email_body_html(sgbs: list[SGB]) -> str:
    """
    Reads the template at ./assets/email_template.html and returns the HTML version of the email for "modern" clients.

    Parameters
    ----------
    list[sgb] : List of SGBs

    Returns
    -------
    str : Templated HTML


    Examples
    --------
    >>> get_email_body_html(sgbs)
    "<html>....</html>"
    """

    STRING_TO_REPLACE_IN_TEMPLATE = '<section id="generated-results"></section>'

    with open(dirname(__file__) + "/../assets/email_template.html") as f:
        email_template = f.read()

    replacement_string = get_table_html(sgbs)

    return email_template.replace(STRING_TO_REPLACE_IN_TEMPLATE, replacement_string, 1)


def get_table_html(sgbs: list[SGB]) -> str:
    table_html: str = (
        f"""<table id="sgb-returns-table">
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
            </tbody>
        </table>"""
        if len(sgbs) > 0
        else "<h2>No recommendations<h2>"
    )

    return table_html


def write_html_to_file(html: str) -> str:
    """
    Writes the HTML to the output file for debugging purposes

    Parameters
    ----------
    list[sgb] : List of SGBs
    output_file : The output file to write the HTML to. Defaults to `/../assets/output/email.html`

    Returns
    -------
    bool : True if successful

    Examples
    --------
    >>> send_email(sgbs)
    True
    """

    output_file = get_temp_file_path("html")

    with open(output_file, "w") as f:
        f.write(html)
        return output_file

    msg = f'couldn\'t save output HTML file to "{output_file}"'

    logger.error(msg)
    raise RuntimeError(msg)


def write_table_html_to_file(sgbs: list[SGB]) -> str:
    table_html = get_table_html(sgbs)

    html = f"""<html>
    <head>
        <title>SGB advisor output</title>
        <style>
            table {{
                border-collapse: collapse;
                border: 0.25px solid black;
            }}

            th,
            td {{
                border: 0.125px solid black;
                padding: 0.5rem 0.625rem;
            }}
        </style>
    </head>
        </body>
            {table_html}
        </body>
    </html>"""

    return write_html_to_file(html)
