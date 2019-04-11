import logging

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.env import sc2_env
from pysc2.env.environment import StepType

import gym
import numpy as np

# With reference from https://github.com/islamelnabarawy/sc2gym/blob/master/sc2gym/envs/sc2_game.py

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestBaseEnv(gym.Env):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

        self._env = None
        self._episode = 0
        self._num_step = 0
        self._epi_reward = 0

        self.available_actions = []

        import sys
        from absl import flags
        FLAGS = flags.FLAGS
        FLAGS(sys.argv[0:1])

        print("Init called")

    def reset(self):
        if self._env is None:
            self._init_env()

        self._log_episode_info()
        self._episode += 1
        self._num_step = 0
        self._epi_reward = 0

        logger.info("Episode %d starting...", self._episode)
        # obs = self._env.reset()[0]
        # self.available_actions = obs.observation['available_actions']

        return np.zeros((84, 84, 22))

    def step(self, action):
        self._num_step += 1

        # if action[0] not in self.available_actions:
        #     logger.warning("Invalid action: %s", action)
        
        # obs = self._env.step([actions.FunctionCall(action[0], action[1:])])[0]
        # self.available_actions = obs.observation.available_actions
        # self._epi_reward += obs.reward
        
        # return obs, obs.reward, obs.step_type == StepType.LAST, {}

        return np.zeros((84, 84, 22)), 0, False, {}

    def close(self):
        self._log_episode_info()
        # if self._env is not None:
        #     self._env.close()

        super().close()

        print("closed called")

    def _init_env(self):
        args = {**self.kwargs}
        logger.debug("Initializing Test ENV: %s", args)
        # self._env = sc2_env.SC2Env(**args)

    def _log_episode_info(self):
        if self._episode > 0:
            logger.info("Episode %d ended with reward %d after %d steps.",
                        self._episode, self._epi_reward, self._num_step)

    @property
    def settings(self):
        return self.kwargs

    @property
    def action_spec(self):
        if self._env is None:
            self._init_env()
        return self._env.action_spec()

    @property
    def observation_spec(self):
        if self._env is None:
            self._init_env()
        return self._env.observation_spec()

    @property
    def episode(self):
        return self._episode

    @property
    def num_step(self):
        return self._num_step

    @property
    def episode_reward(self):
        return self._epi_reward

    @property
    def observation_space(self):
        return gym.spaces.Box(low=0, high=255, shape=(84, 84, 22), dtype=np.int32)

    @property
    def action_space(self):
        return gym.spaces.Discrete(1000)

