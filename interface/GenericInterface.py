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

    # Dict of {field: iterable or singleton}
    @abstractmethod
    def get_interval_data(self) -> Tuple:
        pass

    def get_observation(self) -> Tuple:
        data = self.get_interval_data()

        res_list = []

        for k, v in data:
            averages = np.apply_along_axis(self.model.smoothers[k], 0, v)

            assert self.model.input_fields[k][0].contains(averages)

            res_list.append(averages)

        return tuple(res_list)



    @abstractmethod
    def clear_observation(self) -> None:
        pass

    @abstractmethod
    def action_callback(self) -> Callable:
        pass

