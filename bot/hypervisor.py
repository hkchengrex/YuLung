from pysc2.env.sc2_env import SC2Env

from bot.mod.comabt_manager import CombatManager
from bot.mod.expansion_manager import ExpansionManager
from bot.mod.global_info import GlobalInfo
from bot.mod.production_manager import ProductionManager
from bot.mod.scout_manager import ScoutManager
from bot.mod.tech_manager import TechManager
from bot.mod.worker_manager import WorkerManager
from bot.util.helper import *
from bot.util.static_units import *

from bot.macro_actions import *


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
        self.work_man = WorkerManager(self.global_info)
        self.tech_man = TechManager(self.global_info)

        self.scout_man.set_scout_tar([exp.pos for exp in self.expan_man.expansion])
        self.scout_man.go_scout_once()

        self.global_info.log_game_info("Hypervisor initialized.")

        self.produ_man.build_asap(UNITS[UnitID.Overlord])

        self.global_iter = 0
        self.local_iter = 0

        # Action usage info
        self.produ_usage = 0
        self.comba_usage = 0
        self.scout_usage = 0
        self.work_usage = 0
        self.queen_usage = 0
        self.last_queen_iter = 0

    @staticmethod
    def get_macro_action_spec():
        return {'discrete': [
            len(CombatAction),
            len(ConstructionAction),
            len(TechAction),
            len(MiscAction),
            len(ResourcesAction),
            len(ConstructAmountAction),
        ],
            'continuous': []}

    def process(self, macro_action, obs):
        units, units_tag_dict = self.global_info.update(obs)

        """
        Some initialization steps
        """
        hatchery_build_pos, queens_to_be_build = self.expan_man.update_expansion(units, units_tag_dict)

        """
        Applying macro actions
        """
        discrete_input = macro_action[0]
        # continuous_input = macro_action[1]

        comb_action = CombatAction(discrete_input[0])
        cons_action = ConstructionAction(discrete_input[1])
        tech_action = TechAction(discrete_input[2])
        misc_action = MiscAction(discrete_input[3])
        reso_action = ResourcesAction(discrete_input[4])
        amou_action = ConstructAmountAction(discrete_input[5])

        # After 2000 steps (around 12 minutes, FORCE ANNIHILATION!!!)
        if self.global_iter < 2000:
            # Combat resolution
            if comb_action < CombatAction.MOVE_EXP_0:
                self.comba_man.set_attack_tar(self.expan_man.expansion[comb_action].pos)
            elif comb_action < CombatAction.ELIMINATE:
                self.comba_man.set_attack_tar(self.expan_man.expansion[comb_action-CombatAction.MOVE_EXP_0].pos)
            else:
                self.comba_man.try_annihilate()
        else:
            self.comba_man.try_annihilate()

        # Construction resolution
        if cons_action != ConstructionAction.NO_OP:
            if cons_action == ConstructionAction.BUILD_EXPANSION:
                self.expan_man.claim_expansion(self.expan_man.get_next_expansion())
            elif cons_action == ConstructionAction.BUILD_EXTRACTOR:
                # Build only when none is being built, otherwise it will be buggy
                if self.produ_man.get_count_pending(UNITS[UnitID.Extractor]) == 0:
                    if self.expan_man.main_expansion() is not None:
                        next_gas = self.expan_man.get_next_gas(units)
                        if next_gas is not None:
                            self.produ_man.build_asap(UNITS[UnitID.Extractor], pos=next_gas)
            else:
                self.produ_man.build_units_with_checking(CONSTRUCTION_UNITS_MAPPING[cons_action],
                                                         amount=CONSTRUCT_AMOUNT_MAPPING[amou_action])

        # Tech resolution
        if tech_action != TechAction.NO_OP:
            self.tech_man.enable_tech(TECH_UNITS_MAPPING[tech_action])

        # Misc resolution
        if misc_action == MiscAction.SCOUT_ONCE:
            self.scout_man.go_scout_once()

        # Resources resolution
        mineral_worker_ratio = RESOURCES_RATIO_MAPPING[reso_action]

        """
        Routine update within hypervisor and low-level modules
        """

        # Hatchery / queen build request from expansion manager, just do it
        for pos in hatchery_build_pos:
            self.produ_man.build_asap(UNITS[UnitID.Hatchery], pos)
        if queens_to_be_build > 0:
            self.produ_man.build_asap(UNITS[UnitID.Queen], amount=queens_to_be_build)

        self.produ_man.set_base_locations([exp.pos for exp in self.expan_man.own_expansion() if exp.base is not None])

        # Force building overlord when the need arises
        overlord_count = self.produ_man.get_count_pending(UNITS[UnitID.Overlord]) \
                         + self.global_info.overlord_count
        bases = get_all_owned(units, UNITS[UnitID.Hatchery]) \
                 + get_all_owned(units, UNITS[UnitID.Lair]) \
                 + get_all_owned(units, UNITS[UnitID.Hive])
        if self.global_info.resources.food_used + 4 > overlord_count*8 + len(bases)*6:
            self.produ_man.build_asap(UNITS[UnitID.Overlord])
            self.global_info.log_game_info('Building overlord under pressure', False)

        self.work_man.track(units, self.expan_man.expansion)

        # Update tech requirement from tech manager
        tech_to_be_built = self.tech_man.update(units, self.produ_man)
        for t in tech_to_be_built:
            self.produ_man.build_asap(t)

        # Keep track of action usage
        self.local_iter += 1
        self.global_iter += 1
        if self.local_iter % 100 == 0:
            # print('Comba usage: %d' % self.comba_usage)
            # print('Produ usage: %d' % self.produ_usage)
            # print('Work  usage: %d' % self.work_usage)
            # print('Scout usage: %d' % self.scout_usage)
            # print('Queen usage: %d' % self.scout_usage)
            # print('Idle:        %d' % (self.local_iter-self.comba_usage-self.produ_usage
            #                            -self.work_usage-self.scout_usage-self.queen_usage))

            self.local_iter = self.comba_usage = self.produ_usage \
                = self.work_usage = self.scout_usage = self.queen_usage = 0

        # Define priorities here. TODO: Might need to give priorities dynamically
        action = self.comba_man.update(units, self.expan_man.expansion)
        if action is not None:
            self.comba_usage += 1
            return action

        action = self.work_man.assign(units, self.expan_man.expansion, mineral_worker_ratio)
        if action is not None:
            self.work_usage += 1
            return action

        print([u['type'].name for u in self.produ_man.units_pending])

        if self.expan_man.main_expansion() is not None:
            main_base = self.expan_man.main_expansion().base
        else:
            main_base = None
        action = self.produ_man.update(units, units_tag_dict, main_base)
        self.produ_man.update_ongoing_construction(units_tag_dict)
        if action is not None:
            self.produ_usage += 1
            return action

        action = self.scout_man.update(units, units_tag_dict)
        if action is not None:
            self.scout_usage += 1
            return action

        if (self.global_iter - self.last_queen_iter) > 5:
            self.last_queen_iter = self.global_iter
            action = self.expan_man.queen_inject()
            if action is not None:
                self.queen_usage += 1
                return action

        return None
