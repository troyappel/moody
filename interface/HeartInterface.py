from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod
from enum import Enum, auto
from .Averages import Smoother, METHODS
import numpy as np
import sounddevice as sd

import ray

from .GenericInterface import GenericInterface
from models.HeartModel import HeartModel

import pywintypes
import win32pipe, win32file
import time


class HeartInterface(GenericInterface):
    def __init__(self, config, callback_interval, **kwargs):
        super(HeartInterface, self).__init__(config, callback_interval, HeartModel(**kwargs))

        self.get_packet_loops()

    def get_interval_data(self):
        return 0

    def clear_observation(self):
        pass

    def action_callback(self, action):
        pass

    def reward(self):
        return 0.0

    def get_packet_loops(self):
        while True:
            print("pipe!")
            try:
                handle = win32file.CreateFile(
                    '\\\\.\\pipe\\hrpipetroy',
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_BYTE, None, None)
                if res == 0:
                    print(f"SetNamedPipeHandleState return code: {res}")
                while True:
                    resp = win32file.ReadFile(handle, 64 * 1024)
                    print(f"message: {resp}")
            except pywintypes.error as e:
                if e.args[0] == 2:
                    print("no pipe, trying again in a sec")
                    time.sleep(1)
                elif e.args[0] == 109:
                    print("broken pipe, bye bye")
                    quit = True