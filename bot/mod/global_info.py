from pysc2.env.sc2_env import SC2Env

from bot.struct.resources import Resources, player_to_resources
from bot.util.consistent_units import ConsistentUnits
from bot.util.game_logger import GameLogger
from bot.util.unit_info import UnitType


class GlobalInfo(GameLogger):
    """
    - Contains global information for information passing between modules
    - Logging ability
    """

    def __init__(self, sc2_env: SC2Env):
        super(GlobalInfo, self).__init__(sc2_env)
        self.resources = None  # type: Resources
        self.consistent_units = ConsistentUnits()

    def update(self, obs):
        self.consistent_units.update(obs.observation.raw_units)
        self.resources = player_to_resources(obs.observation.player)

        return self.consistent_units.units, self.consistent_units.units_tag_dict

    def avail_food(self):
        return self.resources.food_cap - self.resources.food_used

    def can_afford_unit(self, unit: UnitType):
        return (self.resources.mineral >= unit.mineral_cost
                and self.resources.vespene >= unit.vespene_cost
                and self.avail_food() >= unit.food_required)
