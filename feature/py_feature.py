import numpy as np
from pysc2.lib import actions
import common.utils as U
from pysc2.lib import actions, features

PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
PLAYER_RELATIVE_SCALE = features.SCREEN_FEATURES.player_relative.scale

from common import utils

class FeatureTransform:

    def __init__(self, screen_shape):
        """
        Define Observation Space
        """
        """
        Define the screen space
        """
        ###
        self.n_feature_screen = 1
        self.screen_shape = (self.n_feature_screen,) + screen_shape
        ###

        """
        Define the discrete space
        """
        ###
        self.high = np.array([200, 200, 200, 200, 200])
        self.low = np.array([0, 0, 0, 0, 0])
        ###
        self.n_discrete_info = len(self.high)

    def transform(self, obs):
        feature_screen = obs.observation['feature_screen']

        screens = np.zeros(self.screen_shape, dtype=np.int32)
        discrete_infos = np.zeros(self.n_discrete_info, dtype=np.int32)

        """
        Define the observation space mapping
        """
        #################Define#########################

        feature_screen[0] = feature_screen['player_relative']
        discrete_infos[0] = obs.observation["player"][0]
        discrete_infos[1] = obs.observation["player"][1]
        discrete_infos[2] = obs.observation["player"][2]
        discrete_infos[3] = obs.observation["player"][3]
        discrete_infos[4] = obs.observation["player"][4]
        ###################################################

        return screens, discrete_infos



