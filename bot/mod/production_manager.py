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
        # self.working_larva_list = []
        self.ongoing_construction = []

    def _extend_queue(self, unit_type: UnitType, pos=None, amount=1, life=10000):
        self.units_pending.extend([{'type': unit_type, 'pos': pos, 'life': life}] * amount)

    def build_asap(self, unit_type: UnitType, pos=None, amount=1):
        self._extend_queue(unit_type, pos, amount)

    def check_exist_in_queue(self, unit_type: UnitType):
        for u in self.units_pending:
            if u['type'].unit_id == unit_type.unit_id:
                return True
        return False

    def build_units_with_checking(self, unit_type: UnitType, amount=1):

        # Don't spam my queue dude
        if self.check_exist_in_queue(unit_type):
            return

        if self.global_info.can_afford_unit(unit_type):

            # Check tech requirement
            if unit_type in [UNITS[UnitID.Zergling], UNITS[UnitID.Queen]]:
                if self.global_info.check_if_unit_exist(UNITS[UnitID.SpawningPool]):
                    self._extend_queue(unit_type, None, amount, life=30)

            elif unit_type == UNITS[UnitID.Roach]:
                if self.global_info.check_if_unit_exist(UNITS[UnitID.RoachWarren]):
                    self._extend_queue(unit_type, None, amount, life=30)

            elif unit_type == UNITS[UnitID.Hydralisk]:
                if self.global_info.check_if_unit_exist(UNITS[UnitID.HydraliskDen]):
                    self._extend_queue(unit_type, None, amount, life=30)

            elif unit_type in [UNITS[UnitID.Mutalisk], UNITS[UnitID.Corruptor]]:
                if self.global_info.check_if_unit_exist(UNITS[UnitID.Spire]):
                    self._extend_queue(unit_type, None, amount, life=30)

            elif unit_type == UNITS[UnitID.Ultralisk]:
                if self.global_info.check_if_unit_exist(UNITS[UnitID.UltraliskCavern]):
                    self._extend_queue(unit_type, None, amount, life=30)

            elif unit_type == UNITS[UnitID.Overseer]:
                if self.global_info.check_if_unit_exist(UNITS[UnitID.Lair]):
                    self._extend_queue(unit_type, None, amount, life=30)

            else:
                self._extend_queue(unit_type, None, amount, life=30)

    def record_build(self, pending):

        if pending['type'] in ZERG_OVERSEER_LORD:
            self.global_info.overlord_count += 1

        self.logger.log_game_info('Planning to build: ' + pending['type'].name, False)
        self.units_pending.remove(pending)
        self.all_built.append(pending['type'])

    def set_base_locations(self, base_locations: List[point.Point]):
        self.base_locations = base_locations  # type: List[point.Point]

    def update(self, units, units_tag_dict, main_base: Unit):

        planned_action = None

        drones = get_all_owned(units, UNITS[UnitID.Drone])
        self.check_failed_construction(drones)

        # Life decay, nothing last forever, bro
        for pending in self.units_pending:
            pending['life'] -= 1

        self.units_pending = [p for p in self.units_pending if p['life'] > 0]

        for pending in self.units_pending:
            unit_type = pending['type']
            pos = pending['pos']

            if self.global_info.can_afford_unit(unit_type):

                # usable_larvas = [d for d in larvas if not d.has_ongoing_action]
                larvas = get_all_owned(units, UNITS[UnitID.Larva])
                if unit_type in FROM_LARVA_TYPE:
                    # Pick a larva and build the unit required
                    if len(larvas) > 0:
                        selected_larva = random.choice(larvas)  # type: Unit

                        avail_abilities = query_available_abilities(self.sc2_env, selected_larva.tag)
                        if unit_type.ability_id in avail_abilities:
                            self.record_build(pending)
                            # selected_larva.has_ongoing_action = True
                            # selected_larva.action_detail = pending
                            # self.working_larva_list.append(selected_larva)
                            planned_action = get_raw_quick_action_id(unit_type.ability_id)("now", [selected_larva.tag])
                            return planned_action
                        # else:
                        #     self.logger.log_game_verbose('Tried to morph: ' + unit_type.name + ' but we cannot.')

                elif unit_type in FROM_DRONE_TYPE:
                    # Don't take the drones that have missions
                    usable_drones = [d for d in drones if not d.has_ongoing_action]

                    if len(usable_drones) > 0:
                        # Pick drone
                        selected_drone = random.choice(usable_drones)  # type: Unit
                        avail_abilities = query_available_abilities(self.sc2_env, selected_drone.tag)
                        if unit_type.ability_id in avail_abilities:
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
                                    # Just remove it from the queue
                                    # Since I changed an item in the for loop, better return
                                    self.units_pending.remove(pending)
                                    return planned_action

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
                        pass
                        # print('No usable drones!')

                elif unit_type == UNITS[UnitID.Queen]:
                    bases = get_all_owned(units, ZERG_BASES)
                    bases = [b for b in bases if b.order_len == 0]
                    if len(bases) > 0:
                        selected_base = random.choice(bases)
                        avail_abilities = query_available_abilities(self.sc2_env, selected_base.tag)
                        if unit_type.ability_id in avail_abilities:
                            self.record_build(pending)
                            planned_action = get_raw_quick_action_id(unit_type.ability_id)("now", [selected_base.tag])
                            return planned_action
                        else:
                            self.logger.log_game_verbose('Tried to build: ' + unit_type.name + ' in base but we cannot.')

                elif unit_type == UNITS[UnitID.Lair]:
                    if main_base is not None:
                        if main_base.unit_type == UNITS[UnitID.Hatchery].unit_id and main_base.order_len == 0:
                            # Upgrade it to Lair
                            self.record_build(pending)
                            planned_action = get_raw_quick_action_id(unit_type.ability_id)(
                                "now", [main_base.tag])
                            return planned_action
                        else:
                            # Just remove it from the queue
                            # Since I changed an item in the for loop, better return
                            self.units_pending.remove(pending)
                            return planned_action

                # Similar logic
                elif unit_type == UNITS[UnitID.Hive]:
                    if main_base is not None:
                        if main_base.unit_type == UNITS[UnitID.Lair].unit_id:
                            # Upgrade it to Hive
                            avail_abilities = query_available_abilities(self.sc2_env, main_base.tag)
                            if unit_type.ability_id in avail_abilities:
                                self.record_build(pending)
                                planned_action = get_raw_quick_action_id(unit_type.ability_id)(
                                    "now", [main_base.tag])
                                return planned_action
                        else:
                            # Just remove it from the queue
                            # Since I changed an item in the for loop, better return
                            self.units_pending.remove(pending)
                            return planned_action

                elif unit_type == UNITS[UnitID.Overseer]:
                    overlords = get_all_owned(units, UNITS[UnitID.Overlord])
                    overlords = [o for o in overlords if not o.is_a_scout]

                    if len(overlords) > 0:
                        selected_overlord = random.choice(overlords)

                        avail_abilities = query_available_abilities(self.sc2_env, selected_overlord.tag)
                        if unit_type.ability_id in avail_abilities:
                            self.record_build(pending)
                            planned_action = get_raw_quick_action_id(unit_type.ability_id)("now", [selected_overlord.tag])
                            return planned_action

                else:
                    print(unit_type)
                    raise NotImplementedError

        return planned_action

    def check_failed_construction(self, drones):
        interrupted_drones = [d for d in drones if d.has_ongoing_action and d.order_len == 0]

        for d in interrupted_drones:
            self.logger.log_game_info('Re-inserting %s into the production queue' % d.action_detail)
            self.units_pending.extend([d.action_detail])
            d.has_ongoing_action = False
            d.action_detail = None
            self.working_drone_list.remove(d)

    def update_ongoing_construction(self, units_tag_dict: Dict[int, Unit]):
        ongoing_construction = []

        to_be_removed = []
        for d in self.working_drone_list:
            new_d = units_tag_dict.get(d.tag)
            if new_d is not None:
                if new_d.action_detail is not None:
                    # It should be not None but happens sometime
                    ongoing_construction.append(new_d.action_detail)
            else:
                to_be_removed.append(d)

        for d in to_be_removed:
            self.working_drone_list.remove(d)

        # for l in larva_list:
        #     new_l = units_tag_dict.get(l.tag)
        #     if new_l is not None:
        #         print(new_l)
        #         ongoing_construction.append(new_l.action_detail)
        #     else:
        #         self.working_larva_list.remove(l)

        self.ongoing_construction = ongoing_construction

    def get_count_ours_and_pending(self, units, unit_type):
        return len(get_all_owned(units, unit_type)) + len([
            u for u in self.units_pending if u['type'] == unit_type
        ]) + len([
            u for u in self.ongoing_construction if u['type'] == unit_type
        ])

    def get_count_pending(self, unit_type):
        return len([
            u for u in self.units_pending if u['type'] == unit_type
        ]) + len([
            u for u in self.ongoing_construction if u['type'] == unit_type
        ])


