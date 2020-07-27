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

            averages = None

            if isinstance(v, np.ndarray) and v.ndim > 0:
                averages = np.apply_along_axis(self.model.smoothers[k].evaluate, 0, v)
            elif isinstance(v, np.ndarray) and v.ndim == 0:
                averages = self.model.smoothers[k].evaluate(v)
            else:
                averages = v

            print(averages)


            # Array might be 0-dimensional -- gym space expects an array or list for Box
            if isinstance(averages, np.ndarray):
                if isinstance(self.model.input_fields[k][1], gym.spaces.Box):
                    if averages.size == 1:
                        averages = averages.reshape(1)

            # if isinstance(averages, float):
            #     averages = [float(averages)]

            print(averages)
            print(self.model.input_fields[k][1])
            print(type(averages))

            assert self.model.input_fields[k][1].contains(averages)

            res_list.append(averages)

        return tuple(res_list)

    # Order of calls:
    # get_interval_data -> action_callback -> reward -> clear_observation

    @abstractmethod
    def clear_observation(self) -> None:
        pass

    @abstractmethod
    def action_callback(self, action) -> None:
        pass

    @abstractmethod
    def reward(self) -> float:
        pass

    def get_model(self):
        return self.model
