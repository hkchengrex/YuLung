import typing

from bot.struct.unit_class import Unit

"""
As the list of units refresh every observation, we need to keep track of some of the units
to maintain a consistent reference to their true up-to-date properties like health, mana, position, etc.

In the sub-modules, please use the unit tag to obtain the most up-to-date unit information here.
"""


class ConsistentUnits:
    def __init__(self):
        self.units_tag_dict = {}  # type: typing.Dict[int, Unit]
        self.units = []  # type: typing.List[Unit]

    def update(self, raw_units):
        self.units = [Unit(u) for u in raw_units]
        new_units_tag_dict = {}

        for u in self.units:
            new_units_tag_dict[u.tag] = u.update(
                self.units_tag_dict.get(u.tag, None))

        self.units_tag_dict = new_units_tag_dict



