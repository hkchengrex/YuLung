import logging

from pysc2.env.sc2_env import SC2Env


class GameLogger:

    def __init__(self, sc2_env: SC2Env):
        self.sc2_env = sc2_env

    def log_game_info(self, message: str, show_in_chat=True):
        logging.info(message)
        if show_in_chat:
            self.sc2_env.send_chat_messages(message)
