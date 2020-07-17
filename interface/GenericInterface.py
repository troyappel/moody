from typing import Callable, Tuple
import gym
from abc import ABC


class GenericInterface(ABC):
    def __init__(self, config, callback_interval):
        pass

    def input_space(self) -> gym.spaces.space:
        pass

    def output_space(self) -> gym.spaces.space:
        pass

    def get_observation(self) -> Tuple:
        pass

    def action_callback(self) -> Callable:
        pass

