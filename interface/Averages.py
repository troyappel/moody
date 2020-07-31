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

        self.prev_val = 0

        for k, v in kwargs.items():
            setattr(self, k, v)

    # Data should be python list
    def evaluate(self, data):
        return_val = None
        if self.method == METHODS.MAX:
            return_val = max(data)
        elif self.method == METHODS.MIN:
            return_val = min(data)
        elif self.method == METHODS.MEAN:
            return_val = sum(data) / len(data)
        elif self.method == METHODS.MS:
            return_val = sum([x**2 for x in data])/len(data)
        elif self.method == METHODS.EXP:
            first = self.prev_val
            for datum in data:
                first = datum * self.alpha + (1 - self.alpha) * first
            return_val = first
        elif self.method == METHODS.CUST:
            return_val = self.function(data)
        elif self.method == METHODS.PASS:
            if isinstance(data, list):
                raise Exception("Cannot pass-through a non-singleton value")
            return_val = data
        else:
            raise Exception("Unsupported smoothing function.")

        # Failsafe in case we are given no data in a period of time, just return previous value
        if not return_val:
            return_val = self.prev_val

        self.prev_val = return_val

        return return_val

    def __str__(self):
        return self.method.name + "_" + json.dumps(self.kwargs)
