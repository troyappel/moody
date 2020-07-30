from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod
from enum import Enum, auto
from .Averages import Smoother, METHODS
import numpy as np

def flatten(l):
    return [item for sublist in l for item in sublist]

class GenericInterface(ABC):

    def __init__(self, config, callback_interval, model):
        self.config = config
        self.callback_interval = callback_interval
        self.model = model

        self.is_ready = False

        self.prev_vals = {}

    # Dict of {field: iterable or singleton}
    @abstractmethod
    def get_interval_data(self, self_actor) -> list:
        pass

    def init_in_task(self, self_actor) -> None:
        return

    def ready(self) -> None:
        if not self.is_ready:
            print(self.__class__, " ready!")
        self.is_ready = True

    def is_ready(self):
        return self.is_ready

    # Tuple of values, in key-sorted order
    def get_observation(self) -> list:
        data = self.get_interval_data()

        res_list = []

        for k, v in data.items():
            v_arr = np.array(v, dtype=np.float16)

            averages = None
            #
            if v_arr.ndim > 0:
                averages = np.apply_along_axis(self.model.smoothers[k].evaluate, 0, v)
            elif v_arr.ndim == 0:
                averages = self.model.smoothers[k].evaluate(v)
            # else:
            #     averages = v


            # # Array might be 0-dimensional -- gym space expects an array or list for Box
            # if isinstance(v, np.ndarray):
            #     if isinstance(self.model.input_fields[k][1], gym.spaces.Box):
            #         if v.size == 1:
            #             averages = v.reshape(1)

            # if isinstance(averages, float):
            #     averages = [float(averages)]

            # assert self.model.input_fields[k][1].contains(averages)

            res_list.append(list(averages))

        return flatten(res_list)

        # return np.array(flatten(res_list), dtype=np.float16)

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
