from src.sgb_advisor import calculate_sgb_xirr, get_price_of_gold, get_sgbs

all_sgbs = get_sgbs()

current_gold_price = get_price_of_gold()
max_sgb = all_sgbs[0]

for sgb in all_sgbs:
    sgb.xirr = calculate_sgb_xirr(sgb, current_gold_price)
    if sgb.xirr > max_sgb.xirr:
        max_sgb = sgb

print(f"{max_sgb} will give you {max_sgb.xirr}% if gold price stays the same")
