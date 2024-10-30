from dotenv import load_dotenv

from src.sgb_advisor import logger, notify, write_html_to_file

load_dotenv(".env")

all_sgbs = []  # get_sgbs()

write_html_to_file(all_sgbs)

if len(all_sgbs) > 0:
    print(
        f"{all_sgbs[0].nse_symbol} will give you {all_sgbs[0].xirr}% if gold price stays the same"
    )
else:
    logger.error(f"SGB list seems to be empty")
