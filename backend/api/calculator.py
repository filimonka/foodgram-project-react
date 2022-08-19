
def create_shopping_list(ingredients: list) -> dict:
    count_ingredients_amounts = dict()
    for ingredient in ingredients:
        if ingredient[0] in count_ingredients_amounts:
            count_ingredients_amounts[ingredient[0]][0] += ingredient[1]
        else:
            count_ingredients_amounts[ingredient[0]] = [
                ingredient[1], ingredient[2]
            ]
    return count_ingredients_amounts
