"""
6.101 Lab:
Recipes
"""

import pickle
import sys

# import typing # optional import
# import pprint # optional import

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary mapping each atomic food name to its cost.
    """
    recipe_cost = {}
    # Simply going through the database and finding the atomic ingredients
    for recipe in recipes_db:
        if recipe[0] == "atomic":
            recipe_cost[recipe[1]] = recipe[2]
    return recipe_cost


def compound_ingredient_possibilities(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary that maps each compound food name to a
    list of all the ingredient lists associated with that name.
    """
    recipe_compound = {}
    # Going through the database and finding the compound ingredients
    for recipe in recipes_db:
        if recipe[0] == "compound":
            # Check if the compound wasn't present
            if recipe[1] not in recipe_compound:
                # This ruined test cases at the start, need to remember.
                recipe_compound[recipe[1]] = []
            # Appending the ingredients to the list
            recipe_compound[recipe[1]].append(recipe[2])
    return recipe_compound


def lowest_cost(recipes_db, food_name, forbidden=None):
    """
    Given a recipes database and the name of a food (str), return the lowest
    cost of a full recipe for the given food item or None if there is no way
    to make the food_item.
    """
    # Creating a forbidden set for efficiency
    forbidden_set = set(forbidden) if forbidden else set()
    # Getting the atomic costs and the compound possibilities
    atomic_costs = atomic_ingredient_costs(recipes_db)
    compound_possibilities = compound_ingredient_possibilities(recipes_db)

    # Recursive function to find the lowest cost
    def recurse(food):
        # Checking the edge cases
        if food in forbidden_set:
            return None
        if food in atomic_costs:
            return atomic_costs[food]
        if food not in compound_possibilities:
            return None

        # List to store the possible costs
        cost_pos = []
        # Going through the possible ingredients
        for ingredients in compound_possibilities[food]:
            # Initialize the cost
            cost = 0
            for ingr, quant in ingredients:
                # Calculating the cost of the ingredient w/ recursion
                ingr_cost = recurse(ingr)
                # If the ingredient doesn't have a cost, then break
                if not ingr_cost:
                    cost = None
                    break
                # Appending the cost to the total
                cost += ingr_cost * quant
            # If the cost is still valid, then append it
            if cost:
                cost_pos.append(cost)
        # Returning the lowest cost
        return min(cost_pos, default=None)

    # Returning the lowest cost of the food
    return recurse(food_name)


def scaled_recipe(recipe_dict, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    # Scale the quantiies
    return {ingredient: quant * n for ingredient, quant in recipe_dict.items()}


def add_recipes(recipe_dicts):
    """
    Given a list of recipe dictionaries that map food items to quantities,
    return a new dictionary that maps each ingredient name
    to the sum of its quantities across the given recipe dictionaries.

    For example,
        add_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    # Intialized combined dictionary
    combined = {}
    # Going through the recipes
    for recipe in recipe_dicts:
        for ingr, quant in recipe.items():
            # If the ingredient wasn't present, then initialize it
            if ingr not in combined:
                combined[ingr] = 0
            # Adding the quantity
            combined[ingr] += quant
    return combined


def cheapest_flat_recipe(recipes_db, food_name, forbidden=None):
    """
    Given a recipes database and the name of a food (str), return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    # Creating a forbidden set for efficiency
    forbidden_set = set(forbidden) if forbidden else set()
    # Getting the atomic costs and the compound possibilities
    atomic_costs = atomic_ingredient_costs(recipes_db)
    compound_possibilities = compound_ingredient_possibilities(recipes_db)

    # Function for the cost of a recipe
    def cost(recipe, atomic_cost):
        # Using a comprhenesion for efficiency
        return sum(atomic_cost.get(i, float("inf")) * q for i, q in recipe.items())

    def recurse(food):
        # Checking the edge cases
        if food in forbidden_set:
            return None
        if food in atomic_costs:
            return {food: 1}
        if food not in compound_possibilities:
            return None
        # The possible recipes
        poss_recipes = []
        # Going through the ingredients
        for ingredients in compound_possibilities[food]:
            recipe = []
            # Going through the ingredients
            for ingr, quant in ingredients:
                ingr_recipe = recurse(ingr)
                if not ingr_recipe:
                    break
                # Scale the recipe
                recipe.append(scaled_recipe(ingr_recipe, quant))
            else:
                # Adding the recipe
                poss_recipes.append(add_recipes(recipe))
        # Returning the cheapest recipe
        return min(poss_recipes, key=lambda x: cost(x, atomic_costs), default=None)

    return recurse(food_name)


def combine_recipes(nested_recipes):
    """
    Given a list of lists of recipe dictionaries, where each inner list
    represents all the recipes for a certain ingredient, compute and return a
    list of recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    # If there are no recipes, then return an empty list
    if not nested_recipes:
        return []
    # Initialize the combine list
    combine = [{}]
    for recipes in nested_recipes:
        # The new combinations for test cases
        new_comb = []
        # Going through the recipes
        for recipe in recipes:
            for comb in combine:
                # Adding the new combinations
                new_comb.append(add_recipes([comb, recipe]))
        # Updating the combine list
        combine = new_comb
    return combine


def all_flat_recipes(recipes_db, food_name, forbidden=None):
    """
    Given a recipes database, the name of a food (str), produce a list (in any
    order) of all possible flat recipe dictionaries for that category.

    Returns an empty list if there are no possible recipes
    """
    # Creating a forbidden set for efficiency
    forbidden_set = set(forbidden) if forbidden else set()
    # Getting the atomic costs and the compound possibilities
    atomic_costs = atomic_ingredient_costs(recipes_db)
    compound_possibilities = compound_ingredient_possibilities(recipes_db)

    # Recursive function to find all the recipes
    def recurse(food):
        # Checking the edge cases
        if food in forbidden_set:
            return []
        if food in atomic_costs:
            # Returning the recipe
            return [{food: 1}]
        if food not in compound_possibilities:
            return []
        # All the possible recipes
        poss_recipes = []
        # Going through the ingredients
        for ingredients in compound_possibilities[food]:
            # The curr recipe
            recipe = []
            # Going through our ingredients
            for ingr, quant in ingredients:
                ingr_recipes = recurse(ingr)
                if not ingr_recipes:
                    break
                # Scaling
                recipe.append([scaled_recipe(x, quant) for x in ingr_recipes])
            else:
                # Combining with the other ingredients
                # using extend because combine_recipes returns a l
                # ist of lists, append doesn't work
                poss_recipes.extend(combine_recipes(recipe))
        return poss_recipes

    return recurse(food_name)


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes_db = pickle.load(f)
    # you are free to add additional testing code here!
