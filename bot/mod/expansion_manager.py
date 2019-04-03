import typing

from pysc2.lib.units import Neutral, Terran, Zerg, Protoss
from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env
from pysc2.lib import point

from .low_level_module import LowLevelModule

from bot.util.helper import *

from bot.struct.expansion import *
from bot.struct.unit_class import *

"""
Constants
"""

RESOURCE_SPREAD_THRESHOLD = 1500

# TODO: IS THIS GOOD?
BUILDING_TO_EXPANSION_THRESHOLD = 5000


class ExpansionManager(LowLevelModule):
    """
    ExpansionManager
    - Record locations of expansions in the map
    - Record ownership of expansions
    """
    def __init__(self, global_info):
        super(ExpansionManager, self).__init__(global_info)

        self.expansion = []  # type: typing.List[Expansion]

    def own_expansion(self):
        return [e for e in self.expansion if e.ownership == Alliance.Self]

    def enemy_expansion(self):
        return [e for e in self.expansion if e.ownership == Alliance.Enemy]

    def init_expansion(self, units: typing.List[Unit]):
        """
        - Finds all expansion locations by clustering the resources fields once
        - Find initial set of owned/enemy's base
        """
        if len(self.expansion) == 0:
            """
            Initialize expansion information
            see bot_ai in python_sc2
            """
            clusters = []  # list of lists
            for u in units:
                if u.unit_type in (MINERAL_UNIT_ID + GAS_UNIT_ID):
                    # print(u.unit_type, u.pos)
                    for c in clusters:
                        if any(u.dist_to(other) < RESOURCE_SPREAD_THRESHOLD for other in c):
                            c.append(u)
                            break
                    else:
                        clusters.append([u])

            # Debug
            # for i, c in enumerate(clusters):
            #     print('Cluster: ', len(c), c[0].pos)
            #     # for m in c:
            #         # print(m.unit_type, m.pos)

            # TODO: NOT RELIABLE IN LARGER/ACTUAL MAP!!!!!!!!
            # Find centers
            for c in clusters:
                center_pos = point.Point(sum([p.posx for p in c]) / len(c),
                              sum([p.posy for p in c]) / len(c))

                minerals = [u for u in c if u.unit_type in MINERAL_UNIT_ID]
                gases = [u for u in c if u.unit_type in GAS_UNIT_ID]
                self.expansion.append(Expansion(center_pos, minerals, gases))

            self.logger.log_game_info('Found %d expansions' % len(self.expansion))

        # The following part just find the initial set of bases
        if len(self.enemy_expansion()) == 0:

            # Find our starting expansion using distance to hatchery
            hatcheries = get_all_owned(units, UNITS[UnitID.Hatchery])
            for exp in self.expansion:
                if hatcheries[0].pos.dist(exp.pos) < 2000:
                    # self.owned_expansion.append(loc)
                    exp.ownership = Alliance.Self
                    self.logger.log_game_info('Initial own expansion: ' + str(exp))

            # Assume the furthest base is the enemy base
            if len(self.own_expansion()) > 0:
                max_dist = 0
                max_dist_exp = None
                for exp in self.expansion:
                    if exp.pos.dist(self.own_expansion()[0].pos) > max_dist:
                        max_dist_exp = exp
                        max_dist = exp.pos.dist(self.own_expansion()[0].pos)

                max_dist_exp.ownership = Alliance.Enemy
                self.logger.log_game_info('Initial enemy expansion: ' + str(max_dist_exp))

    def update_expansion(self, units: typing.List[Unit]):
        """
        Enemy's expansion is defined to be an expansion with a nearby enemy building (unmovable things)
        Our expansion is what we claim it is. It does not matter whether we have structures around it.
        We should, however, build a hatchery if any of our claimed base does not have one already.
        TODO: Build defensive structure in each expansion also
        TODO: Allow "losing" an expansion
        """

        self.init_expansion(units)

        enemy_buildings = get_all_enemy(units, ALL_BUILDING_ID)

        # First, refresh the list of enemy expansions
        for exp in self.expansion:
            if exp.ownership == Alliance.Self:
                # Assume that our expansions are always ours. Bold claim though.
                continue

            belong_to_enemy = False
            for b in enemy_buildings:
                if b.pos.dist(exp.pos) < BUILDING_TO_EXPANSION_THRESHOLD:
                    exp.ownership = Alliance.Enemy
                    belong_to_enemy = True
                    break
            if belong_to_enemy:
                new_ownership = Alliance.Enemy
                if new_ownership != exp.ownership:
                    self.logger.log_game_info('Expansion at %s ownership changed from %s to %s.' %
                                              (exp.pos, exp.ownership, new_ownership), False)

                exp.ownership = new_ownership




