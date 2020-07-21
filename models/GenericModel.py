from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod


class GenericModel(ABC):

    # List of fields and their spaces
    # 'None' if not listed
    @abstractmethod
    @property
    def fields(self):
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
        space_list = [k for k, v in self.fields if v is not None]
        return "_".join



