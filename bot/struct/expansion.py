import typing
from typing import Dict, List

from bot.struct.unit_class import Unit
from bot.util.unit_info import Alliance
from bot.util.unit_ids import *


class Expansion:
    """
    This class is describing a single expansion, including:
    - Location
    - List of unit id of minerals patches/gas
    - Ownership
    """

    def __init__(self, pos, minerals, gases, drones, ownership=Alliance.Neutral):
        self.pos = pos
        self.minerals = minerals
        self.gases = gases
        self.drones = drones
        
        self.ownership = ownership

        self.extractor = []  # type: List[Unit]
        self.base = None   # type: Optional[Unit] # Unit referring to hatchery/lair/hive
        self.is_main = False

        self.queen = None
        self.queen_queued = False

    def __str__(self):
        return 'Expansion at %s owned by %s' % (str(self.pos), str(self.ownership))

    def update(self, units_tag_dict: Dict[int, Unit]):
        if self.base is not None:
            self.base = units_tag_dict.get(self.base.tag, None)

    def get_ideal_harvesters(self):
        if self.base is not None:
            return self.base.ideal_harvesters
        else:
            return 0

    def get_assigned_harvesters(self):
        if self.base is not None:
            return self.base.assigned_harvesters
        else:
            return 0

    def reset(self):
        self.base = None
        self.base_queued = False
