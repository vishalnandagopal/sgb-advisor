"""
Use this to send emails
"""

from os import getenv

from boto3 import client as aws_client
from botocore.exceptions import ClientError

from ..data import SGB
from ..logg import logger
from .common import generate_html_from_template

AWS_ACCESS_KEY_ENV: str = "SGB_AWS_ACCESS_KEY"
AWS_ACCESS_KEY: str = getenv(AWS_ACCESS_KEY_ENV, "")
"""AWS access key from the AWS console. Try to create one for a non-root user"""

AWS_SECRET_ACCESS_KEY: str = getenv("SGB_AWS_SECRET_ACCESS_KEY", "")
"""AWS secret access key from the AWS console. Try to create one for a non-root user"""

SENDER: str = getenv("SGB_AWS_SES_SENDER_EMAIL", "")
"""The sender from which the email will appear to be sent by. Must be verified in Amazon SES dashboard"""

RECIPIENT: str = getenv("SGB_AWS_SES_RECIPIENT", "")
"""The recipient of the email. If your account is still in the AWS SES sandbox, the recipient must also verify his email"""

AWS_REGION: str = getenv("SGB_AWS_REGION", "")
"""The AWS region where the SES resource will be hosted"""

SUBJECT: str = "SGBs you can consider buying"
"""Subject of the email"""

CHARSET: str = "UTF-8"
"""The character encoding for the email."""


def get_email_body_plain_text(sgbs: list[SGB]):
    """
    Get text that shows the trading symbols, maturity dates, XIRR of each SGBs

    Parameters
    ----------
    list[sgb] : List of SGBs

    Returns
    -------
    str
        Plain text that shows info on many SGBs

    Examples
    --------
    >>> get_email_body_plain_text(sgbs)
    "You can consider the following SGBs. THIS IS NOT INVESTMENT ADVICE. IT CAN BE WRONG, DUE TO DATA, CALCULATION, TIMING OR ANY OTHER ERRORS. DO YOUR OWN RESEARCH. PROFITS ARE NOT GUARANTEED, LOSSES CAN BE UPTO 100%!

    SGBSEP27 - Issued at ₹5400 - LTP ₹7900.02 - 2.5% interest - 2024-09-01"
    """
    NEW_LINE = "\n"
    body_text = (
        "You can consider the following SGBs\n"
        + "THIS IS NOT INVESTMENT ADVICE. IT CAN BE WRONG, DUE TO DATA, CALCULATION, TIMING OR ANY OTHER ERRORS. DO YOUR OWN RESEARCH. PROFITS ARE NOT GUARANTEED, LOSSES CAN BE UPTO 100%!\n"
        + f"{NEW_LINE.join(str(sgb) for sgb in sgbs)}"
    )
    return body_text


def send_mail(sgbs: list[SGB]) -> bool:
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
    return send_aws_email(
        generate_html_from_template(sgbs),
        get_email_body_plain_text(sgbs),
    )


def send_aws_email(email_html: str, email_plain_text: str):
    required_envs = {
        AWS_ACCESS_KEY,
        AWS_SECRET_ACCESS_KEY,
        AWS_REGION,
        RECIPIENT,
        SENDER,
    }

    if not all(required_envs):
        logger.error("not all ENV variables seem to be set")
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
                    "Html": {"Charset": CHARSET, "Data": email_html},
                    "Text": {
                        "Charset": CHARSET,
                        "Data": email_plain_text,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
        )
        logger.info(
            f"email sent to {RECIPIENT[:4] + '****' + RECIPIENT[-9:]}! Message ID: {response['MessageId']}"
        )
        return True
    except ClientError as e:
        error_msg = "error sending email"

        if "Error" in e.response and "Message" in e.response["Error"]:
            error_msg += f" - {e.response['Error']['Message']}"

        logger.error(error_msg)

    return False
