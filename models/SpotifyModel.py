from .GenericModel import GenericModel
import gym
from interface import Averages
import numpy as np


class SpotifyModel(GenericModel):
    def __init__(self, **kwargs):
        super(SpotifyModel, self).__init__(**kwargs)

    input_fields = {
        "attributes": (
            Averages.Smoother(Averages.METHODS.PASS),
            gym.spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 50], dtype=np.float16), high=np.array([1, 1, 1, 1, 1, 1, 1, 255, 100], dtype=np.float16),
                           dtype=np.float16)
        ),
        "mode": (
            Averages.Smoother(Averages.METHODS.PASS),
            gym.spaces.Discrete(2)
        )
    }

    output_fields = {
        "attributes":
            gym.spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 50], dtype=np.float16), high=np.array([1, 1, 1, 1, 1, 1, 1, 255, 100], dtype=np.float16),
                           dtype=np.float16),
        "mode":
            gym.spaces.Discrete(2)
    }
