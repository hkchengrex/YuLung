import numpy as np
from pysc2.lib import features

from bot.util.unit_ids import *
from bot.macro_actions import NUMBER_EXPANSIONS

PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
PLAYER_RELATIVE_SCALE = features.SCREEN_FEATURES.player_relative.scale


class FeatureTransform:

    @staticmethod
    def n_screen():
        return 6

    @staticmethod
    def n_non_screen_cate():
        return NUMBER_EXPANSIONS + \
               len(ZERG_TECH_BUILDINGS) + \
               len(TECH_BUILDING_TYPE)

    @staticmethod
    def n_non_screen():
        return FeatureTransform.n_non_screen_cate() + \
            7  # Extractors, time, drone deficiency, mineral, gas, food usage, food cap

    def __init__(self, screen_shape):

        # (obs) Define Number of Screen Observations ##
        self.n_screen = FeatureTransform.n_screen()
        # ####

        # (obs) Define Non Screen Observation Space, the number in the array just randomly give is ok ##
        # The size the array must be equal to the number of non_Screen Observations ##
        self.n_non_screen = FeatureTransform.n_non_screen()

        self.high = np.array([100000] * self.n_non_screen)
        self.low = np.array([0] * self.n_non_screen)
        # ####

        self.screen_shape = (self.n_screen,) + screen_shape
        self.n_info = len(self.high)

    def transform(self, obs, extra_obs):
        # feature_screen = obs.observation['feature_screen']

        # (obs) Refer to __init__, input the some observations to NN ##

        screens = np.zeros(self.screen_shape, dtype=np.float)
        infos = np.zeros(self.n_info, dtype=np.float)

        screens[0] = obs.observation.feature_screen.height_map
        screens[1] = obs.observation.feature_screen.visibility_map
        screens[2] = obs.observation.feature_screen.creep
        screens[3] = obs.observation.feature_screen.player_relative
        screens[4] = obs.observation.feature_screen.unit_density_aa
        screens[5] = obs.observation.feature_screen.unit_hit_points

        if extra_obs is not None:

            infos[:] = extra_obs['expansions'] + extra_obs['tech'] \
                        + extra_obs['scout'] + [extra_obs['extractors']] \
                        + [extra_obs['time']] + [extra_obs['drone']] \
                        + [extra_obs['minerals']] + [extra_obs['gas']] \
                        + [extra_obs['food_usage']] + [extra_obs['food_cap']]

            # ####

        return screens, infos
