import random

from .low_level_module import LowLevelModule

from .util.static_units import UNITS, UnitID
from .util.unit import Attribute, Weapon, UnitType

from pysc2.lib import actions
FUNCTIONS = actions.FUNCTIONS


class ProductionManager(LowLevelModule):
    """
    ProductionManager
    - Maintain queue of units/buildings production
    - Pick workers/lavras to build stuff
    """
    def __init__(self, hypervisor):
        super(ProductionManager, self).__init__(hypervisor)

        self.units_pending = []
        self.buildings_pending = []

        self.build_asap(UNITS[UnitID.Drone])

    def build_asap(self, unit_type: UnitType, amount=1):
        self.units_pending.extend([unit_type] * amount)

    def update(self, units):
        for unit_type in self.units_pending:
            if self.global_info.can_afford_unit(unit_type):

                larvas = [larva for larva in units if larva.unit_type == UNITS[UnitID.Larva].unit_id]
                if len(larvas) > 0:
                    self.logger.log_game_info("Planning to build unit of type: " + unit_type.name)
                    selected_larva = random.choice(larvas)
                    return list(actions.ABILITY_IDS[unit_type.ability_id])[0]("now", selected_larva.tag)

        return None

