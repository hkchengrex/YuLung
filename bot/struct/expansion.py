import enum
from bot.util.unit_info import Alliance


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

    def __str__(self):
        return 'Expansion at %s owned by %s' % (str(self.pos), str(self.ownership))
