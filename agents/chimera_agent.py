from spade.agent import Agent
from utils.personality import Personality


class ChimeraAgent(Agent):
    """
    A Chimera agent is an agent that has a personality.
    """
    def __init__(self, jid, password, personality: dict[str, int | float | list] = None, **kwargs):
        """
        Initialize the Chimera agent.

        Args:
            jid (str): The JID of the agent.
            password (str): The password of the agent.
            personality (dict[str, int | float | list], optional): The personality of the agent. Defaults to None.
        """
        super().__init__(jid, password, **kwargs)
        self.personality = Personality(personality=personality)

    async def setup(self):
        print(f"[Chimera {self.jid}] Starting with personality: {self.personality}")
