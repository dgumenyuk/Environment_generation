'''
Module for random search Optimization
'''

import config as cf
from schedule_gen import ScheduleGen
import json
from Solution import Solution


def evaluate_random(minimum):
    fit_list = []
    schedules = ScheduleGen(cf.model["temp_min"], cf.model["temp_max"], cf.model["jump"],cf.model["duration_min"], cf.model["duration_max"], cf.model["model_num"])
    for i in range((250)):  # population size
        schedule = schedules.test_case_generate()

        s = Solution()
        s.states = schedule
        s.states = s.check_states()
        s.eval_fitness()
        fit_list.append(s.fitness)

    if min(fit_list) < minimum:
        return min(fit_list)
    else:
        return minimum


if __name__ == "__main__":

    res_dict = {}

    for m in range(30):

        fit_list = []


        print("Evaluation ", m)

        res_dict["run" + str(m)] = {}

        eval_num = 0
        minimum = 0

        while eval_num < 50000:  #  number of evaluations 
            minimum = evaluate_random(minimum)
            eval_num += 250  #  population size

            print("Eval num ", eval_num, "Minimum", minimum)

            fit_list.append(minimum)

        res_dict["run" + str(m)]["fitness"] = fit_list

        with open("Results_dict2.json", "w") as f:
            json.dump(res_dict, f, indent=4)