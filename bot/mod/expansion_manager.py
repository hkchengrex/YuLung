from pysc2.lib.units import Neutral
from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env
from pysc2.lib import point

from .low_level_module import LowLevelModule

from bot.util import unit_info
from bot.util.static_units import UNITS, UnitID

"""
Constants
"""

# From bot_ai.py of python_sc2
RESOURCE_SPREAD_THRESHOLD = 800
resources_id = [Neutral.MineralField, Neutral.MineralField750,
                Neutral.RichMineralField, Neutral.RichMineralField750,
                Neutral.VespeneGeyser, Neutral.RichVespeneGeyser]


class ExpansionManager(LowLevelModule):
    """
    ExpansionManager
    - records expansions in the map
    - Miners control
    """
    def __init__(self, global_info):
        super(ExpansionManager, self).__init__(global_info)

        self.expansion_locations = None
        self.owned_expansion = []
        self.enemy_expansion = []

    def refresh_expansion(self, units):
        """
        Finds all expansion locations by clustering the resources fields once
        Update expansion information
        :type units: list[ru.RawUnit]
        """
        if self.expansion_locations is None:
            """
            Initialize expansion information
            see bot_ai in python_sc2
            """
            clusters = []  # list of sets
            for u in units:
                if u.unit_type in resources_id:
                    for c in clusters:
                        if any(u.dist_to(other) < RESOURCE_SPREAD_THRESHOLD for other in c):
                            c.add(u)
                            break
                    else:
                        clusters.append({u})

            # Filter out those with only one mineral field
            clusters = [c for c in clusters if len(c) > 1]

            # Find centers
            self.expansion_locations = {}
            for c in clusters:
                center_pos = point.Point(sum([p.posx for p in c]) / len(c),
                              sum([p.posy for p in c]) / len(c))

                self.expansion_locations[center_pos] = c

            self.logger.log_game_info('Found %d expansions' % len(self.expansion_locations))

        if len(self.enemy_expansion) == 0:
            # Clear list to create again
            self.owned_expansion = []
            self.enemy_expansion = []

            hatcheries = unit_info.get_all_owned(units, UNITS[UnitID.Hatchery])
            for loc, _ in self.expansion_locations.items():
                if hatcheries[0].pos.dist(loc) < 1000:
                    self.owned_expansion.append(loc)
                    self.logger.log_game_info('We own expansion at ' + str(loc))

            if len(self.owned_expansion) > 0:
                max_dist = 0
                max_loc = None
                for loc, _ in self.expansion_locations.items():
                    if loc.dist(self.owned_expansion[0]) > max_dist:
                        max_loc = loc
                        max_dist = loc.dist(self.owned_expansion[0])

                self.enemy_expansion.append(max_loc)
                self.logger.log_game_info('Enemy expansion at ' + str(max_loc))

    def get_expansion_locations(self):
        return self.expansion_locations


