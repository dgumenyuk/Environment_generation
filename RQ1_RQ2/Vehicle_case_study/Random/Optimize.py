

import config as cf
import os
import json


from Solution import Solution

from road_gen import RoadGen


def evaluate_random(minimum):
    fit_list = []
    generator = RoadGen(
        cf.model["map_size"],
        cf.model["min_len"],
        cf.model["max_len"],
        cf.model["min_angle"],
        cf.model["max_angle"],
    )

    for i in range((500)):
        states = generator.test_case_generate()
        s = Solution()
        s.states = states

        s.get_points()
        s.remove_invalid_cases()
        s.eval_fitness()
        fit_list.append(s.fitness)


    if min(fit_list) < minimum:
        return min(fit_list)
    else:
        return minimum


if __name__ == "__main__":

    res_dict = {}

    m = 0

    for m in range(30):

        fit_list = []

        print("Evaluation ", m)

        res_dict["run" + str(m)] = {}

        eval_num = 0
        minimum = 0

        while eval_num < 100000:  # number of evalutions
            minimum = evaluate_random(minimum)
            eval_num += 500  # popultion size

            print("Eval num ", eval_num, "Minimum", minimum)

            fit_list.append(minimum)

        res_dict["run" + str(m)]["fitness"] = fit_list

        cwd = os.getcwd()
        print(cwd)

        with open("Results_vehicle(3).json", "w") as f:
            json.dump(res_dict, f, indent=4)
