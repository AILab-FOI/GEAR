from agents.chimera_agent import ChimeraAgent
from utils.inventory import Inventory

class AgentWithInventory(ChimeraAgent):
    """
    An agent with an inventory.
    """
    def __init__(self, jid, password, **kwargs):
        """
        Initialize the agent with an inventory.

        Args:
            jid (str): The JID of the agent.
            password (str): The password of the agent.
        """
        super().__init__(jid, password, **kwargs)
        self.inventory = Inventory()

    async def setup(self):
        print(f"[Agent with inventory {self.jid}] Starting with inventory {self.inventory} and personality: {self.personality}")
