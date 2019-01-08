from bot.util.game_logger import GameLogger
from pysc2.env.sc2_env import SC2Env


class GameModule:
    def __init__(self, sc2_env: SC2Env, logger: GameLogger):
        self.sc2_env = sc2_env
        self.logger = logger