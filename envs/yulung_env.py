import logging

import numpy as np

from pysc2.agents import base_agent
from pysc2.lib import actions, features
from pysc2.env import sc2_env
from feature.py_feature import FeatureTransform
from feature.py_action import ActionTransform
from pysc2.env.environment import StepType
import gym
from bot.agent import YuLungAgent
from gym import spaces
from envs.base_env import SC2BaseEnv
from bot.hypervisor import Hypervisor

# With reference from https://github.com/islamelnabarawy/sc2gym/blob/master/sc2gym/envs/sc2_game.py

FUNCTIONS = actions.FUNCTIONS
PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
PLAYER_RELATIVE_SCALE = features.SCREEN_FEATURES.player_relative.scale


class YuLungEnv(gym.Env):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

        self._env = None
        self._episode = 0
        self._num_step = 0
        self._epi_reward = 0
        self.sc2_env = None

        self._action_space = None
        self._observation_space = None
        self.feature_transform = None
        self.action_transform = None
        self.obs = None

        self.agent = None

        self.available_actions = []

        import sys
        from absl import flags
        FLAGS = flags.FLAGS
        FLAGS(sys.argv[0:1])

        # print("Init called")

    def reset(self):
        if self._env is None:
            self._init_env()

        # self._log_episode_info()
        self._episode += 1
        self._num_step = 0
        self._epi_reward = 0

        # logger.info("Episode %d starting...", self._episode)
        obs = self._env.reset()[0]
        self.available_actions = obs.observation['available_actions']

        obs = self._env.step([actions.FunctionCall(FUNCTIONS.no_op.id, [])])[0]
        self.obs = obs
        self.get_agent().reset()

        return self._process_obs(obs)

    def get_agent(self):
        if self.agent is None:
            self.agent = YuLungAgent(self.sc2_env)
            return self.agent
        else:
            return self.agent

    def step(self, action):
        self._num_step += 1
        # self.agent.set_action(action)
        # if action[0] not in self.available_actions:
        obs = self._env.step([actions.FunctionCall(FUNCTIONS.no_op.id, [])])[0]
        # else:
        #     obs = self._env.step([actions.FunctionCall(*action)])[0]
        self.available_actions = obs.observation.available_actions
        self._epi_reward += obs.reward

        if obs is None:
            return None, 0, True, {}
        self.obs = obs

        reward = obs.reward
        done = obs.step_type == StepType.LAST

        obs = self._process_obs(obs)

        return obs, reward, done, {}

    def close(self):
        # self._log_episode_info()
        if self._env is not None:
            self._env.close()

        super().close()

        # print("Close called")

    def _init_env(self):
        args = {**self.kwargs}
        # logger.debug("Initializing SC2Env: %s", args)
        self._env = sc2_env.SC2Env(**args)
        self.sc2_env = self._env

    # def _log_episode_info(self):
    #     if self._episode > 0:
    #         logger.info("Episode %d ended with reward %d after %d steps.",
    #                     self._episode, self._epi_reward, self._num_step)

    def _process_obs(self, obs):
        # obs = np.zeros(self.observation_space.shape)
        screens, discrete_info = self.feature_transform.transform(obs)
        return {"feature_screen": screens,
                "info_discrete": discrete_info,
                }

        # def _process_action(self, action):
        #     return [FUNCTIONS.Move_screen.id, [0], action]

    def _process_action(self, action):
        action = self.action_transform.transform(action)
        return action

    @property
    def observation_space(self):
        if self._observation_space is None:
            self._observation_space = self._get_observation_space()
        return self._observation_space

    def _get_observation_space(self):
        self.feature_transform = FeatureTransform(self.observation_spec[0]["feature_screen"][1:])
        space = spaces.Dict({
            "feature_screen": spaces.Box(low=0, high=500, shape=self.feature_transform.screen_shape,
                                         dtype=np.float32),
            "info_discrete": spaces.Box(low=self.feature_transform.low, high=self.feature_transform.high,
                                        dtype=np.float32),
        })
        return space

    @property
    def action_space(self):
        if self._action_space is None:
            self._action_space = self._get_action_space()
        return self._action_space

    def _get_action_space(self):
        self.action_transform = ActionTransform()
        space = spaces.Dict({
            "continous_output": spaces.Box(low=self.action_transform.low, high=self.action_transform.high,
                                           dtype=np.int32),
            "discrete_output": spaces.MultiDiscrete(self.action_transform.discrete_space)
        })
        return space

    def get_featurem_map(self):
        return 1

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


class YuLungSimple64Env(YuLungEnv):
    def __init__(self, **kwargs):
        super().__init__(map_name='Simple64', visualize=True, **kwargs)