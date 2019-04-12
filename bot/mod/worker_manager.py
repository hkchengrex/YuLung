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
        self.drones_on_gas = []
        
    def track(self, units, expansion):
        all_drones = get_all_owned(units, UNITS[UnitID.Drone])

        expansions = [exp for exp in expansion if exp.ownership == Alliance.Self]

        for exp in expansions:
            if exp.is_main is True and len(exp.drones) == 0:
                for drone in all_drones:
                    exp.drones.append(drone)
                    self.tracked_drones.append(drone)
        
        dead_drones = [d for d in self.tracked_drones if d not in all_drones and d not in self.drones_on_gas]
        for dead_d in dead_drones:
            for exp in expansions:
                if dead_d in exp.drones:
                    # print("\nRemoving Dead Mineral Drones\n")
                    exp.drones.remove(dead_d)
            self.tracked_drones.remove(dead_d)
            
        """
        for i in range(len(expansions)):
            print("Drones in Base", i, ":", len(expansions[i].drones), expansions[i].get_assigned_harvesters(), expansions[i].get_ideal_harvesters())4        
        print("Tracked Drones", len(self.tracked_drones), "OBS Drones", len(all_drones))
        """

    def get_deficiency(self, units, expansion):
        deficient_exp = [exp for exp in expansion if exp.ownership == Alliance.Self and exp.get_assigned_harvesters() < exp.get_ideal_harvesters()]        
        deficiency = 0
        for exp in deficient_exp:
            deficiency += exp.get_ideal_harvesters() - exp.get_assigned_harvesters()        
        return deficiency + self.get_gas_deficiency(units)

    def get_gas_deficiency(self, units):
        """
        extractors = get_all_owned(units, UNITS[UnitID.Extractor])
        deficiency = 0
        for ext in extractors:
            if ext.build_progress == 100:
                deficiency += ext.ideal_harvesters - ext.assigned_harvesters
        return deficiency
        """
        return self.get_gas_slots(units) - len(self.drones_on_gas)
    

    def get_gas_slots(self, units):
        extractors = get_all_owned(units, UNITS[UnitID.Extractor])
        gas_slots = 0
        for ext in extractors:
            if ext.build_progress == 100:
                gas_slots += ext.ideal_harvesters
        return gas_slots
    
    """
    def get_drones_on_gas(self, units):
        extractors = get_all_owned(units, UNITS[UnitID.Extractor])
        drones_on_gas = 0
        for ext in extractors:
            if ext.build_progress == 100:
                drones_on_gas += ext.assigned_harvesters
        return drones_on_gas
    """

    def assign_gas(self, units, expansions, untracked_drones, ratio):
        planned_action = None

        extractors = [ext for ext in get_all_owned(units, UNITS[UnitID.Extractor]) if ext.build_progress == 100]
        ideal_num_on_gas = round(ratio * self.get_gas_slots(units))
        #print("\nDrones on gas:", len(self.drones_on_gas), "Ideal:", ideal_num_on_gas, "\n")

        #Assign Worker to Extractor
        if len(extractors) > 0:
            if len(self.drones_on_gas) < ideal_num_on_gas:                
                for extract in extractors:
                    if extract.assigned_harvesters < extract.ideal_harvesters:
                        if len(untracked_drones) > 0:
                            selected_drone = random.choice(untracked_drones)
                            self.tracked_drones.append(selected_drone)
                        #Use Mineral Drones
                        else:
                            for exp in expansions:
                                if extract in exp.extractor:
                                    selected_drone = random.choice(exp.drones)
                                    exp.drones.remove(selected_drone)
                                    break
                        
                        planned_action = FUNCTIONS.Harvest_Gather_raw_targeted("now", extract.tag, [selected_drone.tag])
                        self.drones_on_gas.append(selected_drone)
                        # print("\nDrone assigned to Extractor", extractors.index(extract), "\n")
                        
                        return planned_action
        
        return planned_action
    
    def assign(self, units, expansion, ratio):
        
        planned_action = None

        all_drones = get_all_owned(units, UNITS[UnitID.Drone])
        expansions = [exp for exp in expansion if exp.ownership == Alliance.Self]
        
        untracked_drones = [d for d in all_drones if d not in self.tracked_drones]

        planned_action = self.assign_gas(units, expansions, untracked_drones, ratio)
        if planned_action is not None:
            return planned_action
        
        if len(untracked_drones) > 0:
            selected_drone = random.choice(untracked_drones)
            for exp in expansions:                        
                #Assign Worker to Mineral Field
                if exp.base is not None and exp.base.build_progress == 100:
                    if exp.get_assigned_harvesters() < exp.get_ideal_harvesters() or \
                       (exp.base.build_progress < 100 and len(exp.drones) < len(exp.minerals)*2):
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
                        # print("\nDrone Assigned to Base", expansions.index(exp), "\n")
                    
                        return planned_action
                

        return planned_action
        

