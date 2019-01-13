from pysc2.lib.units import Neutral
from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env

from .hypervisor import Hypervisor
from .low_level_module import LowLevelModule
from bot.util.game_logger import GameLogger

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
    def __init__(self, hypervisor: Hypervisor):
        super(ExpansionManager, self).__init__(hypervisor)

        self.expansion_locations = None

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
                center_pos = (sum([p.posx for p in c]) / len(c),
                              sum([p.posy for p in c]) / len(c))

                self.expansion_locations[center_pos] = c

            print('Found %d expansions' % len(self.expansion_locations))


    def get_expansion_locations(self):
        return self.expansion_locations


