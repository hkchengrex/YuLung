from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env

from bot.util.game_logger import GameLogger
from bot.util.resources import Resources, player_to_resources

from .game_module import GameModule
from .expansion_manager import ExpansionManager
from .production_manager import ProductionManager


class Hypervisor(GameModule):
    """
    The hypervisor is an mid-level interface.
    """
    def __init__(self, sc2_env: SC2Env, logger: GameLogger):
        super(Hypervisor, self).__init__(sc2_env, logger)

        self.expan_man = ExpansionManager(sc2_env, logger)
        self.produ_man = ProductionManager(sc2_env, logger)

        self.logger.log_game_info("Hypervisor initialized.")

    def process(self, obs):
        units = [ru.RawUnit(u) for u in obs.observation.raw_units]
        resources = player_to_resources(obs.observation.player)

        self.expan_man.refresh_expansion(units)
        self.produ_man.update(units, resources)



