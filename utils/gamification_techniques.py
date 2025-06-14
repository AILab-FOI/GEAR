from utils.gamification import *
import utils.personality_profiles as pprofile
from utils.inventory import Item


class GamificationTechniqueCollection:
    """
    A collection of gamification techniques and reward items.
    """
    def __init__(
        self,
        techniques: dict[str, GamificationTechnique] = None,
        reward_items: dict[str, Item] = None,
    ):
        self.techniques = techniques or {}
        self.reward_items = reward_items or {}

    def add_technique(self, technique: GamificationTechnique):
        """
        Add a technique to the collection.

        Args:
            technique (GamificationTechnique): The technique to add.
        """
        self.techniques.update({technique.name: technique})

    def add_techniques(self, techniques: list[GamificationTechnique]):
        """
        Add multiple techniques to the collection.

        Args:
            techniques (list[GamificationTechnique]): The techniques to add.
        """
        for technique in techniques:
            self.add_technique(technique)

    def remove_technique(self, name: str):
        """
        Remove a technique from the collection.

        Args:
            name (str): The name of the technique to remove.
        """
        self.techniques.pop(name, None)

    def get_technique(self, name: str):
        """
        Get a technique from the collection.

        Args:
            name (str): The name of the technique to get.

        Returns:
            GamificationTechnique: The technique.
        """
        return self.techniques.get(name, None)

    def get_techniques(self):
        """
        Get all techniques from the collection.

        Returns:
            list[GamificationTechnique]: The techniques.
        """
        return self.techniques.values()

    def add_reward_item(self, item: Item):
        """
        Add a reward item to the collection.

        Args:
            item (Item): The reward item to add.
        """
        self.reward_items.update({item.name: item})

    def add_reward_items(self, items: list[Item]):
        """
        Add multiple reward items to the collection.

        Args:
            items (list[Item]): The reward items to add.
        """
        for item in items:
            self.add_reward_item(item)

    def remove_reward_item(self, name: str):
        """
        Remove a reward item from the collection.

        Args:
            name (str): The name of the reward item to remove.
        """
        self.reward_items.pop(name, None)

    def get_reward_item(self, name: str):
        """
        Get a reward item from the collection.

        Args:
            name (str): The name of the reward item to get.

        Returns:
            Item: The reward item.
        """
        return self.reward_items.get(name, None)

    def get_reward_items(self):
        """
        Get all reward items from the collection.

        Returns:
            list[Item]: The reward items.
        """
        return self.reward_items.values()

    def get_technique_names(self):
        """
        Get all technique names from the collection.

        Returns:
            list[str]: The technique names.
        """
        return list(
            [lambda technique: technique.name for technique in self.get_techniques()]
        )

    def get_reward_item_names(self):
        """
        Get all reward item names from the collection.

        Returns:
            list[str]: The reward item names.
        """
        return list([lambda item: item.name for item in self.get_reward_items()])


reward_items = {
    "efficiency badge": Item(
        "Efficiency Badge", {"effect": "duration_reduction", "value": 0.2}
    ),
    "premium badge": Item("Premium Badge", {"effect": "price_increase", "value": 0.15}),
    "service trophy": Item(
        "Service Trophy", {"effect": "reputation_boost", "value": 10}
    ),
}

techniques = {
    "competitive pricing": CompetitivePricing(
        "competitive pricing", pprofile.competitive_pricing
    ),
    "quality focus": QualityFocus("quality focus", pprofile.quality_focus),
    "risk taking": RiskTaking("risk taking", pprofile.risk_taking),
    "service milestone": ServiceMilestone(
        "service milestone",
        pprofile.service_milestone,
        goal={"metric": "total_services", "target": 2, "comparison": "gte"},
        reward_item=reward_items.get("service trophy", None),
    ),
    "price optimizer": PriceOptimizer(
        "price optimizer",
        pprofile.price_optimizer,
        goal={"metric": "price", "target": 5, "comparison": "lte"},
        reward_item=reward_items.get("efficiency badge", None),
    ),
    "quality achievement": QualityAchievement(
        "quality achievement",
        pprofile.quality_achievement,
        goal={
            "metric": "quality_factor",
            "target": 0.7,
            "comparison": "gte",
        },
        reward_item=reward_items.get("premium badge", None),
    ),
}

defaultGamificationTechniqueCollection = GamificationTechniqueCollection(
    techniques=techniques,
    reward_items=reward_items,
)
