# sgb-advisor

A tool to analyse Sovereign Gold Bonds and compare their yields.

[Sovereign Gold Bond](https://www.rbi.org.in/commonman/English/Scripts/FAQs.aspx?Id=1658) is a security issued by [RBI](https://rbi.org.in) linked to the price of gold.

This tries to use publically available data and maths to advise you on which SGB among all of them is trading at it's lowest "fair value".

**This does not recommend anything. Calculations, data or something else can be wrong. Do your own research**

## Tools used:

1. [Playwright](https://playwright.dev/python/) for getting SGB prices from [NSE](https://www.nseindia.com/market-data/sovereign-gold-bond) and price of gold from [IBJA](https://www.ibja.co/).

2. [pyxirr](https://github.com/Anexen/pyxirr) to calculate XIRR

## Running the app

Run any of these 2 in the root of the project after cloning it

1. [Docker](https://www.docker.com/products/docker-desktop/) (recommended)

    ```sh
    docker build . -t vishalnandagopal/sgb-advisor:latest
    docker run vishalnandagopal/sgb-advisor:latest
    ```

2. While I used [`uv`](https://github.com/astral-sh/uv) to build the project, you can use that or plain pip

    ```sh
    pip install uv
    uv sync
    python app.py
    ```

    (or)

    ```sh
    pip install -r requirements.txt
    python app.py
    ```

## Sending results to someone

Set how to send results to the user in an .

1.  Telegram (recommended)

    If you have a telegram accout, you can create a bot in a few seconds, making it very easy to notify you of the results of every run.

    1. Get an API key from [BotFather](https://t.me/BotFather) on Telegram ("bot token").

    2. Get the chat ID of the user(s) you want to send the output to. It is the unique identifier for the target chat (integer in this case) or username of the target channel (@channelusername in this case). Output can be sent to multiple users (place comma-separated chat IDs). Errors are only sent to the first chat-id.

    If you don't know your chat ID, get it by sending a message to [@JsonDumpBot](https://t.me/JsonDumpBot). The ["chat"]["id"] in response is the ID you need to use to send to that same account you texted the bot from.

2.  Email (AWS SES only)

    Sending results to an email address using [Amazon SES](https://aws.amazon.com/ses/) is supported.

    1. Get API keys from AWS console and place it in an `env` file as per the below format.

    The email address you want to send from be verified in AWS console. Even the recipient of the email must be verified if you are a new user and in AWS SES Sandbox.

```env
MODE=telegram
# How to notify the user. Accepted values are "telegram", "email" or "both"

TELEGRAM_BOT_TOKEN=xxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_CHAT_IDS=xxxxxxxxx,xxxxxxx

# No one need to set any of these if you only want to send a message through telegram
AWS_ACCESS_KEY=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_SES_SENDER_EMAIL=SGB Advisor <sgb-advisor@your-verified-domain.com>
AWS_SES_RECIPIENT=example@example.com
AWS_REGION=us-east-1
```

## License

[GNU GPLv3](./LICENSE)

## TODO

-   Similar tool for finding arbritages in ETFs tracking the same index.
