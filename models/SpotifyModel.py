from .GenericModel import GenericModel
import gym
from interface import Averages
import numpy as np


class SpotifyModel(GenericModel):
    def __init__(self, **kwargs):
        super(SpotifyModel, self).__init__(**kwargs)

    input_fields = {
        'attributes': (
            Averages.Smoother(Averages.METHODS.PASS),
            [0, 0, 0, 0, 0, -60, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 1, 1, 255, 100, 1]
        )
    }

    input_fields = {
        'attributes': (
            [0, 0, 0, 0, 0, -60, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 1, 1, 255, 100, 1]
        )
    }

