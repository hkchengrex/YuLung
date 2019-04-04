import enum
import typing

from bot.util.unit_info import Alliance
from bot.struct.unit_class import Unit


class Expansion:
    """
    This class is describing a single expansion, including:
    - Location
    - List of unit id of minerals patches/gas
    - Ownership
    """

    def __init__(self, pos, minerals, gases, ownership=Alliance.Neutral):
        self.pos = pos
        self.minerals = minerals
        self.gases = gases

        self.ownership = ownership

        self.base = None  # Unit referring to hatchery/lair/hive
        self.base_queued = False
        self.is_main = False

    def __str__(self):
        return 'Expansion at %s owned by %s' % (str(self.pos), str(self.ownership))

    def update(self, units_tag_dict: typing.Dict[int, Unit]):
        if self.base is not None:
            self.base = units_tag_dict.get(self.base.tag, None)

    def reset(self):
        self.base = None
        self.base_queued = False
