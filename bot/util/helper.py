from pysc2.lib import actions

from bot.struct.unit_class import *
from bot.util.unit_info import *


def get_raw_pos_action_id(ability_id):
    fn_list = list(actions.ABILITY_IDS[ability_id])

    for l in fn_list:
        if 'raw_pos' in l.name:
            return l
    return None


def get_raw_quick_action_id(ability_id):
    fn_list = list(actions.ABILITY_IDS[ability_id])

    for l in fn_list:
        if 'raw_quick' in l.name:
            return l
    return None


def get_raw_targeted_action_id(ability_id):
    fn_list = list(actions.ABILITY_IDS[ability_id])

    for l in fn_list:
        if 'raw_targeted' in l.name:
            return l
    return None


def get_all(units, unit_type, ownership=None) -> List[Unit]:
    """
    Returns all matching units in the units list

    The unit_type can be a list or a single value
    It can contain int (unit_id) or UnitType

    When ownership is None, it returns units owned by all parties
    """

    if len(units) == 0:
        return []

    """
    This part transform whatever in unit_type into a list of unit ids
    So that we can use the "in" operator, yeah Python!
    """
    if type(unit_type) != list:
        if type(unit_type) == UnitType:
            unit_type_list = [unit_type.unit_id]
        else:
            unit_type_list = [unit_type]
    else:
        if type(unit_type[0]) == UnitType:
            unit_type_list = [u.unit_id for u in unit_type]
        else:
            unit_type_list = unit_type

    if ownership is None:
        if type(units[0]) == UnitType:
            return [u for u in units if u.unit_id in unit_type_list]
        else:
            return [u for u in units if u.unit_type in unit_type_list]
    else:
        return [u for u in units if u.unit_type in unit_type_list and u.alliance == ownership]


def get_all_owned(units, unit_type):
    return get_all(units, unit_type, Alliance.Self)


def get_all_enemy(units, unit_type):
    return get_all(units, unit_type, Alliance.Enemy)


_sc2_to_ours_reverse_id = {}
for _, u in UNITS.items():
    _sc2_to_ours_reverse_id[u.unit_id] = u

alliance_to_id = {Alliance.Self:0, Alliance.Neutral:1, Alliance.Enemy:2}


def rev_id2type(unit_id: int) -> UnitType:
    return _sc2_to_ours_reverse_id[unit_id]
