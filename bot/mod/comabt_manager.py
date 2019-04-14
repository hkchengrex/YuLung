import random

from pysc2.lib import actions
from pysc2.lib import point

from bot.util.helper import *
from bot.util.unit_ids import *
from bot.struct.expansion import Expansion
from .low_level_module import LowLevelModule

FUNCTIONS = actions.FUNCTIONS


class CombatManager(LowLevelModule):
    """
    CombatManager
    - Fight
    """
    def __init__(self, global_info):
        super().__init__(global_info)

        self._target = point.Point(0, 0)
        self._attack_mode = True
        self._target_changed = False

        self._annihilate_mode = False
        self._last_annihilate_target = None

    def set_attack_tar(self, target):
        if self._attack_mode and self._target == target and not self._annihilate_mode:
            return

        self._target = target
        self._attack_mode = True
        self._annihilate_mode = False
        self._target_changed = True

    def set_move_tar(self, target):
        if not self._attack_mode and self._target == target and not self._annihilate_mode:
            return

        self._target = target
        self._attack_mode = False
        self._annihilate_mode = False
        self._target_changed = True

    def try_annihilate(self):
        if self._annihilate_mode:
            return
        self._annihilate_mode = True
        self._target_changed = True
        self._last_annihilate_target = None

    def _get_free_combat_units(self, units):

        if self._target_changed:
            self._target_changed = False
            # Return units regardless of current order
            return [
                u.tag for u in units if u.alliance == Alliance.Self
                                        and u.is_combat_unit
                                        and not u.has_ongoing_action
            ]

        return [
            u.tag for u in units if u.alliance == Alliance.Self
                                    and u.is_combat_unit
                                    and not u.has_ongoing_action
                                    and u.order_len == 0
        ]

    def update(self, units: List[Unit], expansions: List[Expansion]):

        planned_action = None

        to_be_controlled = self._get_free_combat_units(units)

        if len(to_be_controlled) == 0:
            return planned_action

        if not self._annihilate_mode:
            if self._attack_mode:
                planned_action = FUNCTIONS.Attack_raw_pos("now", self._target, to_be_controlled)
            else:
                planned_action = FUNCTIONS.Move_raw_pos("now", self._target, to_be_controlled)

        else:
            buildings = get_all_enemy(units, ALL_BUILDING_ID)
            if len(buildings) > 0:
                print('Got building', buildings[0].pos)
                # CHARGE!
                if self._last_annihilate_target is None or buildings[0] != self._last_annihilate_target:
                    # Sees a new building, let's move everyone
                    self._last_annihilate_target = buildings[0]
                    self._target_changed = True
                    to_be_controlled = self._get_free_combat_units(units)  # Get everyone
                    planned_action = FUNCTIONS.Attack_raw_pos("now", buildings[0].pos, to_be_controlled)
                else:
                    # Send newbies to a random building
                    planned_action = FUNCTIONS.Attack_raw_pos("now", random.choice(buildings).pos, to_be_controlled)
            else:
                # Units will also do
                enemy_units = [u for u in units if u.alliance == Alliance.Enemy]
                if len(enemy_units) > 0:
                    print('Got unit', enemy_units[0].pos)
                    if self._last_annihilate_target is None or enemy_units[0] != self._last_annihilate_target:
                        self._last_annihilate_target = enemy_units[0]
                        self._target_changed = True
                        to_be_controlled = self._get_free_combat_units(units)  # Get everyone
                        planned_action = FUNCTIONS.Attack_raw_pos("now", enemy_units[0].pos, to_be_controlled)
                    else:
                        planned_action = FUNCTIONS.Attack_raw_pos("now", random.choice(enemy_units).pos,
                                                                  to_be_controlled)
                else:
                    # Search those bastard, send some
                    if len(to_be_controlled) > 10:
                        to_be_controlled = random.choices(to_be_controlled, k=int(len(to_be_controlled)*0.2))
                    print('Got nothing', len(to_be_controlled))
                    planned_action = FUNCTIONS.Attack_raw_pos("now", random.choice(expansions).pos,
                                                                to_be_controlled)

        return planned_action

