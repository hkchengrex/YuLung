from bot.util.unit_ids import *

from pysc2.lib.raw_units import RawUnit

from bot.util.unit_ids import *


class Unit(RawUnit):
    """
    This class is an addition wrapper to raw_unit
    You can add addition additional properties here for ease of programming
    """
    def __init__(self, np_array):
        # A hack to copy all parameters from base class to derived class
        # self.__dict__.update(raw_unit.__dict__)
        super().__init__(np_array)

        self.has_ongoing_action = False
        self.is_a_scout = False

    @property
    def is_combat_unit(self):
        if self.is_a_scout:
            return False

        return self.unit_type not in [
            UNITS[UnitID.Drone],
            UNITS[UnitID.Overlord],
            UNITS[UnitID.Larva],
        ] + ZERG_BUILDINGS_TYPE

    def update(self, old_unit):
        """
        Propagate all custom information from old_unit to self.
        Returns self.
        """

        if old_unit is not None:
            self.has_ongoing_action = old_unit.has_ongoing_action
            self.is_a_scout = old_unit.is_a_scout

        return self
