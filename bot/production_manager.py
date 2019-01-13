from pysc2.lib.units import Zerg
from pysc2.lib import raw_units as ru
from pysc2.env.sc2_env import SC2Env

from .hypervisor import Hypervisor
from .low_level_module import LowLevelModule
from bot.util.game_logger import GameLogger
from bot.util.resources import Resources

class ProductionManager(LowLevelModule):
    """
    ProductionManager
    - Maintain queue of units/buildings production
    - Pick workers/lavras to build stuff
    """
    def __init__(self, hypervisor: Hypervisor):
        super(ProductionManager, self).__init__(hypervisor)

        self.units_pending = []
        self.buildings_pending = []

    def build_asap(self, unit_type: int, amount: int):
        self.units_pending.extend([unit_type] * amount)

    def update(self, units):
        for u in self.units_pending:
            pass

