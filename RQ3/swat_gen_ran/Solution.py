
from swat_gen.vehicle import Car
#from FitFunction import FitFunction
#from ImageBuilder import ImageBuilder
import swat_gen.config as cf
from swat_gen.car_road import Map
import json
from code_pipeline.beamng_executor import BeamngExecutor
from code_pipeline.tests_generation import RoadTestFactory

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
        #self.crossover_point = 2

    def eval_fitness(self):

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

            if self.fitness <= -20:
                self.fitness = 0


        return 

        #print("FITNESS", self.fitness)

    def car_model_fit(self):

        the_executor = BeamngExecutor(cf.model["map_size"])

        #the_test = RoadTestFactory.create_road_test(road.road_points)
        the_test = RoadTestFactory.create_road_test(self.road_points)
        # Try to execute the test
        #test_outcome, description, execution_data = the_executor._execute(the_test)

        fit = the_executor._eval_tc(the_test)

        return fit


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
