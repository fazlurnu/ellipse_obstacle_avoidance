import sys
import matplotlib

import numpy as np

from matplotlib.patches import Ellipse
from matplotlib.patches import Polygon

from matplotlib.artist import Artist

from numpy.linalg import inv

from Coordinate import *
from Aircraft import *

matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# reference
# https://www.xarg.org/book/computer-graphics/line-segment-ellipse-intersection/

# transform A and B to wrt C
def get_ellipse_line_intersection(A, B, C, rx, ry, ellipse_heading):
    A = (A - C).rotate(-ellipse_heading)
    B = (B - C).rotate(-ellipse_heading)

    dx = B.x - A.x
    dy = B.y - A.y

    a = (rx*rx * dy*dy + ry*ry * dx*dx)
    b = (2*rx*rx*A.y*dy + 2*ry*ry*A.x*dx)
    c = rx*rx*A.y*A.y + ry*ry*A.x*A.x - rx*rx*ry*ry

    D = b*b - 4*a*c

    ret = []
    
    if(D > 0):
        t1 = (-b + np.sqrt(D))/(2*a)
        t2 = (-b - np.sqrt(D))/(2*a)

        if(0<= t1 <= 1):
            IP_1 = Coordinate(A.x+(B.x-A.x)*t1, A.y+(B.y-A.y)*t1).rotate(ellipse_heading) + C
            ret.append(IP_1)
        if((0<= t2 <= 1) and (t1 - t2 > 0)):
            IP_2 = Coordinate(A.x+(B.x-A.x)*t2, A.y+(B.y-A.y)*t2).rotate(ellipse_heading) + C
            ret.append(IP_2)
            
    return ret

def normal_vector(g):
    dx = g[0].item()
    dy = g[1].item()
    
    length = np.sqrt(dx*dx + dy*dy)
    
    g = g/length
    
    return g

def avoidance_point(a, b, ellipse_center, ellipse_heading, point1, point2):
    rx = a/2
    ry = b/2
    c = rx*rx
    
    ellipse_heading_rad = np.radians(ellipse_heading)
    
    R = np.matrix([[np.cos(ellipse_heading_rad), -np.sin(ellipse_heading_rad)],
                   [np.sin(ellipse_heading_rad),  np.cos(ellipse_heading_rad)]])
    
    Ao =np.matrix([[1/(rx*rx), 0],
                   [0, 1/(ry*ry)]])
    
    A = R.transpose()*Ao*R
    A11 = A.item((0, 0))
    A = A/A11
    c = (1/A11)
    
    dx = point2.x - point1.x
    dy = point2.y - point1.y
    
    if(dy/dx > 0):
        g = np.array([[-dy], [dx]])
        g = normal_vector(g)
    else:
        g = np.array([[dy], [-dx]])
        g = normal_vector(g)
        
    CP = -inv(np.sqrt((g.transpose()*inv(A)*g).item()/c)*A)*g
    x_cp = CP[0].item() + ellipse_center.x
    y_cp = CP[1].item() + ellipse_center.y

#     print(g.item(0)*x_cp + g.item(1)*y_cp)
    
    return Coordinate(x_cp, y_cp)

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class SliderLabel():
    def __init__(self, MainWindow, min, max, step, name = "Slider"):
        self.layout = QtWidgets.QHBoxLayout()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(min,max)
        self.slider.setSingleStep(step)
        self.slider.valueChanged.connect(MainWindow.updateLabel)

        label_name = QtWidgets.QLabel(name)
        self.label_value = QtWidgets.QLabel(str(self.slider.value()))
        
        self.layout.addWidget(label_name)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.slider)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.label_value)

    def setText(self, text):
        self.label_value.setText(text)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs) 
        # variables
        self.ellipse_heading = 0.0
        self.rx = 4.0
        self.ry = 3.0
        self.ex = 0.0
        self.ey = 12.0
        self.target_x = 0.0
        self.target_y = 19.0

        #sliders
        self.slider_rx = SliderLabel(self, 4, 8, 1, "Ellipse\nRad X")
        self.slider_ry = SliderLabel(self, 3, 6, 1, "Ellipse\nRad Y")
        self.slider_ex = SliderLabel(self, -5, 5, 1, "Ellipse\nCtr X")
        self.slider_ey = SliderLabel(self, 12, 15, 1, "Ellipse\nCtr Y")
        
        self.slider_heading = SliderLabel(self, -60, 60, 3, "Ellipse\nHeading")
        self.slider_target_x = SliderLabel(self, -10, 10, 1, "WP X")
        self.slider_target_y = SliderLabel(self, 23, 25, 1, "WP Y")

        self.all_sliders = [self.slider_rx, self.slider_ry, self.slider_ex, self.slider_ey,
                            self.slider_heading, self.slider_target_x, self.slider_target_y]
                              
        self.sc = MplCanvas(self, width=4, height=4, dpi=100)
        self.sc.axes.set_xlim(-12.7, 12.7)
        self.sc.axes.set_ylim(-0.2, 25.2)

        self.update_plot()

        layout = QtWidgets.QVBoxLayout()
        layout_control_panel = QtWidgets.QHBoxLayout()
        layout_cp_left = QtWidgets.QVBoxLayout()
        layout_cp_right = QtWidgets.QVBoxLayout()
        
        layout_cp_left.addLayout(self.slider_rx.layout)
        layout_cp_left.addLayout(self.slider_ry.layout)
        layout_cp_left.addLayout(self.slider_heading.layout)

        layout_cp_right.addLayout(self.slider_ex.layout)
        layout_cp_right.addLayout(self.slider_ey.layout)
        layout_cp_right.addLayout(self.slider_target_x.layout)
        layout_cp_right.addLayout(self.slider_target_y.layout)

        layout_control_panel.addLayout(layout_cp_left)
        layout_control_panel.addLayout(layout_cp_right)

        layout.addWidget(self.sc)
        layout.addLayout(layout_control_panel)

        # Create a placeholder widget to hold our plot and control panel
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def updateLabel(self):
        for idx in range(len(self.all_sliders)):
            slider = self.all_sliders[idx]
            slider.setText(str(slider.slider.value()))
            
            if(idx == 0):
                self.rx = float(slider.slider.value())
            if(idx == 1):
                self.ry = float(slider.slider.value())
            if(idx == 2):
                self.ex = float(slider.slider.value())
            if(idx == 3):
                self.ey = float(slider.slider.value())
            if(idx == 4):
                self.ellipse_heading = float(slider.slider.value())
            if(idx == 5):
                self.target_x = float(slider.slider.value())
            if(idx == 6):
                self.target_y = float(slider.slider.value())

        self.update_plot()
        
    def draw_ellipse(self, ellipse_center, rx, ry, heading):
        ellipse = Ellipse((ellipse_center.x, ellipse_center.y),
                        rx*2, ry*2, angle = heading,
                        facecolor='None', edgecolor = 'k')
        ellipse2 = Ellipse((ellipse_center.x, ellipse_center.y),
                        rx*2-2.4, ry*2-2.4, angle = heading,
                        facecolor='None', edgecolor = 'k', linestyle = '--')

        self.sc.axes.add_artist(ellipse)
        self.sc.axes.add_artist(ellipse2)

    def draw_aircraft(self, aircraft):
        dx = aircraft.target_pos.x - aircraft.pos.x
        dy = aircraft.target_pos.y - aircraft.pos.y
        length = np.sqrt(dx*dx + dy*dy)/2

        if (dy/dx > 0):
            self.sc.axes.arrow(aircraft.icon.polygon[2][0], aircraft.icon.polygon[2][1]*0.8,
                        dy/length, -dx/length,
                        shape='full', length_includes_head=True, head_width=.1)
            self.sc.axes.text((aircraft.icon.polygon[2][0] + dy/(length*2)),
                                (aircraft.icon.polygon[2][1] - dx/(length*2)),
                                'g', weight = 'bold')
            
        else:
            self.sc.axes.arrow(aircraft.icon.polygon[2][0], aircraft.icon.polygon[2][1]*0.8,
                        -dy/length, dx/length,
                        shape='full', length_includes_head=True, head_width=.1)
            self.sc.axes.text((aircraft.icon.polygon[2][0] - dy/(length*2)),
                                (aircraft.icon.polygon[2][1] + dx/(length*2)),
                                'g', weight = 'bold')
            

        self.sc.axes.plot(aircraft.target_pos.x, aircraft.target_pos.y, 'ko')
        self.sc.axes.add_patch(aircraft.icon.icon)

        self.sc.axes.plot([aircraft.pos.x, aircraft.target_pos.x],
                [aircraft.pos.y, aircraft.target_pos.y],
                linestyle = '--', alpha = 0.5, color = 'k')

    def draw_points(self, aircraft, ellipse_center, rx, ry, heading):
        dx = aircraft.target_pos.x - aircraft.pos.x
        dy = aircraft.target_pos.y - aircraft.pos.y
        length = np.sqrt(dx*dx + dy*dy)/2 

        IPs = get_ellipse_line_intersection(aircraft.pos, aircraft.target_pos,
                                        ellipse_center, rx, ry, heading)

        if(len(IPs) > 0):
            AP = avoidance_point(rx*2, ry*2, ellipse_center, -heading, aircraft.pos, aircraft.target_pos)
            self.sc.axes.plot(AP.x, AP.y, 'bx')

            if (dx == 0 or dy/dx > 0):
                self.sc.axes.arrow(AP.x, AP.y,
                            dy/length, -dx/length,
                            shape='full', length_includes_head=True, head_width=.1)
            else:
                self.sc.axes.arrow(AP.x, AP.y,
                            -dy/length, dx/length,
                            shape='full', length_includes_head=True, head_width=.1)

            self.sc.axes.plot([aircraft.pos.x, AP.x],
                    [aircraft.pos.y, AP.y],
                    color = 'k', linewidth = 0.5)

        for IP in IPs:
            self.sc.axes.plot(IP.x, IP.y, 'rx')

    def update_plot(self):
        self.ellipse_center = Coordinate(self.ex, self.ey)
        self.aircraft = Aircraft(Coordinate(0.1, 0.0),
                            Coordinate(self.target_x, self.target_y))
                            
        self.sc.axes.cla()  # Clear the canvas.
        # self.sc.axes.axis('equal')
        self.sc.axes.set_aspect('equal', 'box')
        self.sc.axes.set_xlim(-12.7, 12.7)
        self.sc.axes.set_ylim(-0.2, 25.2)
        self.sc.axes.set_title("Ellipse-based Obstacle Avoidance")
        self.sc.axes.set_xlabel("X-coordinate")
        self.sc.axes.set_ylabel("Y-coordinate")

        self.draw_ellipse(self.ellipse_center, self.rx, self.ry, self.ellipse_heading)
        self.draw_aircraft(self.aircraft)
        self.draw_points(self.aircraft, self.ellipse_center, self.rx, self.ry, self.ellipse_heading)

        # Trigger the canvas to update and redraw.
        self.sc.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()