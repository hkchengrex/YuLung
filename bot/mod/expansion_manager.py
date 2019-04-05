from pysc2.lib import point

from bot.struct.expansion import *
from bot.struct.unit_class import *
from bot.util.helper import *
from .low_level_module import LowLevelModule

"""
Constants
"""

RESOURCE_SPREAD_THRESHOLD = 1500

BASE_TO_EXPANSION_THRESHOLD = 1000

# TODO: IS THIS GOOD?
BUILDING_TO_EXPANSION_THRESHOLD = 1500


class ExpansionManager(LowLevelModule):
    """
    ExpansionManager
    - Record locations of expansions in the map
    - Record ownership of expansions
    """
    def __init__(self, global_info):
        super().__init__(global_info)

        self.expansion = []  # type: List[Expansion]

        # Hardcoded approximate enemy start location
        if 'Simple' in self.sc2_env._map_name:
            self.starting_points = None  # None means use the furthest expansion
        elif 'Abiogenesis' in self.sc2_env._map_name:
            self.starting_points = [point.Point(12400, 0), point.Point(0, 14000)]

    def own_expansion(self):
        return [e for e in self.expansion if e.ownership == Alliance.Self]

    def enemy_expansion(self):
        return [e for e in self.expansion if e.ownership == Alliance.Enemy]

    def neutral_expansion(self):
        return [e for e in self.expansion if e.ownership == Alliance.Neutral]

    def init_expansion(self, units: List[Unit]):
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
            for i, c in enumerate(clusters):
                print('Cluster: ', len(c), c[0].pos)
                # for m in c:
                    # print(m.unit_type, m.pos)

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
                if hatcheries[0].pos.dist(exp.pos) < BASE_TO_EXPANSION_THRESHOLD:
                    # self.owned_expansion.append(loc)
                    exp.ownership = Alliance.Self
                    exp.base = hatcheries[0]
                    exp.is_main = True
                    self.global_info.home_pos = exp.pos
                    self.logger.log_game_info('Initial own expansion: ' + str(exp))

            if len(self.own_expansion()) > 0:
                if self.starting_points is None:
                    # Assume the furthest base is the enemy base
                    max_dist = 0
                    enemy_exp = None
                    for exp in self.expansion:
                        dist = exp.pos.dist(self.own_expansion()[0].pos)
                        if dist > max_dist:
                            max_dist = dist
                            enemy_exp = exp
                else:
                    # First, find the furthest start point from our expansion
                    max_dist = 0
                    max_point = None
                    for sp in self.starting_points:
                        dist = sp.dist(self.own_expansion()[0].pos)
                        if dist > max_dist:
                            max_dist = dist
                            max_point = sp

                    # Find the expansion closest to the furthest starting point
                    min_dist = 2**31
                    enemy_exp = None
                    for exp in self.expansion:
                        dist = exp.pos.dist(max_point)
                        if dist < min_dist:
                            min_dist = dist
                            enemy_exp = exp

                enemy_exp.ownership = Alliance.Enemy
                enemy_exp.is_main = True
                self.logger.log_game_info('Initial enemy expansion: ' + str(enemy_exp))

    def claim_expansion(self, idx):
        # Instant claim, yeah
        exp = self.expansion[idx]
        if exp.ownership == Alliance.Enemy:
            self.logger.log_game_info('Attempt to claim an enemy expansion at %s' % str(exp.pos))
            pass
        elif exp.ownership == Alliance.Self:
            self.logger.log_game_info('Attempt to an claimed expansion at %s' % str(exp.pos))
            pass
        else:
            self.logger.log_game_info('Claimed expansion at %s ' % str(exp.pos))
            exp.ownership = Alliance.Self

    def update_expansion(self, units: typing.List[Unit], units_tag_dict: typing.Dict[int, Unit]):
        """
        Enemy's expansion is defined to be an expansion with a nearby enemy building (unmovable things)
        Our expansion is what we claim it is. It does not matter whether we have structures around it.
        We should, however, build a hatchery if any of our claimed base does not have one already.

        Expansions can be lost if
        1. we don't have an alive base there
        2. enemy has buildings there
        TODO: Build defensive structure in each expansion also
        """

        hatchery_build_pos = []

        self.init_expansion(units)

        enemy_buildings = get_all_enemy(units, ALL_BUILDING_ID)

        # First, refresh the list of expansions
        for exp in self.expansion:

            # Update expansion using observation
            exp.update(units_tag_dict)

            """
            This part deals with our bases
            """

            if exp.ownership == Alliance.Self:
                # Assume that our expansions are always ours. Bold claim though.

                # Build hatchery if we haven't
                if exp.base is None and not exp.base_queued:
                    exp.base_queued = True
                    hatchery_build_pos.append(exp.pos)
                    self.logger.log_game_info("Wanted to build hatchery at %s" % str(exp.pos))

                # Assign hatchery
                our_bases = get_all_owned(units, ZERG_BASES)

                for b in our_bases:
                    if b.pos.dist(exp.pos) < BASE_TO_EXPANSION_THRESHOLD:
                        exp.base = b
                        exp.base_queued = False

                if exp.base is not None:
                    # If we still have base there, we cannot lose it to the enemy
                    continue

            """
            This part deals with enemy's bases
            """

            belong_to_enemy = False
            for b in enemy_buildings:
                if b.pos.dist(exp.pos) < BUILDING_TO_EXPANSION_THRESHOLD:
                    exp.reset()
                    exp.ownership = Alliance.Enemy
                    belong_to_enemy = True
                    break

            new_ownership = None
            if belong_to_enemy:
                new_ownership = Alliance.Enemy
            elif exp.ownership == Alliance.Enemy and not exp.is_main:
                # Cannot convert enemy's main to neutral easily
                new_ownership = Alliance.Neutral

            # Update base ownership
            if new_ownership is not None:
                if new_ownership != exp.ownership:
                    self.logger.log_game_info('Expansion at %s ownership changed from %s to %s.' %
                                              (exp.pos, exp.ownership, new_ownership), False)
                    exp.ownership = new_ownership

        return hatchery_build_pos

    def get_next_expansion(self):
        """
        Obtain the next expansion to be used
        Based on sum of distances to existing expansion, pick the closest one
        """
        min_total_dist = 2**31
        min_total_idx = -1

        for i, n_exp in enumerate(self.expansion):
            # We don't directly get neutral expansions to preserve idx
            if n_exp.ownership != Alliance.Neutral:
                continue

            total_dist = 0
            for o_exp in self.own_expansion():
                total_dist += n_exp.pos.dist(o_exp.pos)
            if total_dist < min_total_dist:
                min_total_dist = total_dist
                min_total_idx = i

        return min_total_idx





