import random

from pysc2.lib import actions
from pysc2.lib import point

from bot.queries import *
from bot.util import grid_ordering
from bot.util.helper import *
from bot.util.unit_ids import *
from bot.struct.unit_class import *
from .low_level_module import LowLevelModule
from .production_manager import ProductionManager

FUNCTIONS = actions.FUNCTIONS


class TechManager(LowLevelModule):
    """
    TechManager
    - Maintain list of researched technology/building prerequisite
    - Maintain tech requirement, i.e. when pool is destroyed, it will be rebuilt
    """
    def __init__(self, global_info):
        super().__init__(global_info)
        self.tech_list = [False] * len(ZERG_TECH_BUILDINGS)

    def enable_tech(self, unit_id: int):
        for i, tech in enumerate(ZERG_TECH_BUILDINGS):
            if unit_id == tech.unit_id:
                if not self.tech_list[i]:
                    self.logger.log_game_info('I should have %s from now on' % tech.name)
                self.tech_list[i] = True
                return

        print('Unit id %d is not the tech list' % unit_id)

    def update(self, units, prod_man: ProductionManager):
        to_be_built = []

        for i, tech_enable in enumerate(self.tech_list):
            if tech_enable:
                if prod_man.get_count_ours_and_pending(units, ZERG_TECH_BUILDINGS[i]) == 0:
                    to_be_built.append(ZERG_TECH_BUILDINGS[i])

                    print(len(get_all_owned(units, ZERG_TECH_BUILDINGS[i])))
                    print(len([u for u in prod_man.units_pending if u['type'] == ZERG_TECH_BUILDINGS[i]]))
                    print(len([u for u in prod_man.ongoing_construction if u['type'] == ZERG_TECH_BUILDINGS[i]]))

        return to_be_built
