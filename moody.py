from interface.SpotifyInterface import SpotifyInterface
from interface.SoundDeviceInterface import SoundDeviceInterface
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


interfaces = [
    SpotifyInterface(my_config, INTERVAL),
    SoundDeviceInterface(my_config, INTERVAL)
]

flatten = lambda l: [item for sublist in l for item in sublist]

class MoodyEnvLoop(ExternalEnv):
    def __init__(self, interfaces):
        self.stepcount = 0

        self.interfaces: list [GenericInterface]
        self.interfaces = sorted(interfaces, key=lambda x: type(x).__name__)


        observation_space = gym.spaces.Tuple(flatten([interface.model.input_space() for interface in self.interfaces]))
        action_space = gym.spaces.Tuple(flatten([interface.model.output_space() for interface in self.interfaces]))


        print("making env")
        super(MoodyEnvLoop, self).__init__(action_space, observation_space)
        print("made env loop")

    def run(self):
        print("running")
        while True:
            eid = self.start_episode()
            for j in range(0, EPISODE_LEN):
                self.interfaces: list[GenericInterface]

                for el in self.interfaces:
                    self.log_returns(eid, el.reward())

                obs = flatten([el.get_observation() for el in self.interfaces])

                print(obs)
                print(self.observation_space.sample())

                actions = self.get_action(eid, obs)

                print(actions)
                print(self.action_space.sample())

                action_list = list(actions)

                for i in range(0, len(interfaces)):
                    el = self.interfaces[i]
                    action = action_list[0:len(el.model.output_space())]
                    el.action_callback(action)

                    action_list = action_list[len(el.model.output_space()):]

                time.sleep(INTERVAL)


ray.init()

config = ppo.DEFAULT_CONFIG.copy()

register_env("moody", lambda _: MoodyEnvLoop(interfaces))

config = ppo.DEFAULT_CONFIG.copy()
config["num_gpus"] = 0
config["num_workers"] = 1
config["eager"] = False
trainer = ppo.PPOTrainer(config=config, env="moody")

print("here")

for i in range(0, 100):
    print("oogaboogho")
    print(i)
    result = trainer.train()
    print("Iteration {}, reward {}, timesteps {}".format(
        i, result["episode_reward_mean"], result["timesteps_total"]))