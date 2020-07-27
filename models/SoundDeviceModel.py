from .GenericModel import GenericModel
import gym
from interface import Averages
import numpy as np


class SoundDeviceModel(GenericModel):
    def __init__(self, **kwargs):
        super(SoundDeviceModel, self).__init__(**kwargs)

    input_fields = {
        "ambientNoise": (
            Averages.Smoother(Averages.METHODS.MEAN),
            gym.spaces.Box(low=np.array([0], dtype=np.float16),
                           high=np.array([255], dtype=np.float16),
                           dtype=np.float16)
        )
}

    output_fields = {}
