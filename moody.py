from interface.SpotifyInterface import SpotifyInterface
from interface.SoundDeviceInterface import SoundDeviceInterface
from interface.HeartInterface import HeartInterface
import configparser
from ray.rllib.env.external_env import ExternalEnv
from ray.tune.registry import register_env
from ray.rllib.agents import sac
import time
import gym
import ray
from ray.rllib.agents import ppo

import numpy as np

from interface.GenericInterface import GenericInterface

INTERVAL = 5
EPISODE_LEN = 20

my_config = configparser.ConfigParser()
my_config.read('config.txt')

ray.init()

interfaces = [
    SpotifyInterface,
    # SoundDeviceInterface,
    HeartInterface
]

def flatten(l):
    return [item for sublist in l for item in sublist]

def get_remote(object, function, *args, **kwargs):
    return ray.get(getattr(object, function).remote())(*args, **kwargs)



class MoodyEnvLoop(ExternalEnv):
    def __init__(self, interface_classes, _config, _interval):
        self.stepcount = 0

        interfaces = [ray.remote(interface_class).remote(_config, _interval) for interface_class in interface_classes]

        self.interfaces: list [GenericInterface]
        self.interfaces = sorted(interfaces, key=lambda x: type(x).__name__)

        low_in = flatten([ray.get(interface.get_model.remote()).input_space()[0] for interface in self.interfaces])
        high_in = flatten([ray.get(interface.get_model.remote()).input_space()[1] for interface in self.interfaces])

        print([ray.get(interface.get_model.remote()).input_space()[0] for interface in self.interfaces])
        observation_space = gym.spaces.Box(
            low=np.array(low_in, dtype=np.float16), high=np.array(high_in, dtype=np.float16), dtype=np.float16)

        low_out = flatten([ray.get(interface.get_model.remote()).output_space()[0] for interface in self.interfaces])
        high_out = flatten([ray.get(interface.get_model.remote()).output_space()[1] for interface in self.interfaces])

        action_space = gym.spaces.Box(
            low=np.array(low_out, dtype=np.float16), high=np.array(high_out, dtype=np.float16), dtype=np.float16)

        super(MoodyEnvLoop, self).__init__(action_space, observation_space)

    def run(self):
        for interface in self.interfaces:
            interface.init_in_task.remote(interface)

        ready = False
        while not ready:
            try:
                ready = all([ray.get(interface.is_ready.remote()) for interface in self.interfaces])
                print("Ready: ", ready)
            except Exception as e:
                print(e)
            if not ready:
                time.sleep(5)

        print("ready!")


        while True:
            obs = None
            eid = self.start_episode()
            for j in range(0, EPISODE_LEN):
                self.interfaces: list[GenericInterface]

                for el in self.interfaces:
                    reward = ray.get(el.reward.remote())
                    print(reward)
                    self.log_returns(eid, ray.get(el.reward.remote()))

                print("taking observation")

                obs = flatten([ray.get(el.get_observation.remote()) for el in self.interfaces])

                actions = self.get_action(eid, obs)

                action_list = list(actions)


                for i in range(0, len(interfaces)):

                    el = self.interfaces[i]

                    model = ray.get(el.get_model.remote())

                    action = action_list[0:len(model.output_space()[0])]

                    action_dict = model.values_list_to_dict(action, False)

                    el.action_callback.remote(action_dict)

                    action_list = action_list[len(model.output_space()[0]):]

                for el in self.interfaces:
                    ray.get(el.clear_observation.remote())

                time.sleep(INTERVAL)

            self.end_episode(eid, obs)



register_env("moody", lambda _: MoodyEnvLoop(interfaces, my_config, INTERVAL))

config = sac.DEFAULT_CONFIG.copy()
config["num_gpus"] = 0
config["num_workers"] = 0
config["eager"] = False
config["timesteps_per_iteration"] = 20
config["learning_starts"] = 60
config['use_state_preprocessor'] = True

# Required to prevent rllib from thinking we subclass gym env
config["normalize_actions"] = False

trainer = sac.SACTrainer(config=config, env="moody")

print("Beginning training.")

for i in range(0, 100):
    print(i)
    result = trainer.train()
    print("Iteration {}, reward {}, timesteps {}".format(
        i, result["episode_reward_mean"], result["timesteps_total"]))
    trainer.save()