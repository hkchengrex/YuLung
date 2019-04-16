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

        self.mineral_worker_ratio = 0.5

        self.last_reward = None

        self.last_raw = None
        self.last_mineral_adv = None
        self.last_gas_adv = None
        self.last_total_val = None

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

    def get_observation(self):
        return {
            'expansions': [alliance_to_id[ex.ownership] for ex in self.expan_man.expansion],
            'tech': self.tech_man.tech_list,
            'scout': self.scout_man.enemy_tech,
            'extractors': len(get_all_owned(self.global_info.consistent_units.units, UNITS[UnitID.Extractor])),
            'time': self.global_iter,
            'drone': max(self.work_man.get_deficiency(self.global_info.consistent_units.units,
                                                      self.expan_man.expansion), 0),
            'minerals': self.global_info.resources.mineral,
            'gas': self.global_info.resources.vespene,
            'food_usage': self.global_info.resources.food_used,
            'food_cap': self.global_info.resources.food_cap
        }

    def get_reward(self, obs):
        raw_score = obs.observation.score_cumulative.score
        mineral_adv = sum(obs.observation.score_by_category.killed_minerals)
        gas_adv = sum(obs.observation.score_by_category.killed_vespene)
        total_val = obs.observation.score_cumulative.total_value_units
        curr_min = self.global_info.resources.mineral

        raw_score /= 20
        mineral_adv /= 5
        gas_adv /= 2
        total_val /= 5
        curr_min /= 35

        reward = raw_score + mineral_adv + gas_adv + total_val - curr_min

        reward = reward/200 ** ((self.global_iter+1000)/3000)

        if self.last_reward is None:
            self.last_reward = reward
        else:
            # print('Raw  TD: ', raw_score - self.last_raw)
            # print('Madv TD:', mineral_adv)
            # print('Gadv TD:', gas_adv)
            # print('Tval TD:', total_val - self.last_total_val)
            # print('Min    :', curr_min)
            # print('Total  :',  reward)
            pass

        td = reward - self.last_reward

        self.last_reward = reward
        self.last_raw = raw_score
        self.last_mineral_adv = mineral_adv
        self.last_gas_adv = gas_adv
        self.last_total_val = total_val

        td = min(td, 0.5)
        td = max(td, -0.5)

        return td

    def process(self, macro_action, obs):
        units, units_tag_dict = self.global_info.update(obs)

        """
        Some initialization steps
        """
        hatchery_build_pos, queens_to_be_build = self.expan_man.update_expansion(units, units_tag_dict, self.produ_man)

        """
        Applying macro actions
        """
        if macro_action is not None:
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
                if comb_action < CombatAction.RETREAT:
                    self.comba_man.set_attack_tar(self.expan_man.expansion[comb_action].pos)
                elif comb_action == CombatAction.RETREAT:
                    self.comba_man.set_move_tar(self.global_info.home_pos)
                else:
                    self.comba_man.try_annihilate()
            else:
                self.scout_man.go_scout_once()
                self.comba_man.try_annihilate()

            # Construction resolution
            if cons_action != ConstructionAction.NO_OP:
                if cons_action == ConstructionAction.BUILD_EXPANSION:
                    if self.expan_man.get_unbuilt_expansion_count() == 0:
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
                self.tech_man.enable_tech(units, TECH_UNITS_MAPPING[tech_action], self.produ_man)

            # Misc resolution
            if misc_action == MiscAction.SCOUT_ONCE:
                self.scout_man.go_scout_once()

            # Resources resolution
            self.mineral_worker_ratio = RESOURCES_RATIO_MAPPING[reso_action]

        """
        Routine update within hypervisor and low-level modules
        """

        if self.global_info.resources.mineral > 500:
            self.produ_man.build_units_with_checking(UNITS[UnitID.Zergling])
            self.produ_man.build_units_with_checking(UNITS[UnitID.Roach])
            self.produ_man.build_units_with_checking(UNITS[UnitID.Hydralisk])
            self.produ_man.build_units_with_checking(UNITS[UnitID.Mutalisk])

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

        # Only update when there is an incoming macro action
        if macro_action is not None:
            action = self.comba_man.update(units, self.expan_man.expansion)
            if action is not None:
                self.comba_usage += 1
                return action

        action = self.work_man.assign(units, self.expan_man.expansion, self.mineral_worker_ratio)
        if action is not None:
            self.work_usage += 1
            return action

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
