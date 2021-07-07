
from vehicle import Car
#from FitFunction import FitFunction
#from ImageBuilder import ImageBuilder
import config as cf
from car_road import Map
import json
from code_pipeline.beamng_executor import BeamngExecutor
from code_pipeline.tests_generation import RoadTestFactory
from code_pipeline.validation import TestValidator
class Solution:
    def __init__(self):

        self.road_points = []
        self.states = {}
        self.car = Car(cf.model["speed"], cf.model["steer_ang"], cf.model["map_size"])
        self.road_builder = Map(cf.model["map_size"])
        #self.init_pos = []
        #self.fit = FitFunction()
        self.fitness = 0
        self.car_path = []
        self.novelty = 0
        self.intp_points = []
        self.too_sharp = 0
        self.just_fitness = 0
        self.oob = 0
        #self.crossover_point = 2

    def eval_fitness2(self):

        #self.states, self.road_points = self.road_builder.remove_invalid_cases(self.road_points, self.states)
        #print("STATES", self.states)
        #self.road_points = self.road_builder.get_points_from_states(self.states)
        #print("POINTS", self.road_points)
        
        #road = self.car.interpolate_road(self.road_points)
        road = self.road_points
        if not road:
            self.get_points()
            self.remove_invalid_cases()
            road = self.road_points
            print("Points was empty")

        #if len(self.road_points) <= 3:
           # self.fitness = 0
        #else:

        #in_state = self.states["st0"]["state"]
        #in_value = self.states["st0"]["value"]



        if len(self.road_points) < 2:
            self.fitness = 0
        else:
            self.intp_points = self.car.interpolate_road(road)
            self.fitness, self.car_path = self.car.execute_road(self.intp_points)
            #self.fitness, self.car_path = self.car.execute_road(road)
        self.just_fitness = self.fitness

        if self.fitness < -25:
            self.fitness = 0


        return 

        #print("FITNESS", self.fitness)

    def eval_fitness(self):

        the_executor = BeamngExecutor(cf.model["map_size"])
        test_validator = TestValidator(cf.model["map_size"])

        the_test = RoadTestFactory.create_road_test(self.road_points)
        self.intp_points = self.car.interpolate_road(self.road_points)

        is_valid, validation_msg = test_validator.validate_test(the_test)

        print(is_valid)

        #the_test = RoadTestFactory.create_road_test(road.road_points)
        
        # Try to execute the test
        #test_outcome, description, execution_data = the_executor._execute(the_test)

        #test_outcome, description, execution_data
        if (is_valid== True):
            fit, dist = the_executor._eval_tc(the_test)
            dist *= -1

            print("oob", fit)
            print("dist", dist)
        else:
            fit = 0
            dist = 0

        self.fitness = dist
        self.oob = fit

        return -dist

        '''
        dist_list = []
        for i in execution_data:
            dist_list.append(i[15])
        print("executed",max(dist_list) )

        self.fitness = max(dist_list)*(-1)


        return max(dist_list)*(-1)
        '''


    def get_points(self):
        self.road_points = self.road_builder.get_points_from_states(self.states)

    def remove_invalid_cases(self):
        self.states, self.road_points = self.road_builder.remove_invalid_cases(self.road_points, self.states)
        #self.road_points = self.car.interpolate_road(self.road_points)





    def calc_novelty(self, old, new):
        novelty = 0
        #print("OLD", old)
        #print("NEW", new)
        difference = abs(len(new) - len(old))/2
        novelty += difference
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


    @property
    def states(self):
        return self._states

    @states.setter
    def states(self, value):
        self._states = value

    @property
    def n_states(self):
        return len(self._states)

    @property
    def fitness(self):
        return self._fitness

    @fitness.setter
    def fitness(self, value: float):
        self._fitness = value


