from .low_level_module import LowLevelModule

from bot.util.static_units import UNITS, UnitID
from bot.util.unit import Attribute, Weapon, UnitType
from bot.util.helper import *
from bot.util import unit
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
        super(CombatManager, self).__init__(global_info)

        self.queued = []

    def update(self, units):

        # Need to command one-by-one now, will add batched command later in pysc2
        if len(self.queued) != 0:
            u = self.queued.pop(0)

            avail_abilities = query_available_abilities(self.sc2_env, u.tag)
            # attack_id = FUNCTIONS.Attack_raw_pos.id
            # print(attack_id)
            # print(avail_abilities)
            # if attack_id in avail_abilities:
            self.logger.log_game_info("Planning to attack")
            return get_raw_action_id(3674)("now", point.Point(6000, 0), u.tag)

        else:
            self.queued = unit.get_all(units, UNITS[UnitID.Zergling])
            if len(self.queued) <= 8:
                self.queued = []

        return None

