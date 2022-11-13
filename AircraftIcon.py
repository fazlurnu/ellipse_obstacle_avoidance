from Coordinate import *

from matplotlib.patches import Polygon
import numpy as np

class AircraftIcon:
    def __init__(self, pos, heading):
        self.pos = pos
        self.heading = heading
        
        self.width = 1.0
        self.height = 2.0
        
        self.points = self.get_triangle_points()
        self.points = self.rotate(heading)
        
        # create polygon for triangle icon
        self.polygon = []
        
        for point in self.points:
            self.polygon.append((point.x, point.y))
        
        self.icon = Polygon(self.polygon, color='red', alpha = 0.5)
        
    def get_triangle_points(self):
        left  = Coordinate( (self.pos.x - self.width/2), self.pos.y )
        right = Coordinate( (self.pos.x + self.width/2), self.pos.y )
        front = Coordinate( (self.pos.x), (self.pos.y + self.height) )
        
        return ([left, right, front])
        
        
    def rotate(self, heading):
        points_rotated = []
        
        for point in self.points:
            points_rotated.append((point - self.pos).rotate(heading) + self.pos)
            
        return points_rotated
    
    def distance(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return np.sqrt(dx*dx + dy*dy)