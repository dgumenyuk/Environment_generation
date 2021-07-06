

import config as cf
from robot_map import Map
import matplotlib.pyplot as plt
from a_star import AStarPlanner
from shapely.geometry import  LineString
class Solution:
    def __init__(self):

        self.map_points = []
        self.states = {}
        self.fitness = 0
        self.novelty = 0
        self.sx = 1.0  # [m]
        self.sy = 1.0  # [m]
        self.gx = cf.model["map_size"] - 2  # [m]
        self.gy = cf.model["map_size"] - 2  # [m]
        self.map_builder = Map(cf.model["map_size"])

        self.grid_size = 1  # [m]
        self.robot_radius = 0.5  # [m]

    def eval_fitness(self):

        ox = [t[0] for t in self.map_points]
        oy = [t[1] for t in self.map_points]

        a_star = AStarPlanner(ox, oy, self.grid_size, self.robot_radius)  # noqa: E501

        rx, ry, time = a_star.planning(self.sx, self.sy, self.gx, self.gy)
        self.robot_path_x = rx
        self.robot_path_y = ry
        path = zip(rx, ry)

        #print(path)

        if len(rx) > 2:
        
            test_road = LineString([(t[0], t[1]) for t in path])
            self.fitness = -test_road.length
        else:
            self.fitness = 0


        #self.fitness = -time
        #self.fitness = -test_road.length

        #print(self.fitness)

        return self.fitness
    def calc_novelty(self, old, new):
        novelty = 0
        #print("OLD", old)
        #print("NEW", new)

        if len(new) <= len(old):
            shorter = new
        else:
            shorter = old
        for tc in shorter:
            if old[tc]["state"] == new[tc]["state"]:
                value_list = [old[tc]["value"], new[tc]["value"]]
                ratio = max(value_list)/min(value_list)
                if ratio >= 2:
                    novelty += 0.5
            else:
                novelty += 1
        #print("NOVELTY", novelty)
        return -novelty
        

    def get_points(self):
        self.map_points = self.map_builder.get_points_from_states(self.states)

    # setter and getter via  @ properties
    def build_tc(self):

        fig, ax = plt.subplots(figsize=(12, 12))
        #, nodes[closest_index][0], nodes[closest_index][1], 'go'
        road_x = []
        road_y = []
        for p in self.road_points:
            road_x.append(p[0])
            road_y.append(p[1])

        ax.plot( self.car_path[0], self.car_path[1], 'bo', label="Car path")

        ax.plot(road_x, road_y, 'yo--', label="Road")

        top = cf.model["map_size"]
        bottom = 0

        ax.set_title( "Test case fitenss " + fitness  , fontsize=17)

        ax.set_ylim(bottom, top)
        
        ax.set_xlim(bottom, top)

        fig.savefig(cf.files["tc_img"] + fitness + ".jpg")
        ax.legend()
        plt.close(fig)


    @property
    def states(self):
        return self._states

    @states.setter
    def states(self, value):
        self._states = value

    @property
    def n_states(self):
        return len(self.states)

    @property
    def fitness(self):
        return self._fitness

    @fitness.setter
    def fitness(self, value: float):
        self._fitness = value
