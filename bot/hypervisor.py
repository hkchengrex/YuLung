from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env

from bot.util.game_logger import GameLogger

from .global_info import GlobalInfo

from .expansion_manager import ExpansionManager
from .production_manager import ProductionManager


class Hypervisor:
    """
    The hypervisor is an mid-level interface.
    """
    def __init__(self, sc2_env: SC2Env):
        self.sc2_env = sc2_env

        self.global_info = GlobalInfo(sc2_env)

        self.expan_man = ExpansionManager(self.global_info)
        self.produ_man = ProductionManager(self.global_info)

        self.global_info.log_game_info("Hypervisor initialized.")

    def process(self, obs):
        units = [ru.RawUnit(u) for u in obs.observation.raw_units]
        self.global_info.update(obs)

        self.expan_man.refresh_expansion(units)
        return self.produ_man.update(units)



