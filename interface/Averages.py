# Upon instantiation, can specify how to take averages of different fields

import math
from enum import Enum, auto
import json

class METHODS(Enum):
    MAX = auto()
    MIN = auto()
    MEAN = auto()
    MS = auto()
    EXP = auto()
    CUST = auto()
    PASS = auto()


# Upon instantiation, can specify how to take averages of different fields
class Smoother(object):

    mandatory_kwargs = {
        METHODS.EXP: [
            "alpha"
        ],
        METHODS.CUST: [
            "function"
        ]
    }

    def __init__(self, method, **kwargs):
        self.method = method
        self.kwargs = kwargs

        # Check if required kwargs are here
        if method in self.mandatory_kwargs.keys() \
            and self.mandatory_kwargs[method] \
            and not set(self.mandatory_kwargs[method]) == set(kwargs.keys()):
            raise Exception("Invalid kwargs: use " + ", ".join(self.mandatory_kwargs[method]))

        self.function = None
        self.alpha = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    # Data should be python list
    def evaluate(self, data, prev_val):
        if self.method == METHODS.MAX:
            return max(data)
        elif self.method == METHODS.MIN:
            return min(data)
        elif self.method == METHODS.MEAN:
            return sum(data) / len(data)
        elif self.method == METHODS.MS:
            return sum([x**2 for x in data])
        elif self.method == METHODS.EXP:
            first = prev_val
            for datum in data:
                first = datum * self.alpha + (1 - self.alpha) * first
            return first
        elif self.method == METHODS.CUST:
            return self.function(data)
        elif self.method == METHODS.PASS:
            if isinstance(data, list):
                raise Exception("Cannot pass-through a non-singleton value")
            return data
        else:
            raise Exception("Unsupported smoothing function.")

    def __str__(self):
        return self.method.name + "_" + json.dumps(self.kwargs)
