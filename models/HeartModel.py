from .GenericModel import GenericModel
import gym
from interface import Averages
import numpy as np


class HeartModel(GenericModel):
    def __init__(self, **kwargs):
        super(HeartModel, self).__init__(**kwargs)

    input_fields = {
        "metrics": (
            # HR, HRV, BREATHING RATE
            Averages.Smoother(Averages.METHODS.EXP, alpha=0.1),
            [0, 0, 0],
            [255, 255, 255]
        )
    }

    output_fields = {}
