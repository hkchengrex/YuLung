import numpy as np
from pysc2.lib import actions

FUNCTIONS = actions.FUNCTIONS


class ActionTransform:

    def __init__(self):
        # (action) Define the Number of Classes of Discrete Action Space
        self.discrete_space = [3, 2, 2, 84, 84]
        # ####
        self.n_dp = len(self.discrete_space)

        # (action) Define the Limit of the Continous Action Space
        self.high = np.array([200, 300])
        self.low = np.array([0, 0])
        # ####

        self.n_cp = len(self.high)

    '''
    def transform(self, action):
 
        action = {"discrete_output": action[0].astype(int), "continous_output": action[1]}
 
        action_id = action["discrete_output"][0]
        action_act = action["discrete_output"][1]
        unit_id = action["discrete_output"][2]
        x = action["discrete_output"][3]
        y = action["discrete_output"][4]
        temp = action["continous_output"][0]
        temp2 = action["continous_output"][1]
 
        ##################### sample testing #########################
        if action_id == 0:
            action_plan = [FUNCTIONS.Move_screen.id, [action_act], (x, y)]
        elif action_id == 1:
            action_plan = [FUNCTIONS.select_point.id, [action_act], (x, y)]
        elif action_id == 2:
            action_plan = [FUNCTIONS.select_army.id, [action_act]]
        else:
            action_plan = [FUNCTIONS.no_op.id]
 
        return action_plan
    '''
