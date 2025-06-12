import numpy as np
from utils.service import Service
from typing import Self

class Recipe:
    """
    A recipe is a list of services that a consumer needs to perform to complete a task.
    """
    def __init__(self, recipe: list[dict[str, any] | Self]):
        self.recipe = []
        self.set_recipe(recipe)
        self.current_element_index = 0
        self.done = False

    def get_recipe(self) -> list[dict[str, any]]:
        """
        Get the recipe.

        Returns:
            list[dict[str, any]]: The recipe.
        """
        return self.recipe

    def set_recipe(self, recipe: list[dict[str, any] | Self]):
        """
        Set the recipe.

        Args:
            recipe (list[dict[str, any] | Self]): The recipe.
        """
        assert isinstance(recipe, list), "Recipe must be a list."
        assert all(isinstance(element, dict) or isinstance(element, Recipe) for element in recipe), "Recipe must be a list of dicts or Recipes."
        self.recipe = list(map(self.add_element, recipe))

    def get_recipe_length(self) -> int:
        """
        Get the length of the recipe.

        Returns:
            int: The length of the recipe.
        """
        return len(self.recipe)

    def add_element(self, element: dict[str, any] | Self) -> dict[str, any] | Self:
        """
        Add an element to the recipe.

        Args:
            element (dict[str, any] | Recipe): The element to add.

        Returns:
            dict[str, any] | Recipe: The added element.
        """
        assert isinstance(element, dict) or isinstance(element, Recipe), "Element must be a dict or a Recipe."
        if isinstance(element, Recipe):
            pass
        elif "recipe" in element:
            element = Recipe(element.get("recipe"))
        elif "service" in element and isinstance(element.get("service"), dict):
            element = {"service": Service(**element.get("service"))}
        self.recipe.append(element)
        return element

    def remove_element(self, element: dict[str, any]):
        """
        Remove an element from the recipe.

        Args:
            element (dict[str, any]): The element to remove.
        """
        assert element in self.recipe, "Element not in recipe."
        self.recipe.remove(element)

    def get_current_element(self) -> dict[str, any]:
        """
        Get the current element.

        Returns:
            dict[str, any]: The current element.
        """
        if self.current_element_index < len(self.recipe):
            return self.recipe[self.current_element_index]
        return None

    def finish_current_element(self):
        """
        Finish the current element.
        """
        current_element = self.get_current_element()
        if current_element is not None:
            current_element["done"] = True
        self.check_if_done()

    def next_element(self):
        """
        Move to the next element in the recipe.
        """
        if self.current_element_index + 1 < len(self.recipe):
            self.current_element_index += 1
        self.check_if_done()

    def check_if_done(self):
        """
        Check if the recipe is done.
        """
        self.done = all(element.get("done") for element in self.recipe)

    def is_done(self) -> bool:
        """
        Check if the recipe is done.

        Returns:
            bool: True if the recipe is done, False otherwise.
        """
        return self.done

    def to_json(self):
        """
        Convert the recipe object to a JSON object.

        Returns:
            dict: The JSON object.
        """
        return {
            "recipe": self.recipe,
            "current_element_index": self.current_element_index,
            "done": self.done
        }

    @classmethod
    def from_json(cls, data):
        """
        Create a recipe object from a JSON object.

        Args:
            data (dict): The JSON object.

        Returns:
            Recipe: The recipe object.
        """
        recipe = cls(data["recipe"])
        recipe.current_element_index = data["current_element_index"]
        recipe.done = data["done"]
        return recipe

    @classmethod
    def random(cls, services: list[str]=["A", "B", "C", "D"], min_length: int=1, max_length: int=5):
        import random
        recipe_length = random.randint(min_length, max_length)
        return cls([{"service": Service(random.choice(services)), "done": False, "providers": []} for _ in range(recipe_length)])

    def __str__(self):
        return f"Recipe.{self.current_element_index+1}/{self.get_recipe_length()}: " + ", ".join([element.get("service").name if isinstance(element, dict) else f"({str(element)})" if isinstance(element, Recipe) else "" for element in self.recipe])

    def __repr__(self):
        return repr(self.recipe)