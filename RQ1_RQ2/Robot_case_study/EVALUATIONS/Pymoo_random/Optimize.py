'''
Module for random search based Optimization
'''


import config as cf
import json
from Solution import Solution
from room_gen import MapGen


def evaluate_random(minimum):
    fit_list = []
    generator = MapGen(cf.model["map_size"], cf.model["min_len"], cf.model["max_len"], cf.model["len_step"], cf.model["pos_step"])
    for i in range((10)):
        map_points, states = generator.test_case_generate()
        s = Solution()
        s.map_points = map_points
        s.states = states
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

        while eval_num < 100+10*400:
            minimum = evaluate_random(minimum)
            eval_num += 10

            print("Eval num ", eval_num, "Minimum", minimum)

            fit_list.append(minimum)

        res_dict["run" + str(m)]["fitness"] = fit_list

        with open("Results_dict2.json", "w") as f:
            json.dump(res_dict, f, indent=4)
