from interface.SpotifyInterface import SpotifyInterface
from interface.SoundDeviceInterface import SoundDeviceInterface
from interface.HeartInterface import HeartInterface
import configparser
from ray.rllib.env.external_env import ExternalEnv
from ray.tune.registry import register_env
from ray.rllib.agents.dqn import DQNTrainer
import time
import gym
import ray
from ray.rllib.agents import ppo

from interface.GenericInterface import GenericInterface

INTERVAL = 5
EPISODE_LEN = 3

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

        print(ray.get(self.interfaces[0].reward.remote()))

        observation_space = gym.spaces.Tuple(flatten(
            [ray.get(interface.get_model.remote()).input_space() for interface in self.interfaces]
        ))

        action_space = gym.spaces.Tuple(flatten(
            [ray.get(interface.get_model.remote()).output_space() for interface in self.interfaces]
        ))


        super(MoodyEnvLoop, self).__init__(action_space, observation_space)

    def run(self):
        for interface in self.interfaces:
            interface.init_in_task.remote(interface)

        ready = False
        while not ready:
            try:
                ready = all([ray.get(interface.is_ready.remote()) for interface in interfaces])
            except Exception:
                pass
            if not ready:
                time.sleep(1)

        print("ready!")


        while True:
            eid = self.start_episode()
            for j in range(0, EPISODE_LEN):
                self.interfaces: list[GenericInterface]


                for el in self.interfaces:
                    self.log_returns(eid, ray.get(el.reward.remote()))

                obs = flatten([ray.get(el.get_observation.remote()) for el in self.interfaces])

                actions = self.get_action(eid, obs)

                action_list = list(actions)


                for i in range(0, len(interfaces)):

                    el = self.interfaces[i]

                    model = ray.get(el.get_model.remote())

                    action = action_list[0:len(model.output_space())]

                    el.action_callback.remote(action)

                    action_list = action_list[len(model.output_space()):]

                time.sleep(INTERVAL)



register_env("moody", lambda _: MoodyEnvLoop(interfaces, my_config, INTERVAL))

config = ppo.DEFAULT_CONFIG.copy()
config["num_gpus"] = 0
config["num_workers"] = 0
config["eager"] = False
trainer = ppo.PPOTrainer(config=config, env="moody")

print("here")

for i in range(0, 100):
    print("oogaboogho")
    print(i)
    result = trainer.train()
    print("Iteration {}, reward {}, timesteps {}".format(
        i, result["episode_reward_mean"], result["timesteps_total"]))