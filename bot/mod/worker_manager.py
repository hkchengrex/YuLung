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
        self.bases = []
        self.drones = []
        self.drones_in_bases = []
        
    def track(self, units):
        all_bases = get_all_owned(units, ZERG_BASES)
        all_drones = get_all_owned(units, UNITS[UnitID.Drone])
        
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
        
        dead_drones = [d for d in self.drones if d not in all_drones]
        for dead_d in dead_drones:
            # print("\nRemoving Dead Drones\n")
            for drones_base_i in self.drones_in_bases:
                if dead_d in drones_base_i:
                    drones_base_i.remove(dead_d)
            self.drones.remove(dead_d)

        # for i in range(len(self.bases)):
        #     print("Drones in Base", i, ":", len(self.drones_in_bases[i]))
        # print("Total Drones", len(self.drones))
        
    def assign(self, units):
        
        planned_action = None

        all_drones = get_all_owned(units, UNITS[UnitID.Drone])
        max_worker = 16
        
        untracked_drones = [d for d in all_drones if d not in self.drones]
        
        if len(untracked_drones) > 0:
            for drones_base_i in self.drones_in_bases:
                if len(drones_base_i) < max_worker:                    
                    selected_drone = random.choice(untracked_drones)
                    base_index = self.drones_in_bases.index(drones_base_i)
                    base = self.bases[base_index]
                    base_pos = point.Point(base.posx, base.posy)
                    
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
                    
                    self.drones_in_bases[base_index].append(selected_drone)
                    self.drones.append(selected_drone)
                    print("\nDrone Assigned to Base", base_index, "\n")
                    
                    return planned_action

        return planned_action
        

