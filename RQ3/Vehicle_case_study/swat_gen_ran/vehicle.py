#
import random as rm
import numpy as np
import math as m
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt
import json
from swat_gen.road_gen import RoadGen
from scipy.interpolate import splprep, splev, interp1d, splrep
from shapely.geometry import  LineString, Point, GeometryCollection
from scipy.spatial import distance
from numpy.ma import arange
import timeit
import time

class Car:
    """Class that conducts transformations to vectors automatically,
    using the commads "go straight", "turn left", "turn right".
    As a result it produces a set of points corresponding to a road
    """

    def __init__(self, speed, steer_ang, map_size):
        self.speed = speed
        self.map_size = map_size
        self.str_ang = steer_ang


    def interpolate_road(self, road):
        #road.sort()
        #print(road)
        test_road = LineString([(t[0], t[1]) for t in road])

        length = test_road.length

        #print("Length", length)

        old_x_vals = [t[0] for t in road]
        old_y_vals = [t[1] for t in road]

        if len(old_x_vals) == 2:
        # With two points the only option is a straight segment
            k = 1
        elif len(old_x_vals) == 3:
        # With three points we use an arc, using linear interpolation will result in invalid road tests
            k = 2
        else:
        # Otheriwse, use cubic splines
            k = 3
        #print(old_x_vals)
        f2, u = splprep([old_x_vals, old_y_vals], s=0, k=k)
        #print(u)


        step_size = 1 / (length) * 10
        xnew = arange(0, 1 + step_size, step_size) 

        x2, y2 = splev(xnew, f2)

        #self.road_x = old_x_vals
        #self.road_y = old_y_vals
        #print(x2)

        #point = np.array([125, 125])

        #p = Point(125, 125)

        nodes = list(zip(x2,y2))

        #self.image_road(x2, y2, "vehicle2.png")


        #road = LineString([(t[0], t[1]) for t in nodes])
        #r1 = p.distance(road)

        return nodes

        
        #closest_index = distance.cdist([point], nodes).argmin()
        #print(nodes[closest_index])
        #r2 = np.linalg.norm(point - nodes[closest_index])
    def image_road(self, x, y, name):

        fig, ax = plt.subplots(figsize=(12, 12))
        #, nodes[closest_index][0], nodes[closest_index][1], 'go'
        plt.plot( x, y, 'bo')

        top = self.map_size
        bottom = 0
        ax.set_ylim(bottom, top)
        
        ax.set_xlim(bottom, top)

        fig.savefig(".\\" + name)
        plt.close(fig)

    def image_car_path(self, name, fitness):

        fig, ax = plt.subplots(figsize=(12, 12))
        #, nodes[closest_index][0], nodes[closest_index][1], 'go'
        ax.plot( self.tot_x, self.tot_y, 'bo', label="Car path")

        ax.plot(self.road_x, self.road_y, 'yo--', label="Road")

        top = self.map_size
        bottom = 0

        ax.set_title( "Test case fitenss " + fitness , fontsize=17)

        ax.set_ylim(bottom, top)
        
        ax.set_xlim(bottom, top)

        #fig.savefig(".\\images2\\" + name)
        fig.savefig(name + "_" + fitness + ".jpg")
        ax.legend()
        plt.close(fig)




    def get_distance(self, road, x, y):
        p = Point(x, y)
        return p.distance(road)


    def go_straight(self):
        self.x = self.speed*np.cos(m.radians(self.angle)) + self.x
        self.y = self.speed*np.sin(m.radians(self.angle)) + self.y
        self.tot_x.append(self.x)
        self.tot_y.append(self.y)
        return

    def turn_right(self):

            #return
        self.angle = -self.str_ang + self.angle
        self.x = self.speed*np.cos(m.radians(self.angle))/3 + self.x
        self.y = self.speed*np.sin(m.radians(self.angle))/3 + self.y
        self.tot_x.append(self.x)
        self.tot_y.append(self.y)
        return

    def turn_left(self):

            #return
        self.angle = self.str_ang + self.angle
        self.x = self.speed*np.cos(m.radians(self.angle))/3 + self.x
        self.y = self.speed*np.sin(m.radians(self.angle))/3 + self.y

        self.tot_x.append(self.x)
        self.tot_y.append(self.y)
        
        return

    '''
    def get_angle(self, init_pos):
        """returns the sector of initial position"""

        return -90

        if round(init_pos[1], 1) == 10:
            return 90
        elif round(init_pos[0], 1) == 10:
            return 0
        elif round(init_pos[1], 1) == self.map_size - 10:
            return -90
        elif round(init_pos[0], 1) == self.map_size - 10:
            return 180
        else:
            return 0
    '''

    def get_angle(self, node_a, node_b):
        vector = np.array(node_b) - np.array(node_a)
        #print("vec", vector)
        cos = vector[0]/(np.linalg.norm(vector))

        angle = m.degrees(m.acos(cos))

        #print("a", node_a)
        #print("b", node_b)


        if node_a[1] > node_b[1]:
            #print("angle", -angle)
            return -angle
        else:
            #print("angle", angle)
            return angle



        '''
        if in_state == "straight":
            return 90
        elif in_state == "right":
            return 90 - in_value
        else:
            return 90 + in_value
        '''





    def execute_road(self, nodes):

        self.x = 0
        self.y = 0 

        old_x_vals = [t[0] for t in nodes]
        old_y_vals = [t[1] for t in nodes]

        self.road_x = old_x_vals
        self.road_y = old_y_vals

        self.angle = 0 
        self.tot_x = []
        self.tot_y = []
        self.tot_dist = []
        self.final_dist = []


        road = LineString([(t[0], t[1]) for t in nodes])
        if road.is_simple == False or is_too_sharp(_interpolate(nodes))==True:
            fitness = 0
        else:
            init_pos = nodes[0]
            #print("Init pos", init_pos)
            self.x = init_pos[0]
            self.y = init_pos[1]

            #self.angle = self.get_angle(init_pos)

            self.angle = self.get_angle(nodes[0], nodes[1])

            #print("POS x", round(init_pos[0],1), "POS Y", round(init_pos[1], 1))
            #print("ANGLE", self.angle)
            #self.angle = self.get_angle(init_pos)

            self.tot_x.append(self.x)
            self.tot_y.append(self.y)

            length = np.linalg.norm(np.array([nodes[0][0], nodes[0][1]]) - np.array([nodes[-1][0], nodes[-1][1]]))

            
            i = 0
            current_length = 0
            norm = np.linalg.norm(np.array([self.x, self.y]) - np.array([init_pos[0], init_pos[1]])) 
            #while ((np.linalg.norm(np.array([self.x, self.y]) - np.array([init_pos[0], init_pos[1]]) )) < length):
            while (current_length < road.length) and i < 1000:
            #while ((current_length < road.length) or (norm < length)) and (i < 1000):
            #while i < 10000:
                distance = self.get_distance(road, self.x, self.y)
                self.tot_dist.append(distance)
                if distance > 2:
                    self.final_dist.append(distance)
                #print(self.x)
                #print(self.y)
                if distance <= 1:
                    self.go_straight()
                else:
                    angle = -self.str_ang + self.angle
                    x = self.speed*np.cos(m.radians(angle)) + self.x
                    y = self.speed*np.sin(m.radians(angle)) + self.y

                    distance_right = self.get_distance(road, x, y)

                    angle = self.str_ang + self.angle
                    x = self.speed*np.cos(m.radians(angle)) + self.x
                    y = self.speed*np.sin(m.radians(angle)) + self.y

                    distance_left = self.get_distance(road, x, y)


                    #print("Distance2", distance2)
                    if distance_right < distance_left:
                        self.turn_right()
                    else:
                        self.turn_left()

                current_road = LineString([(t[0], t[1]) for t in zip(self.tot_x, self.tot_y)])
                current_length = current_road.length
                norm = np.linalg.norm(np.array([self.x, self.y]) - np.array([init_pos[0], init_pos[1]])) 
                        
                i += 1
                #print("i", i)
            
            #fitness = sum(self.tot_dist)/len(self.tot_dist)*(-1)
            fitness = max(self.tot_dist)*(-1)
            #fitness = len(self.final_dist)*(-1)




        return fitness, [self.tot_x, self.tot_y]



   # def get_distance(self, road_point):



def find_circle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).
    """
    temp = p2[0] * p2[0] + p2[1] * p2[1]
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])

    if abs(det) < 1.0e-6:
        return np.inf

    # Center of circle
    cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det

    radius = np.sqrt((cx - p1[0])**2 + (cy - p1[1])**2)
    #print(radius)
    return radius


def min_radius(x, w=5):
    mr = np.inf
    nodes = x
    for i in range(len(nodes) - w):
        p1 = nodes[i]
        p2 = nodes[i + int((w-1)/2)]
        p3 = nodes[i + (w-1)]
        radius = find_circle(p1, p2, p3)
        if radius < mr:
            mr = radius
    if mr == np.inf:
        mr = 0

    return mr * 3.280839895#, mincurv


def _interpolate(the_test):
    """
        Interpolate the road points using cubic splines and ensure we handle 4F tuples for compatibility
    """
    rounding_precision = 3
    interpolation_distance = 1
    smoothness = 0
    min_num_nodes = 20

    old_x_vals = [t[0] for t in the_test]
    old_y_vals = [t[1] for t in the_test]

    # This is an approximation based on whatever input is given
    test_road_lenght = LineString([(t[0], t[1]) for t in the_test]).length
    num_nodes = int(test_road_lenght / interpolation_distance)
    if num_nodes < min_num_nodes:
        num_nodes = min_num_nodes

    assert len(old_x_vals) >= 2, "You need at leas two road points to define a road"
    assert len(old_y_vals) >= 2, "You need at leas two road points to define a road"

    if len(old_x_vals) == 2:
        # With two points the only option is a straight segment
        k = 1
    elif len(old_x_vals) == 3:
        # With three points we use an arc, using linear interpolation will result in invalid road tests
        k = 2
    else:
        # Otheriwse, use cubic splines
        k = 3

    pos_tck, pos_u = splprep([old_x_vals, old_y_vals], s= smoothness, k=k)

    step_size = 1 / num_nodes
    unew = arange(0, 1 + step_size, step_size)

    new_x_vals, new_y_vals = splev(unew, pos_tck)

    # Return the 4-tuple with default z and defatul road width
    return list(zip([round(v, rounding_precision) for v in new_x_vals],
                    [round(v, rounding_precision) for v in new_y_vals],
                    [-28.0 for v in new_x_vals],
                    [8.0 for v in new_x_vals]))


def is_too_sharp(the_test, TSHD_RADIUS=47):
    if TSHD_RADIUS > min_radius(the_test) > 0.0:
        check = True
        #print("TOO SHARP")
    else:
        check = False
    #print(check)
    return check



if __name__ == "__main__":
    car = Car(3, 10, 250)
    with open("points2.json") as file:
        points = json.load(file)

    for tc in points:
        case = tc
        road = points[case]
        #road = car.interpolate_road(points[case])
        #car.execute_road(points[case], case)
        car.execute_road(car.interpolate_road(road), case)
    #road.road_points
    


