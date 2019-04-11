import random

from bot.util.helper import *
from bot.util.unit_ids import *
from .low_level_module import LowLevelModule

FUNCTIONS = actions.FUNCTIONS


class ScoutManager(LowLevelModule):
    """
    ScoutingManager
    - Send scouts to scout
    - Record seen things
    """
    def __init__(self, global_info):
        super().__init__(global_info)

        self.seen_types = set()
        self.recorded_tech = set()

        self.scout_targets = []
        self.scout_routine = []

        self.curr_target = None

        self.enemy_tech = [False] * len(TECH_BUILDING_TYPE)
        self.enemy_strong_cloak = False

        self.active_scout_tag = None  # type: int
        self.do_scout = False

        # Build DAG for tech requirement
        self.tech_DAG = {}
        for _, u in UNITS.items():
            self.tech_DAG[u.unit_id] = u.tech_requirement

    def set_scout_tar(self, targets):
        self.scout_targets = targets

    def go_scout_once(self):
        self.do_scout = True

    def update(self, units: List[Unit], units_tag_dict: Dict[int, Unit]):

        planned_action = None

        self.record_observation(units)

        active_scout = units_tag_dict.get(self.active_scout_tag, None)

        # Pick a scout
        if active_scout is None:
            overlords = get_all_owned(units, UNITS[UnitID.Overlord])
            if len(overlords) > 0:
                active_scout = random.choice(overlords)
                active_scout.is_a_scout = True

        # Send it to scout
        if active_scout is not None:
            self.active_scout_tag = active_scout.tag

            # Send action once per target
            if not active_scout.has_ongoing_action:
                if len(self.scout_routine) == 0:
                    self.curr_target = self.global_info.home_pos
                else:
                    self.curr_target = self.scout_routine[0]
                    self.scout_routine = self.scout_routine[1:]

                active_scout.has_ongoing_action = True

            # Change to next target when reached
            if active_scout.pos.dist(self.curr_target) < 500:
                # Reset target
                if len(self.scout_routine) == 0 and self.do_scout:
                    self.scout_routine = self.scout_targets
                    self.do_scout = False
                active_scout.has_ongoing_action = False

            elif active_scout.order_len == 0:
                planned_action = FUNCTIONS.Move_raw_pos("now", self.curr_target, [self.active_scout_tag])

        return planned_action

    def record_observation(self, units: List[Unit]):
        enemy_types = set([u.unit_type for u in units if u.alliance == Alliance.Enemy])
        new_types = enemy_types - self.seen_types

        if len(new_types) == 0:
            return

        self.seen_types = self.seen_types.union(new_types)

        while len(new_types) > 0:
            unit_type = new_types.pop()
            self.logger.log_game_info('Scout sees something new: %s' % rev_id2type(unit_type).name)
            new_types.discard(unit_type)  # Remove will give key error

            # Update tech vector
            if rev_id2type(unit_type) in TECH_BUILDING_TYPE:
                self.enemy_tech[TECH_BUILDING_TYPE.index(rev_id2type(unit_type))] = True

            # Update strong cloak flag
            if not self.enemy_strong_cloak and unit_type in STRONG_CLOAK_TYPE:
                self.enemy_strong_cloak = True

            # Resolve DAG
            parent = self.tech_DAG[unit_type]
            if parent != 0 and parent not in self.seen_types:
                self.logger.log_game_info('DAG resolved something new: %s' % rev_id2type(parent).name)
                new_types.add(parent)
                self.seen_types.add(parent)






