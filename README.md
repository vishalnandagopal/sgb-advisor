# sgb-advisor

[Sovereign Gold Bond](https://www.rbi.org.in/commonman/English/Scripts/FAQs.aspx?Id=1658) is a security issued by [RBI](https://rbi.org.in) linked to the price of gold.

This tries to use publically available data and maths to advise you on which SGB among all of them is trading at it's lowest "fair value".

**THIS DOES NOT AND CANNOT "RECOMMEND" ANY BOND, IT JUST OUTPUTS A POSSIBLE XIRR. CALCULATIONS CAN BE WRONG**

## Tools used:

1. [Playwright](https://playwright.dev/python/) for getting SGB prices from [NSE](https://www.nseindia.com/market-data/sovereign-gold-bond) and price of gold from [IBJA](https://www.ibja.co/).

2. [pyxirr](https://github.com/Anexen/pyxirr) to calculate XIRR

## To run

1. [Docker](https://www.docker.com/products/docker-desktop/) (recommended)

    ```sh
    docker build .
    docker run sha256:xxxx
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

## License

[GNU GPLv3](./LICENSE)

## TODO

- Send results via email
- Similar tool for ETFs tracking the same index.