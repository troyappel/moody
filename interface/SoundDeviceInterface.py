from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod
from enum import Enum, auto
from .Averages import Smoother, METHODS
import numpy as np
import sounddevice as sd

from .GenericInterface import GenericInterface
from models.SoundDeviceModel import SoundDeviceModel


class SoundDeviceInterface(GenericInterface):

    def __init__(self, config, callback_interval, **kwargs):

        self.sound_lst = []

        f = sd.Stream(callback=self.inc_sound)

        f.start()

        super(SoundDeviceInterface, self).__init__(config, callback_interval, SoundDeviceModel(**kwargs))

    # Dict of {field: iterable or singleton}
    def get_interval_data(self) -> dict:
        return {
            "ambientNoise": np.ndarray(self.sound_lst)
        }

    def clear_observation(self) -> None:
        self.sound_lst = []

    def action_callback(self, action) -> Callable:
        pass

    def reward(self) -> float:
        pass

    # Internal
    def inc_sound(self, indata, outdata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 10
        self.sound_lst.append(volume_norm)
