import random

from .low_level_module import LowLevelModule

from bot.util.static_units import UNITS, UnitID
from bot.util.unit_info import Attribute, Weapon, UnitType
from bot.util.helper import *
from bot.queries import *

from pysc2.lib import actions
from pysc2.lib import point
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

        self.active_scout = None  # type: Unit

    def set_scout_tar(self, targets):
        self.scout_targets = targets
        if len(self.scout_routine) == 0:
            self.scout_routine = self.scout_targets

    def update(self, units):

        planned_action = None

        # Find scout
        if self.active_scout is not None:
            scout_found = False
            for u in units:
                if self.active_scout.tag == u.tag:
                    self.active_scout = u
                    scout_found = True

            if not scout_found:
                self.active_scout = None  # Whoops it is dead

        # Pick a scout
        if self.active_scout is None:
            overlords = get_all_owned(units, UNITS[UnitID.Overlord])
            if len(overlords) > 0:
                self.active_scout = random.choice(overlords)

        # Send it to scout
        if self.active_scout.pos.dist(self.scout_routine[0]) < 500:
            # Reset target
            if len(self.scout_routine) == 1:
                self.scout_routine = self.scout_targets
            else:
                self.scout_routine = self.scout_routine[1:]

            print(self.scout_targets, self.scout_routine)

        # Send
        # TODO: Dont send every time
        planned_action = get_raw_action_id(3674)("now", self.scout_routine[0], [self.active_scout.tag])

        return planned_action

