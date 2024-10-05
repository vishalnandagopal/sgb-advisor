from sgb_fair_value_calculator import calculate_sgb_xirr, get_price_of_gold, get_sgbs

_ = get_sgbs()

current_gold_price = get_price_of_gold()

for sgb in _:
    sgb.xirr = calculate_sgb_xirr(sgb, current_gold_price)

print(max(map(lambda x: x.xirr, _)))
