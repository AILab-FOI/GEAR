from collections import deque

from agents.agent_with_inventory import AgentWithInventory
from behaviours.provider_behaviours import setup_FSM_provider_behaviour
from behaviours.communication_behaviours import ReceiveMessagesBehaviour

from utils.inventory import Item
from utils.service import Service

class ServiceProviderAgent(AgentWithInventory):
    def __init__(self, jid, password, services=None, budget=100, capacity=1, **kwargs):
        super().__init__(jid, password, **kwargs)
        self.inventory.add_item_in_quantity(Item("money"), budget)
        if services is None:
            services = [Service.random() for _ in range(2)]
        self.inventory.add_item(Item("list of services", {"services": services}))
        self.inventory.add_item(Item("inbox", {"messages": deque()}))
        for _ in range(capacity):
            self.inventory.add_item(Item("service providing medium", {"available": True}))

        if not any(self.personality.get_personality_vector()):
            self.personality.generate_random_personality_vector()

    @property
    def budget(self):
        return self.inventory.get_item_quantity(self.inventory.get_item_by_name("money"))

    @budget.setter
    def budget(self, value):
        self.inventory.update_item_stack_attribute(self.inventory.get_item_by_name("money"), "quantity", value)

    @property
    def services(self):
        return self.inventory.get_item_by_name("list of services").get_feature_value("services")

    @property
    def inbox(self):
        return self.inventory.get_item_by_name("inbox").get_feature_value("messages")

    @property
    def capacity(self):
        return self.inventory.get_items_by_name("service providing medium")

    async def setup(self):
        print(f"[Provider {self.jid}] Starting with services: {self.services} and budget: {self.budget}")
        self.add_behaviour(ReceiveMessagesBehaviour())
        self.main_FSM_behaviour = setup_FSM_provider_behaviour()
        self.add_behaviour(self.main_FSM_behaviour)
