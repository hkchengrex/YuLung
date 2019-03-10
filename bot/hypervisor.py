from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env

from bot.mod.global_info import GlobalInfo
from .util.static_units import UNITS, UnitID
from .util import unit

from bot.mod.expansion_manager import ExpansionManager
from bot.mod.production_manager import ProductionManager
from bot.mod.comabt_manager import CombatManager

class Hypervisor:
    """
    The hypervisor is an mid-level interface.
    """
    def __init__(self, sc2_env: SC2Env):
        self.sc2_env = sc2_env

        self.global_info = GlobalInfo(sc2_env)

        self.expan_man = ExpansionManager(self.global_info)
        self.produ_man = ProductionManager(self.global_info)
        self.comba_man = CombatManager(self.global_info)

        self.global_info.log_game_info("Hypervisor initialized.")

        self.produ_man.build_asap(UNITS[UnitID.Overlord])

    def process(self, obs):
        units = [ru.RawUnit(u) for u in obs.observation.raw_units]
        self.global_info.update(obs)

        self.expan_man.refresh_expansion(units)

        """
        Hardcoded simple rules here
        """
        drones = unit.get_all(units, UNITS[UnitID.Drone]) \
            + unit.get_all(self.produ_man.all_built, UNITS[UnitID.Drone])
        pools = unit.get_all(units, UNITS[UnitID.SpawningPool]) \
            + unit.get_all(self.produ_man.all_built, UNITS[UnitID.SpawningPool])

        # print(self.produ_man.all_built)

        if len(self.produ_man.units_pending) == 0:
            if len(drones) < 12:
                self.produ_man.build_asap(UNITS[UnitID.Drone])
            elif len(pools) == 0:
                self.produ_man.build_asap(UNITS[UnitID.SpawningPool])
            else:
                self.produ_man.build_asap(UNITS[UnitID.Zergling])

        self.comba_man.set_attack_tar(self.expan_man.enemy_expansion[0])
        """
        End of hardcoded simple rules
        """

        # Define priorities here. TODO: Might need to give priorities dynamically
        action = self.comba_man.update(units)
        if action is not None:
            return action

        action = self.produ_man.update(units)
        if action is not None:
            return action

        return None

