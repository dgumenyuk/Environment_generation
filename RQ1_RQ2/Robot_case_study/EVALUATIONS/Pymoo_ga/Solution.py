'''
Module that keep the data about each solution
'''


import config as cf
from robot_map import Map
from a_star import AStarPlanner
from shapely.geometry import LineString


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

        if len(rx) > 2:

            test_road = LineString([(t[0], t[1]) for t in path])
            self.fitness = -test_road.length
        else:
            self.fitness = 0


        return self.fitness

    def calc_novelty(self, old, new):
        novelty = 0

        if len(new) <= len(old):
            shorter = new
        else:
            shorter = old
        for tc in shorter:
            if old[tc]["state"] == new[tc]["state"]:
                value_list = [old[tc]["value"], new[tc]["value"]]
                ratio = max(value_list) / min(value_list)
                if ratio >= 2:
                    novelty += 0.5
            else:
                novelty += 1
        return -novelty

    def get_points(self):
        self.map_points = self.map_builder.get_points_from_states(self.states)


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
