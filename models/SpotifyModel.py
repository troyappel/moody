from .GenericModel import GenericModel
import gym
from interface import Averages


class SpotifyModel(GenericModel):
    def __init__(self, **kwargs):
        super(SpotifyModel, self).__init__(**kwargs)

    input_fields = {
        "attributes": (
            Averages.Smoother(Averages.METHODS.PASS),
            gym.spaces.Box(low=[0, 0, 0, 0, 0, 0, 0, 0, 50], high=[1, 1, 1, 1, 1, 1, 1, 255, 100])
        ),
        "mode": (
            Averages.Smoother(Averages.METHODS.PASS),
            gym.spaces.Discrete(2)
        )
    }

    output_fields = {
        "attributes":
            gym.spaces.Box(low=[0, 0, 0, 0, 0, 0, 0, 0, 50], high=[1, 1, 1, 1, 1, 1, 1, 255, 100]),
        "mode":
            gym.spaces.Discrete(2)
    }
