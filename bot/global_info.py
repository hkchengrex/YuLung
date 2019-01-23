from pysc2.env.sc2_env import SC2Env

from .util.game_logger import GameLogger
from .util.resources import Resources, player_to_resources

from .util.static_units import UNITS
from .util.unit import Attribute, Weapon, UnitType


class GlobalInfo(GameLogger):
    """
    - Contains global information for information passing between modules
    - Logging ability
    """

    def __init__(self, sc2_env: SC2Env):
        super(GlobalInfo, self).__init__(sc2_env)
        self.resources = None  # type: Resources

    def update(self, obs):
        self.resources = player_to_resources(obs.observation.player)

    def avail_food(self):
        return self.resources.food_cap - self.resources.food_used

    def can_afford_unit(self, unit: UnitType):
        return (self.resources.mineral >= unit.mineral_cost
                and self.resources.vespene >= unit.vespene_cost
                and self.avail_food() >= unit.food_required)
