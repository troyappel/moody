from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod
from enum import Enum, auto
from .Averages import Smoother, METHODS
import numpy as np


class GenericInterface(ABC):

    def __init__(self, config, callback_interval, model):
        self.config = config
        self.callback_interval = callback_interval
        self.model = model

        self.prev_vals = {}

    # Dict of {field: iterable or singleton}
    @abstractmethod
    def get_interval_data(self) -> dict:
        pass

    # Tuple of values, in key-sorted order
    def get_observation(self) -> Tuple:
        data = self.get_interval_data()

        res_list = []

        for k in sorted(data):
            v = data[k]

            averages = np.apply_along_axis(self.model.smoothers[k].evaluate, 0, v)

            if len(averages) == 1:
                averages = averages[0]

            assert self.model.input_fields[k][1].contains(averages)

            res_list.append(averages)

        return tuple(res_list)

    @abstractmethod
    def clear_observation(self) -> None:
        pass

    @abstractmethod
    def action_callback(self, action) -> Callable:
        pass

