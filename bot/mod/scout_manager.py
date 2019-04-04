import random

from pysc2.lib import actions

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

        self.seen_buildings = []
        self.scout_targets = []
        self.scout_routine = []

        self.active_scout_tag = None  # type: int

    def set_scout_tar(self, targets):
        self.scout_targets = targets
        if len(self.scout_routine) == 0:
            self.scout_routine = self.scout_targets

    def update(self, units: typing.List[Unit], units_tag_dict: typing.Dict[int, Unit]):

        planned_action = None

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

