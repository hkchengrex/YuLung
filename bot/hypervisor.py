from pysc2.env.sc2_env import SC2Env

from bot.mod.comabt_manager import CombatManager
from bot.mod.expansion_manager import ExpansionManager
from bot.mod.global_info import GlobalInfo
from bot.mod.production_manager import ProductionManager
from bot.mod.scout_manager import ScoutManager
from bot.util.helper import *

from bot.mod.worker_manager import WorkerManager


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
        self.scout_man = ScoutManager(self.global_info)
        self.scout_man.go_scout_once()
        self.work_man = WorkerManager(self.global_info)

        self.global_info.log_game_info("Hypervisor initialized.")

        self.produ_man.build_asap(UNITS[UnitID.Overlord])

    def process(self, obs):
        units, units_tag_dict = self.global_info.update(obs)

        hatchery_build_pos = self.expan_man.update_expansion(units, units_tag_dict)

        for pos in hatchery_build_pos:
            self.produ_man.build_asap(UNITS[UnitID.Hatchery], pos)

        self.produ_man.set_base_locations([exp.pos for exp in self.expan_man.own_expansion() if exp.base is not None])

        self.scout_man.set_scout_tar([exp.pos for exp in self.expan_man.expansion])

        """
        Hardcoded simple rules here
        """
        if len(self.expan_man.own_expansion()) < 2:
            self.expan_man.claim_expansion(self.expan_man.get_next_expansion())

        drones = get_all(units, UNITS[UnitID.Drone]) \
                 + get_all(self.produ_man.all_built, UNITS[UnitID.Drone])
        pools = get_all(units, UNITS[UnitID.SpawningPool]) \
                + get_all(self.produ_man.all_built, UNITS[UnitID.SpawningPool])

        # print(self.produ_man.all_built)

        bases = get_all_owned(units, UNITS[UnitID.Hatchery])
        max_drones = len(bases) * 16

        if len(self.produ_man.units_pending) == 0:
            if len(drones) < max_drones:
                self.produ_man.build_asap(UNITS[UnitID.Drone])
            elif len(pools) == 0:
                self.produ_man.build_asap(UNITS[UnitID.SpawningPool])
            else:
                self.produ_man.build_asap(UNITS[UnitID.Zergling])

        self.comba_man.set_attack_tar(self.expan_man.enemy_expansion()[0].pos)
        self.work_man.track(units)
        """
        End of hardcoded simple rules
        """

        # Define priorities here. TODO: Might need to give priorities dynamically
        action = self.comba_man.update(units)
        if action is not None:
            return action
        

        action = self.work_man.assign(units)
        if action is not None:
            return action

        action = self.produ_man.update(units, units_tag_dict)
        if action is not None:
            return action

        action = self.scout_man.update(units, units_tag_dict)
        if action is not None:
            return action

        return None
