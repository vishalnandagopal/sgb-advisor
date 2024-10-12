from src.sgb_advisor import (
    NSE_SGB_URL,
    get_sgbs,
    logging,
    write_html_to_file,
    send_email,
)

all_sgbs = get_sgbs()


write_html_to_file(all_sgbs)
send_email(all_sgbs)

if len(all_sgbs) > 0:
    print(
        f"{all_sgbs[0].nse_symbol} will give you {all_sgbs[0].xirr}% if gold price stays the same"
    )
else:
    logging.error(
        f"SGB list seems to be empty. Error when fetching from NSE? Check if anything exists on {NSE_SGB_URL}"
    )
