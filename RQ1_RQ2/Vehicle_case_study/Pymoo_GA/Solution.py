'''
Solution object containig the data about the generated road
'''

from vehicle import Car
import config as cf
from car_road import Map

class Solution:
    def __init__(self):

        self.road_points = []
        self.states = {}
        self.car = Car(cf.model["speed"], cf.model["steer_ang"], cf.model["map_size"])
        self.road_builder = Map(cf.model["map_size"])

        self.fitness = 0
        self.car_path = []
        self.novelty = 0
        self.intp_points = []


    def eval_fitness(self):

        road = self.road_points
        if not road:
            self.get_points()
            self.remove_invalid_cases()
            road = self.road_points
            print("Points was empty")

        self.just_fitness = self.fitness

        if len(self.road_points) < 2:
            self.fitness = 0
        else:
            self.intp_points = self.car.interpolate_road(road)
            self.fitness, self.car_path = self.car.execute_road(self.intp_points)

        return

    def get_points(self):
        self.road_points = self.road_builder.get_points_from_states(self.states)

    def remove_invalid_cases(self):
        self.states, self.road_points = self.road_builder.remove_invalid_cases(
            self.road_points, self.states
        )

    def calc_novelty(self, old, new):
        novelty = 0
        difference = abs(len(new) - len(old)) / 2
        novelty += difference
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
