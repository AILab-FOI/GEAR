from dataclasses import dataclass, asdict

@dataclass
class Service:
    name: str
    price: float | int = None
    duration: int = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    @classmethod
    def random(cls):
        import random
        import numpy as np
        return cls(random.choice(["A", "B", "C"]), random.randint(1, 10), random.randint(1, 10))