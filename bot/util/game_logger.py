import logging

from pysc2.env.sc2_env import SC2Env


class GameLogger:

    def __init__(self, sc2_env: SC2Env, level=logging.INFO):
        self.sc2_env = sc2_env
        self.logger = logging.getLogger()
        # logging.basicConfig(level=level)

    def log_game_info(self, message: str, show_in_chat=True):
        self.logger.warning(message)
        # if show_in_chat:
        #     self.sc2_env.send_chat_messages([message])

    def log_game_verbose(self, message: str):
        self.logger.debug(message)
