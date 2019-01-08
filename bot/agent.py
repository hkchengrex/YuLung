from pysc2.agents import base_agent
from pysc2.lib import actions

from .hypervisor import Hypervisor
from bot.util.game_logger import GameLogger

FUNCTIONS = actions.FUNCTIONS


class YuLungAgent(base_agent.BaseAgent):
    """
    The top level of decision making.
    """

    def reset(self):
        super(YuLungAgent, self).reset()

        self.logger = GameLogger(self.sc2_env)
        self.hypervisor = Hypervisor(self.sc2_env, self.logger)

    def step(self, obs):
        super(YuLungAgent, self).step(obs)

        self.hypervisor.process(obs)

        return FUNCTIONS.no_op()
