from pysc2.lib import actions


def get_raw_action_id(abaility_id):
    fn_list = list(actions.ABILITY_IDS[abaility_id])

    for l in fn_list:
        if 'raw' in l.name:
            return l
    return None
