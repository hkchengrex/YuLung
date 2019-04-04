import random

from bot.util.helper import *
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

        self.active_scout_tag = None  # type: int

        # Build DAG for tech requirement
        self.tech_DAG = {}
        for _, u in UNITS.items():
            self.tech_DAG[u.unit_id] = u.tech_requirement

    def set_scout_tar(self, targets):
        self.scout_targets = targets
        if len(self.scout_routine) == 0:
            self.scout_routine = self.scout_targets

    def update(self, units: List[Unit], units_tag_dict: Dict[int, Unit]):

        planned_action = None

        self.record_observation(units)

        active_scout = units_tag_dict.get(self.active_scout_tag, None)

        # Pick a scout
        if active_scout is None:
            overlords = get_all_owned(units, UNITS[UnitID.Overlord])
            if len(overlords) > 0:
                active_scout = random.choice(overlords)

        # Send it to scout
        if active_scout is not None:
            self.active_scout_tag = active_scout.tag
            active_scout.is_a_scout = True

            if active_scout.pos.dist(self.scout_routine[0]) < 500:
                # Reset target
                if len(self.scout_routine) == 1:
                    self.scout_routine = self.scout_targets
                else:
                    self.scout_routine = self.scout_routine[1:]
                active_scout.has_ongoing_action = False

            # Send action sparsely
            if not active_scout.has_ongoing_action:
                planned_action = get_raw_action_id(3674)("now", self.scout_routine[0], [self.active_scout_tag])
                active_scout.has_ongoing_action = True

        return planned_action

    def record_observation(self, units: List[Unit]):
        enemy_types = set([u.unit_type for u in units if u.alliance == Alliance.Enemy])
        new_types = enemy_types - self.seen_types

        if len(new_types) == 0:
            return

        self.seen_types = self.seen_types.union(new_types)
        self.logger.log_game_info('Scout sees something new: %s' % str(new_types))

        while len(new_types) > 0:
            unit_type = new_types[0]
            parent = self.tech_DAG[unit_type]
            if parent != 0 and parent not in self.seen_types:
                self.logger.log_game_info('Scout resolves something new: %s from DAG' % str(parent))
                new_types = new_types.remove(parent)






