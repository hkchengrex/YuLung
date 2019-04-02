from bot.util.static_units import UNITS, UnitID
from bot.util.id_lookup import *
from bot.util.unit_info import Attribute, Weapon, UnitType
from pysc2.lib.raw_units import RawUnit


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
    def is_comabt_unit(self):
        return self.unit_type not in [
            UnitID.Drone,
            UnitID.Overlord,
            UnitID.Larva,
        ] + ZERG_BUILDINGS_ID


