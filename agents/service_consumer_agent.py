from agents.agent_with_inventory import AgentWithInventory
from behaviours.consumer_behaviours import setup_FSM, CheckOfferedServices

from utils.recipe import Recipe
from utils.inventory import Item

class ServiceConsumerAgent(AgentWithInventory):
    def __init__(self, jid, password, recipe=None, budget=50, providers=None, **kwargs):
        super().__init__(jid, password, **kwargs)
        self.inventory.add_item_in_quantity(Item("money"), budget)
        self.inventory.add_item(Item("recipe", {"object": recipe or Recipe.random()}))
        self.inventory.add_item(Item("current recipe element", {"object": None}))
        self.inventory.add_item_in_quantity(Item("completed recipe"), 0)
        self.inventory.add_item(Item("list of providers", {"values": providers or {}}))
        if not any(self.personality.get_personality_vector()):
            self.personality.generate_random_personality_vector()

    @property
    def budget(self):
        return self.inventory.get_item_quantity(self.inventory.get_item_by_name("money"))

    @budget.setter
    def budget(self, value):
        self.inventory.update_item_stack_attribute(self.inventory.get_item_by_name("money"), "quantity", value)

    @property
    def recipe(self):
        return self.inventory.get_item_by_name("recipe").get_feature_value("object")

    @recipe.setter
    def recipe(self, value):
        self.inventory.get_item_by_name("recipe").set_feature("object", value)

    @property
    def current_recipe_element(self):
        return self.inventory.get_item_by_name("current recipe element").get_feature_value("object")

    @current_recipe_element.setter
    def current_recipe_element(self, value):
        self.inventory.get_item_by_name("current recipe element").set_feature("object", value)

    @property
    def completed_recipes(self):
        return self.inventory.get_item_quantity(self.inventory.get_item_by_name("completed recipe"))

    @completed_recipes.setter
    def completed_recipes(self, value):
        self.inventory.update_item_stack_attribute(self.inventory.get_item_by_name("completed recipe"), "quantity", value)

    @property
    def providers(self):
        return self.inventory.get_item_by_name("list of providers").get_feature_value("values")

    @providers.setter
    def providers(self, value):
        self.inventory.get_item_by_name("list of providers").set_feature("values", value)

    async def setup(self):
        print(f"[Consumer {self.jid}] Starting with recipe: {self.recipe} and budget: {self.budget}")
        self.main_FSM_behaviour = setup_FSM()
        self.add_behaviour(self.main_FSM_behaviour)