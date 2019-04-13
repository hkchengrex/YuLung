from pysc2.env.sc2_env import SC2Env

from bot.mod.comabt_manager import CombatManager
from bot.mod.expansion_manager import ExpansionManager
from bot.mod.global_info import GlobalInfo
from bot.mod.production_manager import ProductionManager
from bot.mod.scout_manager import ScoutManager
from bot.mod.tech_manager import TechManager
from bot.util.helper import *
from bot.util.static_units import *

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
        self.tech_man = TechManager(self.global_info)

        self.global_info.log_game_info("Hypervisor initialized.")

        self.produ_man.build_asap(UNITS[UnitID.Overlord])

        self.iter = 0
        self.produ_usage = 0
        self.comba_usage = 0
        self.scout_usage = 0
        self.work_usage = 0
        self.queen_usage = 0

    def process(self, action, obs):
        units, units_tag_dict = self.global_info.update(obs)

        hatchery_build_pos, queens_to_be_build = self.expan_man.update_expansion(units, units_tag_dict)

        for pos in hatchery_build_pos:
            self.produ_man.build_asap(UNITS[UnitID.Hatchery], pos)
        if queens_to_be_build > 0:
            self.produ_man.build_asap(UNITS[UnitID.Queen], amount=queens_to_be_build)

        self.produ_man.set_base_locations([exp.pos for exp in self.expan_man.own_expansion() if exp.base is not None])

        self.scout_man.set_scout_tar([exp.pos for exp in self.expan_man.expansion])

        """
        Hardcoded simple rules here
        """
        ##if len(self.expan_man.own_expansion()) < 2:
        ##    self.expan_man.claim_expansion(self.expan_man.get_next_expansion())

        drones_count = self.produ_man.get_count_ours_and_pending(units, UNITS[UnitID.Drone])
        pools_count = self.produ_man.get_count_ours_and_pending(units, UNITS[UnitID.SpawningPool])
        extractor_count = self.produ_man.get_count_ours_and_pending(units, UNITS[UnitID.Extractor])
        overlord_count = self.produ_man.get_count_pending(UNITS[UnitID.Overlord]) \
                         + self.global_info.overlord_count

        bases = get_all_owned(units, UNITS[UnitID.Hatchery]) \
                 + get_all_owned(units, UNITS[UnitID.Lair]) \
                 + get_all_owned(units, UNITS[UnitID.Hive])
        max_drones = len(bases) * 16

        if self.global_info.resources.food_used + 4 > overlord_count*8 + len(bases)*6:
            self.produ_man.build_asap(UNITS[UnitID.Overlord])
            self.global_info.log_game_info('Building overlord under pressure', False)

        if len(self.produ_man.units_pending) == 0:
            if drones_count < max_drones:
                self.produ_man.build_asap(UNITS[UnitID.Drone])
            elif pools_count == 0:
                self.tech_man.enable_tech(UNITS[UnitID.SpawningPool].unit_id)
            elif extractor_count == 0:
                if self.expan_man.main_expansion() is not None:
                    next_gas = self.expan_man.get_next_gas(units)
                    if next_gas is not None:
                        self.produ_man.build_asap(UNITS[UnitID.Extractor], next_gas)
            elif extractor_count == 1:
                if self.expan_man.main_expansion() is not None:
                    next_gas = self.expan_man.get_next_gas(units)
                    if next_gas is not None:
                        self.produ_man.build_asap(UNITS[UnitID.Extractor], next_gas)
            else:
                self.produ_man.build_asap(UNITS[UnitID.Zergling])

        if len(self.expan_man.enemy_expansion()) > 0:
            self.comba_man.set_attack_tar(self.expan_man.enemy_expansion()[0].pos)
        self.work_man.track(units, self.expan_man.expansion)
        """
        End of hardcoded simple rules
        """

        # Update tech requirement
        tech_to_be_built = self.tech_man.update(units, self.produ_man)
        for t in tech_to_be_built:
            self.produ_man.build_asap(t)

        self.iter += 1
        if self.iter % 100 == 0:
            print('Comba usage: %d' % self.comba_usage)
            print('Produ usage: %d' % self.produ_usage)
            print('Work  usage: %d' % self.work_usage)
            print('Scout usage: %d' % self.scout_usage)
            print('Queen usage: %d' % self.scout_usage)
            print('Idle:        %d' % (self.iter-self.comba_usage-self.produ_usage
                                       -self.work_usage-self.scout_usage-self.queen_usage))

            self.iter = self.comba_usage = self.produ_usage \
                = self.work_usage = self.scout_usage = self.queen_usage = 0

        # Define priorities here. TODO: Might need to give priorities dynamically
        action = self.comba_man.update(units)
        if action is not None:
            self.comba_usage += 1
            return action        

        ratio = 1
        action = self.work_man.assign(units, self.expan_man.expansion, ratio)
        if action is not None:
            self.work_usage += 1
            return action

        action = self.produ_man.update(units, units_tag_dict)
        self.produ_man.update_ongoing_construction(units_tag_dict)
        if action is not None:
            self.produ_usage += 1
            return action

        action = self.scout_man.update(units, units_tag_dict)
        if action is not None:
            self.scout_usage += 1
            return action

        # action = {"discrete_output": action[0].astype(int), "continous_output": action[1]}
        #
        # # (action) Refer to py_action, the output of action #
        #
        # action_id = action["discrete_output"][0]
        # action_act = action["discrete_output"][1]
        # unit_id = action["discrete_output"][2]
        # x = action["discrete_output"][3]
        # y = action["discrete_output"][4]
        # temp = action["continous_output"][0]
        #
        # # ####
        #
        # if action_id == 0:
        #     action = self.comba_man.update(units)
        # elif action_id == 1:
        #     action = self.produ_man.update(units, units_tag_dict)
        # elif action_id == 2:
        #     ratio = 1
        #     action = self.work_man.assign(units, self.expan_man.expansion, ratio)
        # else:
        #     action = None
        # return action

        if self.iter % 5 == 0:
            action = self.expan_man.queen_inject()
            if action is not None:
                self.queen_usage += 1
                return action

        return None
