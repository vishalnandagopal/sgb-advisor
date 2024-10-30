from os import getenv
from os.path import dirname

from boto3 import client as aws_client
from botocore.exceptions import ClientError

from ..data import SGB
from ..logger import logger

AWS_ACCESS_KEY = getenv("AWS_ACCESS_KEY")
"""AWS access key from the AWS console. Try to create one for a non-root user"""

AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
"""AWS secret access key from the AWS console. Try to create one for a non-root user"""

# This address must be verified with Amazon SES.
SENDER = getenv("AWS_SES_SENDER_EMAIL")
"""The sender from which the email will appear to be sent by. Must be verified in Amazon SES dashboard"""

# If your account is still in the sandbox, this address must be verified.
RECIPIENT = getenv("AWS_SES_RECIPIENT")
"""The recipient of the email. If your account is still in the AWS SES sandbox, the recipient must also verify his email"""

AWS_REGION = getenv("AWS_REGION")
"""The AWS region where the SES resource will be hosted"""

SUBJECT = "SGBs you can consider buying"
"""Email subject"""

CHARSET = "UTF-8"
"""The character encoding for the email."""


def get_html_table_row(sgb: SGB) -> str:
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
    </tr>"""


def get_email_body_plain_text(sgbs: list[SGB]):
    """
    Get text that shows the trading symbols, maturity dates, XIRR of each SGBs

    Parameters
    ----------
    list[sgb] : List of SGBs

    Returns
    -------
    str
        The text that shows info on many SGBs

    Examples
    --------
    >>> get_email_body_plain_text(sgbs)
    "You can consider the following SGBs. THIS IS NOT INVESTMENT ADVICE. IT CAN BE WRONG, DUE TO DATA, CALCULATION, TIMING OR ANY OTHER ERRORS. DO YOUR OWN RESEARCH. PROFITS ARE NOT GUARANTEED, LOSSES CAN BE UPTO 100%!

    SGBSEP27 - Issued at ₹5400 - LTP ₹7900.02 - 2.5% interest - 2024-09-01"
    """
    body_text = (
        "You can consider the following SGBs\n"
        + "THIS IS NOT INVESTMENT ADVICE. IT CAN BE WRONG, DUE TO DATA, CALCULATION, TIMING OR ANY OTHER ERRORS. DO YOUR OWN RESEARCH. PROFITS ARE NOT GUARANTEED, LOSSES CAN BE UPTO 100%!\n"
        + f"{'\n'.join(str(sgb) for sgb in sgbs)}"
    )
    return body_text


def get_email_body_html(sgbs: list[SGB]):
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

    replacement_string = (
        f"""
    <table>
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
                {"".join(get_html_table_row(sgb) for sgb in sgbs)}
            </tbody>
        </table>"""
        if len(sgbs) > 0
        else "<h2>No recommendations<h2>"
    )

    return email_template.replace(STRING_TO_REPLACE_IN_TEMPLATE, replacement_string, 1)


def send_email(sgbs: list[SGB]) -> bool:
    """
    Sends an email using AWS SES

    Parameters
    ----------
    list[sgb] : List of SGBs

    Returns
    -------
    bool : True if successful

    Examples
    --------
    >>> send_email(sgbs)
    True
    """
    required_envs = {
        AWS_ACCESS_KEY,
        AWS_SECRET_ACCESS_KEY,
        AWS_REGION,
        RECIPIENT,
        SENDER,
    }
    if not all(required_envs):
        logger.error("Not all ENV variables seem to be set")
        return False

    # Create a new SES resource and specify a region.
    client = aws_client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": get_email_body_html(sgbs),
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": get_email_body_html(sgbs),
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
        )
        logger.info(f"Email sent to ! Message ID: {response["MessageId"]}")
        return True
    except ClientError as e:
        error_msg = "Error sending email"

        if "Error" in e.response and "Message" in e.response["Error"]:
            error_msg += f" - {e.response["Error"]['Message']}"

        logger.error(error_msg)

    return False


def write_html_to_file(sgbs: list[SGB], output_file="/../assets/output.html") -> bool:
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
    with open(dirname(__file__) + output_file, "w") as f:
        f.write(get_email_body_html(sgbs))
        return True
    return False
