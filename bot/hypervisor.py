from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env

from bot.util.game_logger import GameLogger

from .global_info import GlobalInfo
from .util.static_units import UNITS, UnitID
from .util import unit

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

        """
        Hardcoded simple rules here
        """
        drones = unit.get_all(units, UNITS[UnitID.Drone])
        pools = unit.get_all(units, UNITS[UnitID.SpawningPool])

        if len(self.produ_man.units_pending) == 0:
            if len(drones) < 12 and len(pools) == 0:
                self.produ_man.build_asap(UNITS[UnitID.Drone])
            elif len(pools) == 0:
                self.produ_man.build_asap(UNITS[UnitID.SpawningPool])
            else:
                self.produ_man.build_asap(UNITS[UnitID.Zergling])

        """
        End of hardcoded simple rules
        """

        # Define priorities here. TODO: Might need to give priorities dynamically
        action = self.produ_man.update(units)
        if action is not None:
            return action

        return None



