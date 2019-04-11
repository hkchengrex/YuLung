import random

from pysc2.lib import actions
from pysc2.lib import point

from bot.queries import *
from bot.util import grid_ordering
from bot.util.helper import *
from bot.util.unit_ids import *
from bot.struct.unit_class import *
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

        self.working_drone_list = []
        self.ongoing_construction = []

    def build_asap(self, unit_type: UnitType, pos=None, amount=1):
        self.units_pending.extend([{'type': unit_type, 'pos': pos}] * amount)

    def record_build(self, pending):
        self.logger.log_game_info('Planning to build: ' + pending['type'].name)
        self.units_pending.remove(pending)
        self.all_built.append(pending['type'])

    def set_base_locations(self, base_locations: List[point.Point]):
        self.base_locations = base_locations  # type: List[point.Point]

    def update(self, units, units_tag_dict):

        planned_action = None

        drones = get_all_owned(units, UNITS[UnitID.Drone])
        self.check_failed_construction(drones, units_tag_dict)

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
                            self.record_build(pending)
                            planned_action = get_raw_quick_action_id(unit_type.ability_id)("now", [selected_larva.tag])
                            return planned_action
                        else:
                            self.logger.log_game_verbose('Tried to morph: ' + unit_type.name + ' but we cannot.')

                elif unit_type in FROM_DRONE_TYPE:
                    # Don't take the drones that have missions
                    usable_drones = [d for d in drones if not d.has_ongoing_action]

                    if len(usable_drones) > 0:
                        # Pick drone
                        selected_drone = random.choice(usable_drones)

                        if type(pos) != Unit:
                            # Pick location
                            if pos is None:
                                for _ in range(10):
                                    if len(self.base_locations) == 0:
                                        return
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
                                self.record_build(pending)
                                selected_drone.has_ongoing_action = True
                                selected_drone.action_detail = pending
                                self.working_drone_list.append(selected_drone)
                                planned_action = get_raw_pos_action_id(unit_type.ability_id)(
                                    "now", build_pos, [selected_drone.tag])
                                self.update_ongoing_construction(units_tag_dict)
                                return planned_action
                            else:
                                print('Failed to build at ', str(build_pos))

                        else:
                            # Targeted build, like extractors
                            self.record_build(pending)
                            selected_drone.has_ongoing_action = True
                            selected_drone.action_detail = pending
                            self.working_drone_list.append(selected_drone)
                            planned_action = get_raw_targeted_action_id(unit_type.ability_id)(
                                "now", pos.tag, [selected_drone.tag])
                            self.update_ongoing_construction(units_tag_dict)
                            return planned_action
                    else:
                        print('No usable drones!')

                else:
                    raise NotImplementedError

        return planned_action

    def check_failed_construction(self, drones, units_tag_dict: Dict[int, Unit]):
        interrupted_drones = [d for d in drones if d.has_ongoing_action and d.order_len == 0]

        for d in interrupted_drones:
            self.logger.log_game_info('Re-inserting %s into the production queue' % d.action_detail)
            self.units_pending.extend([d.action_detail])
            d.has_ongoing_action = False
            d.action_detail = None
            self.working_drone_list.remove(d)

    def update_ongoing_construction(self, units_tag_dict: Dict[int, Unit]):
        ongoing_construction = []
        for d in self.working_drone_list:
            d = units_tag_dict.get(d.tag)
            if d is not None:
                ongoing_construction.append(d.action_detail)
        self.ongoing_construction = ongoing_construction

    def get_count_ours_and_pending(self, units, unit_type):
        return len(get_all_owned(units, unit_type)) + len([
            u for u in self.units_pending if u['type'] == unit_type
        ]) + len([
            u for u in self.ongoing_construction if u['type'] == unit_type
        ])

