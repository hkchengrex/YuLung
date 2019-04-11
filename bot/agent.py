import pysc2.lib
from pysc2.agents import base_agent
from pysc2.lib import actions

from .hypervisor import Hypervisor

FUNCTIONS = actions.FUNCTIONS


class YuLungAgent(base_agent.BaseAgent):
    """
    The top level of decision making.
    """

    def __init__(self, sc2_env):
        super().__init__(sc2_env)
        self.action = None

    def reset(self):
        super(YuLungAgent, self).reset()

        self.hypervisor = Hypervisor(self.sc2_env)

    def step(self, obs):
        super(YuLungAgent, self).step(obs)

        try:
            action = self.hypervisor.process(self.action, obs)
        except pysc2.lib.protocol.ProtocolError as e:
            action = None
            print('Protocol exception caught in base agent', e)

        if action is not None:
            return action

        return FUNCTIONS.no_op()

    def set_action(self, action):
        self.action = action
