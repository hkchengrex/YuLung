import logging

import numpy as np

from pysc2.agents import base_agent
from pysc2.lib import actions, features
from pysc2.env import sc2_env
from feature.py_feature import FeatureTransform
from feature.py_action import ActionTransform
import gym
from bot.agent import YuLungAgent
from gym import spaces
from envs.base_env import SC2BaseEnv
from bot.hypervisor import Hypervisor

FUNCTIONS = actions.FUNCTIONS
PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
PLAYER_RELATIVE_SCALE = features.SCREEN_FEATURES.player_relative.scale


# With reference from https://github.com/islamelnabarawy/sc2gym/blob/master/sc2gym/envs/movement_minigame.py

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# f
class SimpleMovementEnv(SC2BaseEnv):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._action_space = None
        self._observation_space = None
        self.feature_transform = None
        self.action_transform = None
        self.obs = None

        self.agent = None

    def get_agent(self):
        if self.agent is None:
            self.agent = YuLungAgent(self.sc2_env)
            return self.agent
        else:
            return self.agent

    def reset(self):
        super().reset()
        obs, _, _, _ = super().step([FUNCTIONS.select_army.id, [0]])
        self.obs = obs
        self.get_agent().reset()
        return self._process_obs(obs)

    def step(self, action):
        self.agent.set_action(action)
        obs, reward, done, info = super().step(self.agent.step(self.obs))
        if obs is None:
            return None, 0, True, {}
        self.obs = obs
        obs = self._process_obs(obs)
        # obs = self._process_obs(None)
        # reward = 0
        # done = False
        # info = {}

        return obs, reward, done, info

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
            "continuous_output": spaces.Box(low=self.action_transform.low, high=self.action_transform.high,
                                           dtype=np.int32),
            "discrete_output": spaces.MultiDiscrete(self.action_transform.discrete_space)
        })
        return space

    def get_featurem_map(self):
        return 1

    '''
    def _get_action_space(self):
        screen_shape = self.observation_spec[0]["feature_screen"][1:]
        return spaces.Discrete(screen_shape[0] * screen_shape[1] - 1)
    '''


class CollectMineralShardsEnv(SimpleMovementEnv):
    def __init__(self, **kwargs):
        super().__init__(map_name='Simple64', **kwargs)
