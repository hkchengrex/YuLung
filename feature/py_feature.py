import numpy as np
from pysc2.lib import features

PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
PLAYER_RELATIVE_SCALE = features.SCREEN_FEATURES.player_relative.scale


class FeatureTransform:

    def __init__(self, screen_shape):

        # (obs) Define Number of Screen Observations ##
        self.n_screen = 2
        # ####

        # (obs) Define Non Screen Observation Space, the number in the array just randomly give is ok ##
        # The size the array must be equal to the number of non_Screen Observations ##
        self.high = np.array([200, 200, 200, 200, 200])
        self.low = np.array([0, 0, 0, 0, 0])
        # ####

        self.screen_shape = (self.n_screen,) + screen_shape
        self.n_info = len(self.high)

    def transform(self, obs):
        # feature_screen = obs.observation['feature_screen']

        # (obs) Refer to __init__, input the some observations to NN ##

        screens = np.zeros(self.screen_shape, dtype=np.float)
        infos = np.zeros(self.n_info, dtype=np.float)

        screens[0] = np.random.randint(6, size=(84, 84))
        screens[1] = np.random.random_sample(size=(84, 84))

        infos[0] = obs.observation["player"][0]
        infos[1] = obs.observation["player"][1]
        infos[2] = obs.observation["player"][2]
        infos[3] = obs.observation["player"][3]
        infos[4] = obs.observation["player"][4]

        # ####

        return screens, infos
