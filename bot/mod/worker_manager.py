import random

from pysc2.lib import actions
from pysc2.lib import point

from bot.util.helper import *
from bot.util.unit_ids import *
from .low_level_module import LowLevelModule

FUNCTIONS = actions.FUNCTIONS


class WorkerManager(LowLevelModule):
    def __init__(self, global_info):
        super(WorkerManager, self).__init__(global_info)
        
        self.tracked_drones = []
        
    def track(self, units, expansion):
        all_bases = get_all_owned(units, ZERG_BASES)
        all_drones = get_all_owned(units, UNITS[UnitID.Drone])

        expansions = [exp for exp in expansion if exp.ownership == Alliance.Self]

        for exp in expansions:
            if exp.is_main is True and len(exp.drones) == 0:
                for drone in all_drones:
                    exp.drones.append(drone)
                    self.tracked_drones.append(drone)
        
        dead_drones = [d for d in self.tracked_drones if d not in all_drones]
        for dead_d in dead_drones:
            print("\nRemoving Dead Drones\n")
            for exp in expansions:
                if dead_d in exp.drones:
                    exp.drones.remove(dead_d)
            self.tracked_drones.remove(dead_d)
            
        """
        for i in range(len(expansions)):
            print("Drones in Base", i, ":", len(expansions[i].drones), expansions[i].get_assigned_harvesters(), expansions[i].get_ideal_harvesters())
        print("Total Drones", len(self.tracked_drones))
        """

    def get_deficiency(self, expansion):
        deficient_exp = [exp for exp in expansion if exp.ownership == Alliance.Self and exp.get_assigned_harvesters() < exp.get_ideal_harvesters()]
        deficiency = 0
        for exp in deficient_exp:
            deficiency += exp.get_ideal_harvesters() - exp.get_assigned_harvesters()
        return deficiency
        
        
    def assign(self, units, expansion):
        
        planned_action = None

        all_drones = get_all_owned(units, UNITS[UnitID.Drone])
        expansions = [exp for exp in expansion if exp.ownership == Alliance.Self]

        extractors = get_all(units, UNITS[UnitID.Extractor])
        
        untracked_drones = [d for d in all_drones if d not in self.tracked_drones]
        
        if len(untracked_drones) > 0:
            selected_drone = random.choice(untracked_drones)
            for exp in expansions:
                
                if len(extractors) > 0:
                    for extract in extractors:
                        if extract.build_progress == 100 and extract.assigned_harvesters < extract.ideal_harvesters:
                            planned_action = FUNCTIONS.Harvest_Gather_raw_targeted("now", extract.tag, [selected_drone.tag])
                            print("\nDrone Assigned to Extractor", extractors.index(extract), "\n")

                            return planned_action
                        
                #Assign Worker to Mineral Field
                if exp.get_assigned_harvesters() < exp.get_ideal_harvesters() or (exp.base.build_progress < 100 and len(exp.drones) < len(exp.minerals)*2):                    
                    base_pos = point.Point(exp.base.posx, exp.base.posy)
                    minerals = get_all(units, UNITS[UnitID.MineralField])
                    closest_pos = point.Point(minerals[0].posx, minerals[0].posy)
                    closest_m = minerals[0]
                    for m in minerals:
                        pos = point.Point(m.posx, m.posy)
                        if base_pos.dist(pos) < base_pos.dist(closest_pos):
                            closest_pos = pos
                            closest_m = m

                    planned_action = FUNCTIONS.Harvest_Gather_raw_targeted("now", closest_m.tag, [selected_drone.tag])
                    
                    exp.drones.append(selected_drone)
                    self.tracked_drones.append(selected_drone)
                    print("\nDrone Assigned to Base", expansions.index(exp), "\n")
                    
                    return planned_action

        return planned_action
        

