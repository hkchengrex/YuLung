from .low_level_module import LowLevelModule

from bot.util.static_units import UNITS, UnitID
from bot.util.unit_info import Attribute, Weapon, UnitType
from bot.util.helper import *
from bot.queries import *

from pysc2.lib import actions
from pysc2.lib import point
FUNCTIONS = actions.FUNCTIONS


class CombatManager(LowLevelModule):
    """
    CombatManager
    - Fight
    """
    def __init__(self, global_info):
        super().__init__(global_info)

        self.queued = []
        self.attack_target = point.Point(0, 0)

    def set_attack_tar(self, target):
        self.attack_target = target

    def update(self, units):

        planned_action = None

        # Need to command one-by-one now, will add batched command later in pysc2
        if len(self.queued) != 0:
            # avail_abilities = query_available_abilities(self.sc2_env, u.tag)
            # attack_id = FUNCTIONS.Attack_raw_pos.id
            # print(attack_id)
            # print(avail_abilities)
            # if attack_id in avail_abilities:
            self.logger.log_game_verbose('Planning to attack')
            planned_action = get_raw_action_id(3674)("now", self.attack_target, [u.tag for u in self.queued])
            self.queued = []
        else:
            self.queued = get_all(units, UNITS[UnitID.Zergling])
            if len(self.queued) <= 8:
                self.queued = []

        return planned_action

