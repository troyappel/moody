from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod

from interface import Averages


class GenericModel(ABC):

    def __init__(self, **kwargs):
        for key, val in kwargs:
            if key not in self.input_fields.keys():
                raise AttributeError(key)

        self.smoothers = {}

        # Type hint
        default_smoother: Averages.Smoother
        for field, (default_smoother, space) in self.input_fields:
            if field in kwargs.keys():
                self.smoothers[field] = kwargs[field]
            elif default_smoother is not None:
                self.smoothers[field] = default_smoother
            else:
                self.smoothers[field] = Averages.METHODS.PASS

    # Dictionary of field: (default_smoother, space)
    @abstractmethod
    @property
    def input_fields(self):
        raise NotImplementedError

    # Dictionary of field: space
    @abstractmethod
    @property
    def output_fields(self):
        raise NotImplementedError

    def space(self) -> gym.spaces.space:
        space_list = [v for _, v in self.fields if v is not None]
        return gym.spaces.Tuple(space_list)

    # Data is shaped like maximal version of fields
    def get_repr(self, data):
        final_repr = []
        for i, (_, v) in enumerate(self.fields):
            if v is None:
                continue

            final_repr.append(data[i])

        return tuple(final_repr)

    def get_unique_name(self):
        field_list = ["(" + k + ", " + v + ")" for k, v in self.smoothers if v is not None]
        return str(self.__class__) + "-" + "_".join(field_list)
