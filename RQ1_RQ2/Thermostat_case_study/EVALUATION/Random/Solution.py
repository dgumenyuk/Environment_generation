
from IdealTherm import Thermostat
from FitFunction import FitFunction
from ImageBuilder import ImageBuilder
import config as cf
import os
class Solution:
    def __init__(self):

        self.states = {}
        self.therm = Thermostat(cf.model["sample_rate"], cf.model["threshold"])
        self.fit = FitFunction()
        self.fitness = 0
        self.max_duration = cf.model["tot_dur"]
        self.novelty = 0
        #self.crossover_point = 2

    def eval_fitness(self):
        #print(self.states)
        self.therm.read_test_case(self.states)
        self.fitness = self.fit.calculate_rms(
            self.therm.ideal_temp_list, self.therm.system_temp_list
        ) * (-1)

        val_list = []
        #print(self.states)
        for state in (self.states):
            #print(state)
            val_list.append(self.states[state]['temp'])

        if (max(val_list) - min(val_list)) > cf.model["jump"]:
            self.fitness = 0

        #print("FITNESS", self.fitness)



    def check_states(self):
        total_dur = 0
        new_states = {}
        for state in (self.states):
            total_dur += self.states[state]["duration"]
            if total_dur <= self.max_duration:
                new_states[state] = self.states[state]
            else:
                return new_states

        return new_states




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
            if old[tc]["temp"] == new[tc]["temp"]:
                value_list = [old[tc]["duration"], new[tc]["duration"]]
                ratio = max(value_list)/min(value_list)
                if ratio >= 2:
                    novelty += 0.5
            else:
                novelty += 1
        #print("NOVELTY", novelty)
        return -novelty


    def build_graph(self, generation, tc):
        save_path = os.path.join(cf.files["tc_img"], "generation_" + str(generation))
        imager = ImageBuilder(save_path, cf.model["tot_dur"], cf.model["sample_rate"]).build_image(
            3,
            tc,
            self.fitness,
            id_tmp=self.therm.ideal_temp_list,
            ss_tmp=self.therm.system_temp_list,
        )

    # setter and getter via  @ properties

