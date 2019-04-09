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

        """
        drones stores all tracked drones
        drones_in_bases stores list of drones in each base
        """
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
        """
        if len(self.bases) == 0 and len(self.drones) == 0:
            for base in all_bases:
                self.bases.append(base)
                
            self.drones_in_bases.append([])
            for drone in all_drones:
                self.drones.append(drone)
                self.drones_in_bases[0].append(drone)        
            
        untrack_bases = [b for b in all_bases if b not in self.bases and b.build_progress > 0.95]
        for untrack_b in untrack_bases:
            self.bases.append(untrack_b)
            self.drones_in_bases.append([])
                
        dead_bases = [b for b in self.bases if b not in all_bases]
        for dead_b in dead_bases:
            dead_b_index = self.bases.index(dead_b)
            for drone in self.drones_in_bases[dead_b_index]:
                self.drones.remove(drone)
            self.drones_in_bases.pop(dead_b_index)
            self.bases.remove(dead_b)
        """
        
        dead_drones = [d for d in self.tracked_drones if d not in all_drones]
        for dead_d in dead_drones:
            print("\nRemoving Dead Drones\n")
            for exp in expansions:
                if dead_d in exp.drones:
                    exp.drones.remove(dead_d)
            self.tracked_drones.remove(dead_d)

        for i in range(len(expansions)):
            print("Drones in Base", i, ":", len(expansions[i].drones))
        print("Total Drones", len(self.tracked_drones))
        
    def assign(self, units, expansion):
        
        planned_action = None

        all_drones = get_all_owned(units, UNITS[UnitID.Drone])
        expansions = [exp for exp in expansion if exp.ownership == Alliance.Self]
        
        untracked_drones = [d for d in all_drones if d not in self.tracked_drones]
        
        if len(untracked_drones) > 0:
            
            for exp in expansions:
                if exp.get_assigned_harvesters() < exp.get_ideal_harvesters() or (exp.base.build_progress < 100 and len(exp.drones) < len(exp.minerals)*2):
                    selected_drone = random.choice(untracked_drones)

                    mineral = random.choice(exp.minerals)
                    mineral_pos = point.Point(mineral.posx, mineral.posy)

                    #Temporal Fix
                    base_pos = point.Point(exp.base.posx, exp.base.posy)
                    minerals = get_all(units, UNITS[UnitID.MineralField])
                    m_pos = []
                    for m in minerals:
                        m_pos.append(point.Point(m.posx, m.posy))
                    mini = m_pos[0]
                    for pos in m_pos:
                        if base_pos.dist(pos) < base_pos.dist(mini):
                            mini = pos
                    close_m = minerals[m_pos.index(mini)]

                    planned_action = FUNCTIONS.Harvest_Gather_raw_targeted("now", close_m.tag, [selected_drone.tag])
                    #planned_action = FUNCTIONS.Harvest_Gather_raw_targeted("now", mineral.tag, [selected_drone.tag])
                    #planned_action = FUNCTIONS.Move_raw_pos("now", mineral_pos, [selected_drone.tag])
                    
                    exp.drones.append(selected_drone)
                    self.tracked_drones.append(selected_drone)
                    print("")
                    print("\nDrone Assigned to Base", expansions.index(exp), "\n")
                    print(exp.get_assigned_harvesters())
                    print(exp.get_ideal_harvesters())                    
                    print("")
                    
                    return planned_action

        return planned_action
        

