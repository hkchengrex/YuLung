import pysc2.lib
from pysc2.agents import base_agent
from pysc2.lib import actions

from .hypervisor import Hypervisor

FUNCTIONS = actions.FUNCTIONS


class YuLungAgent(base_agent.BaseAgent):
    """
    The top level of decision making.
    """

    def __init__(self, env):
        super().__init__(env)
        self.camera_moved = False
        self.hypervisor = None
        self.macro_action = None

    def reset(self):
        super(YuLungAgent, self).reset()

        self.hypervisor = Hypervisor(self.sc2_env)
        self.camera_moved = False
        self.macro_action = None

    def step(self, obs):
        super(YuLungAgent, self).step(obs)

        if not self.camera_moved:
            self.camera_moved = True
            return FUNCTIONS.move_camera([11, 13])

        try:
            action = self.hypervisor.process(self.macro_action, obs)
        except pysc2.lib.protocol.ProtocolError as e:
            action = None
            print('Protocol exception caught in base agent', e)

        if action is not None:
            return action

        return FUNCTIONS.no_op()

    def set_macro_action(self, macro_action):
        self.macro_action = macro_action
