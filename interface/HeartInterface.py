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
            print("Checking for pipe")
            time.sleep(1)
            try:
                handle = win32file.CreateFile(
                    '\\\\.\\pipe\\hrpipetroy22',
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_BYTE, None, None)
                print("Pipe created successfully")
                if res == 0:
                    print(f"SetNamedPipeHandleState return code: {res}")
                while True:
                    try:
                        time.sleep(0.1)
                        resp = win32file.ReadFile(handle, 8)

                        if resp[0] != 0:
                            print(resp)
                            break

                        self.recipient.get_from_pipe.remote(resp[1])
                    except Exception:
                        pass


            except pywintypes.error as e:
                if e.args[0] == 2:
                    print("no pipe, trying again in a sec")
                    time.sleep(1)
                elif e.args[0] == 109:
                    print("broken pipe, bye bye")
                else:
                    print(e.args)
                    print("broken with {}".format(e.args[0]))


            except Exception as e:
                print(e)





class HeartInterface(GenericInterface):
    def __init__(self, config, callback_interval, **kwargs):

        self.events = []

        GenericInterface.__init__(self, config, callback_interval, HeartModel(**kwargs))

    def init_in_task(self, self_actor):
        self.queryloop = PipeQueryLoop.remote(self_actor)
        self.queryloop.run.remote()

    def get_interval_data(self):
        return {
            "metrics": self.events
        }

    def clear_observation(self):
        self.events = []

    def action_callback(self, action):
        pass

    def reward(self):
        print(self.get_observation())
        return 255 - self.get_observation()[0]

    def get_from_pipe(self, data):
        try:
            hr_offset = 0

            event_time = (data[hr_offset + 5] << 8) + (data[hr_offset + 4])
            hr = data[hr_offset + 7]
            beat_count =data[hr_offset + 6]
            self.events.append([hr, 0, 0])

            self.ready()

        except Exception as e:
            print(e)

