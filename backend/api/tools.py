
def create_shopping_list(ingredients: list) -> dict:
    count_ingredients_amounts = dict()
    for name, amount, measurement_unit in ingredients:
        if name in count_ingredients_amounts:
            count_ingredients_amounts[name][0] += amount
        else:
            count_ingredients_amounts[name] = [amount, measurement_unit]
    return count_ingredients_amounts
