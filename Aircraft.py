from AircraftIcon import *
import numpy as np

class Aircraft:
    def __init__(self, pos, target_pos):
        self.pos = pos
        self.target_pos = target_pos
        
        dx = target_pos.x - pos.x
        dy = target_pos.y - pos.y
        
        self.heading = -np.degrees(np.arctan2(dx, dy))
        
        self.icon = AircraftIcon(self.pos, self.heading)
    
    def get_position(self):
        return self.pos