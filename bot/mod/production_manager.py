import random

from pysc2.lib import actions
from pysc2.lib import point

from bot.queries import *
from bot.util import grid_ordering
from bot.util.helper import *
from bot.util.unit_ids import *
from .low_level_module import LowLevelModule

FUNCTIONS = actions.FUNCTIONS


class ProductionManager(LowLevelModule):
    """
    ProductionManager
    - Maintain queue of units/buildings production
    - Pick workers/lavras to build stuff
    """
    def __init__(self, global_info):
        super().__init__(global_info)

        self.units_pending = []
        self.all_built = []
        self.base_loc = None

        self.base_locations = []  # type: List[point.Point]

    def build_asap(self, unit_type: UnitType, pos=None, amount=1):
        self.units_pending.extend([{'type': unit_type, 'pos': pos}] * amount)

    def record_build(self, type):
        self.logger.log_game_info('Planning to build: ' + type.name)
        self.units_pending = self.units_pending[1:]
        self.all_built.append(type)

    def set_base_locations(self, base_locations: List[point.Point]):
        self.base_locations = base_locations  # type: List[point.Point]

    def update(self, units):

        planned_action = None
        # print(self.units_pending)

        for pending in self.units_pending:
            unit_type = pending['type']
            pos = pending['pos']

            if self.global_info.can_afford_unit(unit_type):

                if unit_type in FROM_LARVA_TYPE:
                    # Pick a larva and build the unit required
                    larvas = get_all_owned(units, UNITS[UnitID.Larva])
                    if len(larvas) > 0:
                        selected_larva = random.choice(larvas)

                        avail_abilities = query_available_abilities(self.sc2_env, selected_larva.tag)
                        if unit_type.ability_id in avail_abilities:
                            self.record_build(unit_type)
                            planned_action = get_raw_action_id(unit_type.ability_id)("now", [selected_larva.tag])
                            return planned_action
                        else:
                            self.logger.log_game_verbose('Tried to morph: ' + unit_type.name + ' but we cannot.')

                elif unit_type in FROM_DRONE_TYPE:
                    # Pick a drone and build it in a proper place
                    drones = get_all_owned(units, UNITS[UnitID.Drone])
                    if len(drones) > 0:
                        # Pick drone
                        selected_drone = random.choice(drones)

                        # Pick location
                        if pos is None:
                            for _ in range(10):
                                base_loc = random.choice(self.base_locations)
                                ran_x = random.randint(-10, 11)*100 + base_loc.x
                                ran_y = random.randint(-10, 11)*100 + base_loc.y
                                build_pos = point.Point(ran_x, ran_y)
                                result = query_building_placement(self.sc2_env, unit_type.ability_id, build_pos)
                                if result == 1:
                                    break
                        else:
                            # Try 11x11 shift, from center orderly
                            for (i, j) in grid_ordering.order_5:
                                build_pos = point.Point(pos.x+i*100+50, pos.y+j*100+50)
                                result = query_building_placement(self.sc2_env, unit_type.ability_id, build_pos)
                                if result == 1:
                                    break

                        # 1 = Success,
                        # See https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/error.proto
                        if result == 1:
                            self.record_build(unit_type)
                            planned_action = get_raw_action_id(unit_type.ability_id)(
                                "now", build_pos, [selected_drone.tag])
                            return planned_action
                        else:
                            print('Failed to build at ', str(build_pos))

                else:
                    raise NotImplementedError

        return planned_action

