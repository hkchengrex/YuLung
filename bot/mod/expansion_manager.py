from pysc2.lib import point

from bot.struct.expansion import *
from bot.struct.unit_class import *
from bot.util.helper import *
from .low_level_module import LowLevelModule
from bot.queries import *
from .production_manager import ProductionManager

FUNCTIONS = actions.FUNCTIONS

"""
Constants
"""

RESOURCE_SPREAD_THRESHOLD = 1500

BASE_TO_EXPANSION_THRESHOLD = 1000

# TODO: IS THIS GOOD?
BUILDING_TO_EXPANSION_THRESHOLD = 1000


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

    def main_expansion(self):
        for e in self.own_expansion():
            if e.is_main:
                return e
        return None

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
            # for i, c in enumerate(clusters):
            #     print('Cluster: ', len(c), c[0].pos)
            #     for m in c:
            #         print(m.unit_type, m.pos)

            # Find centers
            for c in clusters:
                center_pos = point.Point(sum([p.posx for p in c]) / len(c),
                              sum([p.posy for p in c]) / len(c))

                minerals = [m for m in c if m.unit_type in MINERAL_UNIT_ID]
                gases = [g for g in c if g.unit_type in GAS_UNIT_ID]
                drones = []
                self.expansion.append(Expansion(center_pos, minerals, gases, drones))

            self.logger.log_game_info('Found %d expansions' % len(self.expansion))

            # Sort the expansions using distance to lower left corner
            self.expansion = sorted(self.expansion, key=lambda x: x.pos.dist(point.Point(0, 0)))

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
        queens_to_be_build = 0

        self.init_expansion(units)

        enemy_buildings = get_all_enemy(units, ALL_BUILDING_ID)
        extractors = get_all_owned(units, UNITS[UnitID.Extractor])

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

                # Assign extractors
                exp.extractor = [
                    e for e in extractors if e.pos.dist(exp.pos) < RESOURCE_SPREAD_THRESHOLD
                ]

                for b in our_bases:
                    if b.pos.dist(exp.pos) < BASE_TO_EXPANSION_THRESHOLD:
                        exp.base = b
                        exp.base_queued = False

                if exp.base is not None:
                    if exp.queen is not None:
                        # Reset if dead
                        exp.queen = units_tag_dict.get(exp.queen.tag)

                    if exp.queen is None and self.global_info.has_pool:
                        # The queen will inject me but not in this update function

                        if exp.queen_queued:
                            # Look for a queen
                            queens = get_all_owned(units, UNITS[UnitID.Queen])
                            queens = [q for q in queens if not q.has_ongoing_action]
                            if len(queens) > 0:
                                exp.queen = queens[0]
                                exp.queen.has_ongoing_action = True
                        else:
                            exp.queen_queued = True
                            queens_to_be_build += 1

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
            elif exp.ownership == Alliance.Enemy:
                if exp.is_main:
                    # Cannot convert enemy's main to neutral easily
                    # we need a nearby unit, otherwise we would convert it to neutral at first game step
                    for u in [u for u in units if u.alliance == Alliance.Self]:
                        if u.pos.dist(exp.pos) < 500:
                            new_ownership = Alliance.Neutral
                else:
                    new_ownership = Alliance.Neutral

            # Update base ownership
            if new_ownership is not None:
                if new_ownership != exp.ownership:
                    self.logger.log_game_info('Expansion at %s ownership changed from %s to %s.' %
                                              (exp.pos, exp.ownership, new_ownership), False)
                    exp.ownership = new_ownership

        return hatchery_build_pos, queens_to_be_build

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

    def queen_inject(self):
        for exp in self.own_expansion():
            if exp.base is not None and exp.queen is not None:
                avail_abilities = query_available_abilities(self.sc2_env, exp.queen.tag)
                if 251 in avail_abilities:
                    planned_action = FUNCTIONS.Effect_InjectLarva_raw_targeted('now', exp.base.tag, exp.queen.tag)
                    return planned_action

    """
    Only return each gas position once.
    Therefore, once returned, you better build it.
    """
    def get_next_gas(self, units):
        if len(self.own_expansion()) == 0:
            return None

        extractors = get_all_owned(units, UNITS[UnitID.Extractor])

        gases = get_all(units, GAS_UNIT_ID)
        gases = [g for g in gases if g.display_type == 1 and not g.has_ongoing_action]
        # gases = [g for g in gases]

        empty_gases = [
            g for g in gases if
            not any([ex.pos.dist(g.pos) < 100 for ex in extractors])
        ]

        for g in empty_gases:
            if g.pos.dist(self.main_expansion().pos) < BUILDING_TO_EXPANSION_THRESHOLD:
                g.has_ongoing_action = True
                return g

        for exp in self.own_expansion():
            for g in empty_gases:
                if g.pos.dist(exp.pos) < BUILDING_TO_EXPANSION_THRESHOLD:
                    g.has_ongoing_action = True
                    return g

        return None

