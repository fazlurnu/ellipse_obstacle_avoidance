import numpy as np

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coordinate(self.x - other.x, self.y - other.y)
    
    def rotate(self, theta):
        theta_radians = np.radians(theta)
        c = np.cos(theta_radians)
        s = np.sin(theta_radians)
        
        rot_x = c * self.x - s * self.y
        rot_y = s * self.x + c * self.y
        
        return Coordinate(rot_x, rot_y)