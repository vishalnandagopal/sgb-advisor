# sgb-advisor

A tool to analyse Sovereign Gold Bonds and compare their yields.

[Sovereign Gold Bond](https://en.wikipedia.org/wiki/Sovereign_Gold_Bond) is a security issued by the [RBI](https://rbi.org.in) on behalf of the Government of India. It is linked to the price of gold.

This tool tries to use publically available data and ✨maths✨ to advise you on which SGB among all of them is trading at it's lowest "fair value".

**This does not recommend anything. Calculations, data or something else can be wrong. Do your own research before investing your money anywhere.**

~~**Demo**: Output is being sent in [this](https://t.me/sgb_advisor) public Telegram channel at ~10:00 AM IST every weekday!~~

## Tools used:

1. [Playwright](https://playwright.dev/python/) for getting SGB prices from [NSE](https://www.nseindia.com/market-data/sovereign-gold-bond) and the price of gold from [IBJA](https://www.ibja.co/).

2. [pyxirr](https://github.com/Anexen/pyxirr) to calculate XIRR

## Running the app

You can use any of the 3 methods given below

1. You can use plain pip or something like [`uv`](https://github.com/astral-sh/uv) to build and run the project.

    ```sh
    # Highly recommend creating a venv using `python -m venv .venv` and then activating it (https://docs.python.org/3/library/venv.html#how-venvs-work) first.
    pip install sgb-advisor
    playwright install --with-deps firefox
    # Setup .env in same folder
    sgb-advisor
    ```

2. Docker

    ```sh
    # Setup .env in same folder
    docker container run --env-file .env --pull always ghcr.io/vishalnandagopal/sgb-advisor:latest
    ```

3. ~~Github actions~~

**This is not working now as NSE has blocked IPs outside India from accessing its website [since May 2025](https://web.archive.org/web/20250508075217/https://economictimes.indiatimes.com/markets/stocks/news/bse-nse-restrict-access-to-websites-for-overseas-users-reports/articleshow/120955528.cms) and Github Action run on American servers.**

-   An action is already setup [here](./.github/workflows/sgb_advisor.yaml).
-   Fork the repo, enable the action in repo settings, setup the required GitHub secrets, vars & envs.

## Environment variables

Place the required env variables in an [`.env`](.env) file.

```env
# How to notify the user. Accepted values are "telegram", "email", "both" or "none".
# Use "none" if you just want to run the program and generate results
SGB_MODE=telegram
SGB_LOG_LEVEL=info

# Get token from BotFather on Telegram
SGB_TELEGRAM_BOT_TOKEN=xxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Can be one or many users/channels
SGB_TELEGRAM_CHAT_IDS=xxxxxxxxx,xxxxxxx,@sgb_advisor

# No one need to set any of these if you only want to send a message through telegram
SGB_AWS_ACCESS_KEY=xxx
SGB_AWS_SECRET_ACCESS_KEY=xxx
SGB_AWS_SES_SENDER_EMAIL=SGB Advisor <sgb-advisor@your-verified-domain.com>
SGB_AWS_SES_RECIPIENT=example@example.com
SGB_AWS_REGION=us-east-1

# Highlights below mentioned SGBs in the screenshot for easier identification - Use NSE Scrip names from [scripts.csv](./src/sgb_advisor/assets/scrips.csv). Comma separated string
SGB_ALREADY_HELD_SGBS=SGBAUG28V,SGBMAR28X
```

## Sending results to someone

1.  Telegram (recommended)

    If you have a telegram account, you can create a bot in a few seconds, making it very easy to notify you of the results of every run.

    The bot can send results to multiple telegram accounts (both users and channels) at once.

    1. Get an API key from [BotFather](https://t.me/BotFather) on Telegram ("bot token").

    2. Get the chat ID of the user(s) you want to send the output to. It is the unique identifier for the target chat (integer in this case) or username of the target channel (@channelusername in this case). Output can be sent to multiple users (place comma-separated chat IDs). Errors are only sent to the first chat-id.

    If you don't know your chat ID, get it by sending a message to [@JsonDumpBot](https://t.me/JsonDumpBot). The `["chat"]["id"]` in response is your chat ID.

2.  Email (AWS SES only)

    Sending results to an email address using [Amazon SES](https://aws.amazon.com/ses/) is supported.

    1. Get API keys from AWS console and place it in an `.env` file as per the above format.

    The email address you want to send from be verified in AWS console. Even the recipient of the email must be verified if you are a new user and in AWS SES Sandbox.

## License

[GNU GPLv3](./LICENSE)

## TODO

-   Similar tool for finding arbritages in ETFs tracking the same index.

## Disclaimers

This tries to use publically available data and maths to advise you on which SGB among all of them is trading at it's lowest "fair value".

This is just a tool to maximize XIRR on interest payments, and to find possible arbritages between gold price IRL and the prices SGBs are trading at.

**This does not recommend anything. Calculations, data or something else can be wrong. Do your own research**

### Assumptions Made

-   The price of Gold when the SGB matures will be the same as it is today. While this may sound dumb, any increase in the price of gold should lead to a somewhat similar increase in redemption prices of all SGBs. You way think that gold can fall or increase in between, but that will affect **all** gold investments, not just SGB

-   You are interested in gold and have finalized on SGB as a product, and are just confused among different SGBs.

Copyright (C) 2025 Vishal N (hi@vishalnandagopal.com)
