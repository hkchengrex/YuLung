import numpy as np
from pysc2.lib import actions
import common.utils as U
from pysc2.lib import actions, features

## General Player Information ##

FUNCTIONS = actions.FUNCTIONS


## Action Space ##

## Action ID [3]
## Point / Unit Action [4]
## Unit ID [500]
## Point [84,84]
## select_add [2]

class ActionTransform:

    def __init__(self):
        """
        Define Action Space
        """
        """
        Define the discrete space
        """
        ###
        self.discrete_space = [3,2,2,84,84]
        ###
        self.n_dis_out = len(self.discrete_space)
        """
        Define the continous space
        """
        ###
        self.high = np.array([200])
        self.low = np.array([0])
        ###
        self.n_con_out = len(self.high)

    def transform(self, action):
        action = {"discrete_output": action[0].astype(int), "continous_output": action[1]}
        """
            Define the action space mapping
        """
        #################Define#########################
        action_id = action["discrete_output"][0]
        action_act = action["discrete_output"][1]
        unit_id = action["discrete_output"][2]
        x = action["discrete_output"][3]
        y = action["discrete_output"][4]
        temp = action["continous_output"][0]
        ################################################

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
