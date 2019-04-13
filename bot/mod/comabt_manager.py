import random

from pysc2.lib import actions
from pysc2.lib import point

from bot.util.helper import *
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

        self.queued = []
        self.target = point.Point(0, 0)
        self.attack_mode = True
        self.target_changed = False

        self.annihilate_mode = False
        self.last_annihilate_target = None

    def set_attack_tar(self, target):
        if self.attack_mode and self.target == target and not self.annihilate_mode:
            return

        self.target = target
        self.attack_mode = True
        self.annihilate_mode = False
        self.target_changed = True

    def set_move_tar(self, target):
        if not self.attack_mode and self.target == target and not self.annihilate_mode:
            return

        self.target = target
        self.attack_mode = False
        self.annihilate_mode = False
        self.target_changed = True

    def try_annihilate(self):
        if self.annihilate_mode:
            return
        self.annihilate_mode = True
        self.target_changed = True

    def _get_free_combat_units(self, units):

        if self.target_changed:
            self.target_changed = False
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
            return None

        if not self.annihilate_mode:
            if self.attack_mode:
                planned_action = FUNCTIONS.Attack_raw_pos("now", self.target, to_be_controlled)
            else:
                planned_action = FUNCTIONS.Move_raw_pos("now", self.target, to_be_controlled)

        else:
            buildings = get_all_enemy(units, ALL_BUILDING_ID)
            if len(buildings) > 0:
                # CHARGE!
                if self.last_annihilate_target is None or buildings[0] != self.last_annihilate_target:
                    self.last_annihilate_target = buildings[0]
                    self.target_changed = True
                    planned_action = FUNCTIONS.Attack_raw_pos("now", buildings[0].pos, to_be_controlled)
            else:
                # Units will also do
                enemy_units = [u for u in units if u.alliance == Alliance.Enemy]
                if len(enemy_units) > 0:
                    if self.last_annihilate_target is None or enemy_units[0] != self.last_annihilate_target:
                        self.last_annihilate_target = enemy_units[0]
                        self.target_changed = True
                        planned_action = FUNCTIONS.Attack_raw_pos("now", buildings[0].pos, to_be_controlled)
                else:
                    # Search those bastard, send one only
                    planned_action = FUNCTIONS.Attack_raw_pos("now", random.choice(expansions).pos,
                                                              to_be_controlled[0:1])

        return planned_action

