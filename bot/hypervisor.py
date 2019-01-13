from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env

from bot.util.game_logger import GameLogger
from bot.util.resources import Resources, player_to_resources

from .low_level_module import LowLevelModule
from .expansion_manager import ExpansionManager
from .production_manager import ProductionManager


class Hypervisor:
    """
    The hypervisor is an mid-level interface.
    - Contains resources info
    - Logging ability
    Its reference is passed to low-level objects.
    """
    def __init__(self, sc2_env: SC2Env, logger: GameLogger):
        self.sc2_env = sc2_env
        self.logger = logger

        self.expan_man = ExpansionManager(self)
        self.produ_man = ProductionManager(self)
        self.resources = None

        self.logger.log_game_info("Hypervisor initialized.")

    def process(self, obs):
        units = [ru.RawUnit(u) for u in obs.observation.raw_units]
        self.resources = player_to_resources(obs.observation.player)

        self.expan_man.refresh_expansion(units)
        self.produ_man.update(units)



