from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod
from enum import Enum, auto
from .Averages import Smoother, METHODS
import numpy as np
import sounddevice as sd

import ray

from .GenericInterface import GenericInterface
from models.SoundDeviceModel import SoundDeviceModel


class SoundDeviceInterface(GenericInterface):

    def __init__(self, config, callback_interval, **kwargs):

        self.sound_lst = [0]

        self.stream = None

        super(SoundDeviceInterface, self).__init__(config, callback_interval, SoundDeviceModel(**kwargs))

    def init_in_task(self, self_actor):
        self.stream = sd.Stream(callback=self.inc_sound)
        self.stream.start()

    # Dict of {field: iterable or singleton}
    def get_interval_data(self) -> dict:
        return {
            "ambientNoise": np.array(self.sound_lst, dtype=np.float16)
        }

    def clear_observation(self) -> None:
        self.sound_lst = [0]

    def action_callback(self, action):
        return

    def reward(self) -> float:
        return 0

    # Internal
    def inc_sound(self, indata, outdata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 10
        self.sound_lst.append(volume_norm)


