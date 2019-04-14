from pysc2.env.sc2_env import SC2Env

from bot.struct.resources import Resources, player_to_resources
from bot.util.consistent_units import ConsistentUnits
from bot.util.game_logger import GameLogger
from bot.util.unit_info import UnitType
from bot.util.helper import *
from bot.util.unit_ids import *


class GlobalInfo(GameLogger):
    """
    - Contains global information for information passing between modules
    - Logging ability
    """

    def __init__(self, sc2_env: SC2Env):
        super(GlobalInfo, self).__init__(sc2_env)
        self.resources = None  # type: Resources
        self.consistent_units = ConsistentUnits()
        self.home_pos = None

        self.overlord_count = 1
        self.last_seen_overlords = []

        self.has_pool = False

    def update(self, obs):
        self.consistent_units.update(obs.observation.raw_units)
        self.resources = player_to_resources(obs.observation.player)

        units = self.consistent_units.units
        units_tag_dict = self.consistent_units.units_tag_dict

        for o in self.last_seen_overlords:
            if units_tag_dict.get(o.tag) is None:
                self.overlord_count -= 1  # One of them is dead
        self.last_seen_overlords = get_all_owned(units, ZERG_OVERSEER_LORD)

        if not self.has_pool and len(get_all_owned(units, UNITS[UnitID.SpawningPool])) > 0:
            self.has_pool = True

        return units, units_tag_dict

    def avail_food(self):
        return self.resources.food_cap - self.resources.food_used

    def can_afford_unit(self, unit: UnitType):
        if unit.food_required == 0:
            return (self.resources.mineral >= unit.mineral_cost
                    and self.resources.vespene >= unit.vespene_cost)
        else:
            return (self.resources.mineral >= unit.mineral_cost
                    and self.resources.vespene >= unit.vespene_cost
                    and self.avail_food() >= unit.food_required)

    def check_if_unit_exist(self, unit_type: UnitType):
        return len(get_all_owned(self.consistent_units.units, unit_type)) > 0
