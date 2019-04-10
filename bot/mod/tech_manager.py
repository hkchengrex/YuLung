import random

from pysc2.lib import actions
from pysc2.lib import point

from bot.queries import *
from bot.util import grid_ordering
from bot.util.helper import *
from bot.util.unit_ids import *
from bot.struct.unit_class import *
from .low_level_module import LowLevelModule

FUNCTIONS = actions.FUNCTIONS


class TechManager(LowLevelModule):
    """
    TechManager
    - Maintain list of researched technology/building prerequistite
    - Maintain tech requirement, i.e. when pool is destoryed, it will be rebuilt
    """
    def __init__(self, global_info):
        super().__init__(global_info)

    def update(self, units, units_tag_dict):
        pass