class Item:
    """
    An item is an object that can be stored in an inventory.
    """
    def __init__(self, name: str, features: dict[str, any]=None):
        """
        Initialize the item.

        Args:
            name (str): The name of the item.
            features (dict[str, any], optional): The features of the item. Defaults to None.
        """
        assert isinstance(name, str), "Name must be a string."
        assert features is None or isinstance(features, dict), "Features must be a dict."
        self.name = name
        self.features = features or {}

    def add_feature(self, feature: str, value: any):
        """
        Add a feature to the item.

        Args:
            feature (str): The name of the feature.
            value (any): The value of the feature.
        """
        assert feature not in self.features, f"Feature {feature} already exists"
        self.features.update({feature: value})

    def set_feature(self, feature: str, value: any):
        """
        Set a feature of the item.

        Args:
            feature (str): The name of the feature.
            value (any): The value of the feature.
        """
        assert feature in self.features, f"Feature {feature} not found"
        self.features.update({feature: value})

    def update_feature(self, feature: str, value: any):
        """
        Update a feature of the item.

        Args:
            feature (str): The name of the feature.
            value (any): The value of the feature.
        """
        assert feature in self.features, f"Feature {feature} not found"
        self.set_feature(feature, value)

    def update_features(self, features: dict):
        """
        Update or add multiple features of the item.

        Args:
            features (dict): A dictionary containing the features to update.
        """
        self.features.update(features)

    def get_feature_value(self, feature: str) -> any:
        """
        Get the value of a feature.

        Args:
            feature (str): The name of the feature.

        Returns:
            any: The value of the feature.
        """
        assert feature in self.features, f"Feature {feature} not found"
        return self.features.get(feature)

    def get_features(self) -> dict[str, any]:
        """
        Get all the features of the item.

        Returns:
            dict: A dictionary containing all the features.
        """
        return self.features

    def remove_feature(self, feature: str):
        """
        Remove a feature from the item.

        Args:
            feature (str): The name of the feature.
        """
        assert feature in self.features, f"Feature {feature} not found"
        self.features.pop(feature)

    def get_name(self) -> str:
        """
        Get the name of the item.

        Returns:
            str: The name of the item.
        """
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Item({self.name}, {self.features})"

    def to_json(self) -> dict:
        """
        Convert the item object to a JSON object.

        Returns:
            dict: The JSON object.
        """
        return {
            "name": self.name,
            "features": self.features
        }

    @classmethod
    def from_json(cls, json):
        return cls(json["name"], json["features"])


class Inventory():
    def __init__(self, item_stack: dict[Item, dict[str, any]] = None):
        """
        Initialize the inventory.

        Args:
            item_stack (dict[Item, dict[str, any]], optional): A dictionary containing the item stacks and their attributes (e.g. quantity). Defaults to None.
        """
        self.item_stack = item_stack or {}

    def add_item(self, item: Item):
        """
        Add an item to the inventory.

        Args:
            item (Item): The item to add.
        """
        assert isinstance(item, Item), "Item must be an Item object."
        if item in self.item_stack:
            self.item_stack.update({item: {"quantity": self.item_stack.get(item).get("quantity") + 1}})
        else:
            self.item_stack.update({item: {"quantity": 1}})

    def add_items(self, items: list[Item]):
        """
        Add multiple items to the inventory.

        Args:
            items (list[Item]): A list of items to add.
        """
        assert all(isinstance(item, Item) for item in items), "All items must be Item objects."
        for item in items:
            self.add_item(item)

    def add_item_in_quantity(self, item: Item, quantity: int):
        """
        Add an item to the inventory in a specific quantity.

        Args:
            item (Item): The item to add.
            quantity (int): The quantity of the item to add.
        """
        assert isinstance(item, Item), "Item must be an Item object."
        assert isinstance(quantity, int), "Quantity must be an integer."
        if item in self.item_stack:
            self.item_stack.update({item: {"quantity": self.item_stack.get(item).get("quantity") + quantity}})
        else:
            self.item_stack.update({item: {"quantity": quantity}})

    def remove_item(self, item: Item):
        """
        Remove an item from the inventory.

        Args:
            item (Item): The item to remove.
        """
        assert item in self.item_stack, "Item not found"
        new_quantity = self.item_stack.get(item).get("quantity") - 1
        if new_quantity:
            self.item_stack.update({item: {"quantity": new_quantity}})
        else:
            self.item_stack.pop(item)

    def has_item(self, item: Item):
        """
        Check if the inventory contains an item.

        Args:
            item (Item): The item to check.

        Returns:
            bool: True if the inventory contains the item, False otherwise.
        """
        return item in self.item_stack

    def get_items_in_inventory(self):
        """
        Get all the items in the inventory.

        Returns:
            list[Item]: A list containing the items.
        """
        return self.item_stack.keys()

    def get_item_stacks(self):
        """
        Get all the item stacks in the inventory.

        Returns:
            dict[Item, dict[str, any]]: A dictionary containing the item stacks and their attributes.
        """
        return self.item_stack

    def get_items_by_name(self, name: str) -> list[Item]:
        """
        Get all items from the inventory by name.

        Args:
            name (str): The name of the item.

        Returns:
            Item: The item.
        """
        return list(filter(lambda item: name.lower() in item.get_name().lower(), self.item_stack.keys()))

    def get_item_by_name(self, name: str):
        """
        Get an item from the inventory.

        Args:
            name (str): The name of the item.

        Returns:
            Item: The item.
        """
        return self.get_items_by_name(name)[0]

    def get_item_by_feature(self, feature: str, value: any):
        """
        Get an item from the inventory by a feature.

        Args:
            feature (str): The name of the feature.
            value (any): The value of the feature.

        Returns:
            Item: The item.
        """
        return next(filter(lambda item: item.get_feature_value(feature) == value, self.item_stack), None)

    def get_item_by_features(self, features: dict):
        """
        Get an item from the inventory by multiple features.

        Args:
            features (dict): A dictionary containing the features and their values.

        Returns:
            Item: The item.
        """
        return next(filter(lambda item: all(item.get_feature_value(feature) == value for feature, value in features.items()), self.item_stack), None)

    def get_items_by_feature(self, feature: str, value: any):
        """
        Get all items from the inventory by a feature.

        Args:
            feature (str): The name of the feature.
            value (any): The value of the feature.

        Returns:
            list[Item]: A list of items.
        """
        return list(filter(lambda item: item.get_feature_value(feature) == value, self.item_stack))

    def get_items_by_features(self, features: dict):
        """
        Get all items from the inventory by multiple features.

        Args:
            features (dict): A dictionary containing the features and their values.

        Returns:
            list[Item]: A list of items.
        """
        return list(filter(lambda item: all(item.get_feature_value(feature) == value for feature, value in features.items()), self.item_stack))

    def get_item_quantity(self, item: Item):
        """
        Get the quantity of an item in the inventory.

        Args:
            item (Item): The item.

        Returns:
            int: The quantity of the item.
        """
        assert item in self.item_stack, "Item not found"
        return self.item_stack.get(item).get("quantity")

    def get_total_quantity(self):
        """
        Get the total quantity of all items in the inventory.

        Returns:
            int: The total quantity of all items.
        """
        return sum(attributes.get("quantity") for attributes in self.item_stack.values())

    def add_item_stack_attribute(self, item: Item, attribute: str, value: any):
        """
        Add an attribute to an item stack in the inventory.

        Args:
            item (Item): The item.
            attribute (str): The name of the attribute.
            value (any): The value of the attribute.
        """
        assert item in self.item_stack, "Item not found"
        self.item_stack.get(item).update({attribute: value})

    def update_item_stack_attribute(self, item: Item, attribute: str, value: any):
        """
        Update an attribute of an item stack in the inventory.

        Args:
            item (Item): The item.
            attribute (str): The name of the attribute.
            value (any): The value of the attribute.
        """
        assert item in self.item_stack, "Item not found"
        assert attribute in self.item_stack.get(item), "Attribute not found"
        self.add_item_stack_attribute(item, attribute, value)

    def get_item_stack_attribute(self, item: Item, attribute: str):
        """
        Get an attribute of an item stack in the inventory.

        Args:
            item (Item): The item.
            attribute (str): The name of the attribute.

        Returns:
            any: The value of the attribute.
        """
        assert item in self.item_stack, "Item not found"
        assert attribute in self.item_stack.get(item), "Attribute not found"
        return self.item_stack.get(item).get(attribute)

    def remove_item_stack_attribute(self, item: Item, attribute: str):
        """
        Remove an attribute from an item stack in the inventory.

        Args:
            item (Item): The item.
            attribute (str): The name of the attribute.
        """
        assert item in self.item_stack, "Item not found"
        assert attribute in self.item_stack.get(item), "Attribute not found"
        self.item_stack.get(item).pop(attribute)

    def get_item_stack_attributes(self, item: Item):
        """
        Get all attributes of an item stack in the inventory.

        Args:
            item (Item): The item.

        Returns:
            dict: A dictionary containing all the attributes.
        """
        assert item in self.item_stack, "Item not found"
        return self.item_stack.get(item)

    def get_item_stack_by_attribute(self, attribute: str, value: any):
        """
        Get an item stack from the inventory by an attribute.

        Args:
            attribute (str): The name of the attribute.
            value (any): The value of the attribute.

        Returns:
            dict[Item, dict[str, any]]: The specific item stack.
        """
        return dict(filter(lambda item_stack: item_stack[1].get(attribute) == value, self.item_stack.items()))

    def get_item_stack_by_attributes(self, attributes: dict):
        """
        Get an item stack from the inventory by multiple attributes.

        Args:
            attributes (dict): A dictionary containing the attributes and their values.

        Returns:
            dict[Item, dict[str, any]]: The specific item stack.
        """
        return dict(filter(lambda item_stack: all(item_stack[1].get(attribute) == value for attribute, value in attributes.items()), self.item_stack.items()), None)

    def get_item_stacks_by_attribute(self, attribute: str, value: any):
        """
        Get all item stacks from the inventory by an attribute.

        Args:
            attribute (str): The name of the attribute.
            value (any): The value of the attribute.

        Returns:
            dict[Item, dict[str, any]]: The specific item stacks.
        """
        return dict(filter(lambda item_stack: item_stack[1].get(attribute) == value, self.item_stack.items()))

    def get_item_stacks_by_attributes(self, attributes: dict):
        """
        Get all item stacks from the inventory by multiple attributes.

        Args:
            attributes (dict): A dictionary containing the attributes and their values.

        Returns:
            dict[Item, dict[str, any]]: The specific item stacks.
        """
        return dict(filter(lambda item_stack: all(item_stack[1].get(attribute) == value for attribute, value in attributes.items()), self.item_stack.items()))

    def to_json(self):
        """
        Convert the inventory object to a JSON object.

        Returns:
            dict: The JSON object.
        """
        return {
            "items": {item.to_json(): quantity for item, quantity in self.item_stack.items()}
        }

    @classmethod
    def from_json(cls, json):
        """
        Create an inventory object from a JSON object.

        Args:
            json (dict): The JSON object.

        Returns:
            Inventory: The inventory object.
        """
        return cls({Item.from_json(item): quantity for item, quantity in json["items"].items()})

    def __str__(self):
        return f"Inventory({'; '.join([f"{quantity.get('quantity')}x {item.get_name()}" for item, quantity in self.item_stack.items()])})"

    def __repr__(self):
        return f"Inventory({self.item_stack})"
