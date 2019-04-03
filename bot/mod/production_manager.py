import random

from .low_level_module import LowLevelModule

from bot.util.static_units import UNITS, UnitID
from bot.util.unit_info import Attribute, Weapon, UnitType
from bot.util.helper import *
from bot.util import unit_info
from bot.util.unit_ids import *
from bot.queries import *

from s2clientprotocol import (
    error_pb2 as error_pb,
)

from pysc2.lib import actions
from pysc2.lib import point
FUNCTIONS = actions.FUNCTIONS


class ProductionManager(LowLevelModule):
    """
    ProductionManager
    - Maintain queue of units/buildings production
    - Pick workers/lavras to build stuff
    """
    def __init__(self, global_info):
        super(ProductionManager, self).__init__(global_info)

        self.units_pending = []
        self.all_built = []
        self.base_loc = None

    def build_asap(self, unit_type: UnitType, amount=1):
        self.units_pending.extend([unit_type] * amount)

    def record_build(self, type):
        self.logger.log_game_info('Planning to build: ' + type.name)
        self.units_pending = self.units_pending[1:]
        self.all_built.append(type)

    def set_base_location(self, base_loc: point):
        self.base_loc = base_loc  # type: point

    def update(self, units):

        planned_action = None

        for unit_type in self.units_pending:
            if self.global_info.can_afford_unit(unit_type):

                if unit_type in FROM_LARVA_TYPE:
                    # Pick a larva and build the unit required
                    larvas = get_all(units, UNITS[UnitID.Larva])
                    if len(larvas) > 0:
                        selected_larva = random.choice(larvas)

                        avail_abilities = query_available_abilities(self.sc2_env, selected_larva.tag)
                        if unit_type.ability_id in avail_abilities:
                            self.record_build(unit_type)
                            planned_action = get_raw_action_id(unit_type.ability_id)("now", [selected_larva.tag])
                            print(planned_action)
                        else:
                            self.logger.log_game_verbose('Tried to morph: ' + unit_type.name + ' but we cannot.')

                elif unit_type in FROM_DRONE_TYPE:
                    # Pick a drone and build it in a proper place
                    drones = get_all(units, UNITS[UnitID.Drone])
                    if len(drones) > 0:
                        # Pick drone
                        selected_drone = random.choice(drones)

                        # Pick location
                        ran_x = random.randint(-3000, 3000) + self.base_loc.x
                        ran_y = random.randint(-3000, 3000) + self.base_loc.y
                        p = point.Point(ran_x, ran_y)
                        result = query_building_placement(self.sc2_env, unit_type.ability_id, p)

                        # 1=Success, see https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/error.proto
                        if result == 1:
                            self.record_build(unit_type)
                            planned_action = get_raw_action_id(unit_type.ability_id)("now", p, [selected_drone.tag])

        return planned_action

