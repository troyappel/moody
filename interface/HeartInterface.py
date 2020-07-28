from typing import Callable, Tuple
import gym
from abc import ABC, abstractmethod
from enum import Enum, auto
from .Averages import Smoother, METHODS
import numpy as np
import sounddevice as sd

import threading

import ray

from .GenericInterface import GenericInterface
from models.HeartModel import HeartModel

import pywintypes
import win32pipe, win32file
import time

@ray.remote
class PipeQueryLoop(object):
    def __init__(self, recipient):
        self.recipient = recipient
        pass

    def run(self):
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
                    self.recipient.get_from_pipe.remote(resp)

            except pywintypes.error as e:
                if e.args[0] == 2:
                    print("no pipe, trying again in a sec")
                    time.sleep(1)
                elif e.args[0] == 109:
                    print("broken pipe, bye bye")




class HeartInterface(GenericInterface):
    def __init__(self, config, callback_interval, **kwargs):

        self.queryloop = None

        super(HeartInterface, self).__init__(config, callback_interval, HeartModel(**kwargs))

    def init_in_task(self):
        self.queryloop = PipeQueryLoop.remote(self)
        self.queryloop.run.remote()

    def get_interval_data(self):
        return {"metrics": [0, 0, 0]}

    def clear_observation(self):
        pass

    def action_callback(self, action):
        pass

    def reward(self):
        return 0.0

    def get_from_pipe(self, data):
        print("received it!")
        print(data)
