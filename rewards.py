from pysc2.env.sc2_env import SC2Env

class RewardGiver:
    """
    This thing GIVES YOU REWARDS!
    """
    def __init__(self, sc2_env: SC2Env):
        self.sc2_env = sc2_env

    def step_reward(self, obs):
        # TODO: Love and care
        return 0