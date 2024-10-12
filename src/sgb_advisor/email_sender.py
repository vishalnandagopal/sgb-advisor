from os import getenv
from os.path import dirname

from boto3 import client as aws_client
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from .data import SGB
from .logger import logging

load_dotenv(".env")

# From AWS Console
AWS_ACCESS_KEY = getenv("AWS_ACCESS_KEY")

AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = getenv("AWS_SES_SENDER_EMAIL")

# Replace recipient@example.com with a "To" address. If your account
# is still in the sandbox, this address must be verified.
RECIPIENT = getenv("AWS_SES_RECIPIENT")

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = getenv("AWS_REGION")

# The subject line for the email.
SUBJECT = "SGBs you can consider buying"

# The character encoding for the email.
CHARSET = "UTF-8"


def get_table_row(sgb: SGB):
    return f"""<tr>
    <td>{sgb.nse_symbol}</td>
    <td>{sgb.ltp}</td>
    <td>{sgb.maturity_date.day} {sgb.maturity_date.strftime("%B %Y")}</td>
    <td>{sgb.xirr}</td>
    </tr>"""


def get_body_plain_text(sgbs: list[SGB]):
    """Returns the email body for recipients with non-HTML email clients."""
    body_text = (
        "You can consider the following SGBs\n"
        + "THIS IS NOT INVESTMENT ADVICE. IT CAN BE WRONG, DUE TO DATA, CALCULATION, TIMING OR ANY OTHER ERRORS. DO YOUR OWN RESEARCH. PROFITS ARE NOT GUARANTEED, LOSSES CAN BE UPTO 100%!\n"
        + f"{'\n'.join(str(sgb) for sgb in sgbs)}"
    )
    return body_text


def get_body_html(sgbs: list[SGB]):
    """Returns the HTML version of the email for "modern" clients"""
    body_html = f"""<html>
    <head>
        <style>
            table{{
                border-collapse: collapse;
                border: 0.25px solid black;
            }}

            th, td {{
                border: 0.125px solid black;
                padding: 0.5rem 0.625rem;
            }}

            tbody>tr{{
            }}
        </style>
    </head>
    <body>
        <main>
            <h1>You can consider taking a look at the following SGBs:</h1>
            <p><b>This is not investment advise.</b><p>
            <p><b>The data in table could be wrong due to errors with source data, calculation, timing or other reasons. Please do your own research.</b></p>
            <p><b>PROFITS ARE NOT GUARANTEED. LOSSES CAN BE UPTO 100%!</b></p>
            <p>XIRR shown is only for interest payments. Please read assumptions made below the table<p>
            {
                f'''<table>
                    <caption>
                        Estimated returns of each SGB
                    </caption>
                    <thead>
                        <tr>
                            <th scope="col">NSE Symbol</th>
                            <th scope="col">LTP</th>
                            <th scope="col">Maturity Date</th>
                            <th scope="col">XIRR (%)</th>
                        </tr>
                    </thead>
                    <tbody>{"".join(get_table_row(sgb) for sgb in sgbs)}</tbody>
                </table>'''
                if len(sgbs) > 0 else
                "<h2>No recommendations<h2>"
            }
            <p>This is just a tool to maximize XIRR on interest payments, and to find possible arbritages between gold price IRL and the prices SGBs are trading at</p>
            <p>Assumptions made to calculate the XIRR<p>
            <ul>
                <li>The price of Gold when the SGB matures will be the same as it is today. While this may sound dumb, any increase in the price of gold should lead to a somewhat similar increase in redemption prices of all SGBs. You way think that gold can fall or increase in between, but that will affect <b>all</b> gold investments, not just SGB</li>
                <li>You are interested in gold and have finalized on SGB as a product, and are just confused among different SGBs</li>
            </ul>
        </main>
    </body>
</html>
"""
    return body_html


def send_email(sgbs: list[SGB]) -> bool:
    all_envs = {AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, RECIPIENT, SENDER}
    if not all(all_envs):
        logging.error("Not all ENV variables seem to be set")
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
                        "Data": get_body_html(sgbs),
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": get_body_html(sgbs),
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
        )
        logging.info(f"Email sent to ! Message ID: {response["MessageId"]}")
        return True
    except ClientError as e:
        logging.error(e.response["Error"]["Message"])
    return False


def write_html_to_file(sgbs: list[SGB]):
    with open(dirname(__file__) + "/assets/output.html", "w") as f:
        f.write(get_body_html(sgbs))
