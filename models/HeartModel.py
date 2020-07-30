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
            gym.spaces.Box(low=np.array([0, 0, 0], dtype=np.float16),
                           high=np.array([255, 255, 255], dtype=np.float16),
                           dtype=np.float16)
        )
    }

    output_fields = {}
