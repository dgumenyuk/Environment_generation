import config as cf
import numpy as np
from pymoo.optimize import minimize

from MyProblem import MyProblem
from MyTcMutation import MyTcMutation
from MyTcCrossOver import MyTcCrossover
from MyDuplicates import MyDuplicateElimination
from pymoo.util.termination.f_tol import MultiObjectiveSpaceToleranceTermination
from MyTcSampling import MyTcSampling
import matplotlib.pyplot as plt
import os
import shutil
from shutil import make_archive
from zipfile import ZipFile
import json
import time
from pymoo.algorithms.nsga2 import NSGA2
from pymoo.visualization.scatter import Scatter
from Solution import Solution

from room_gen import MapGen


def evaluate_random(minimum):
    fit_list = []
    solution_dict = {}
    generator = MapGen(
        cf.model["map_size"],
        cf.model["min_len"],
        cf.model["max_len"],
        cf.model["len_step"],
        cf.model["pos_step"],
    )

    map_points, states = generator.test_case_generate()
    s = Solution()
    s.map_points = map_points
    s.states = states
    s.eval_fitness()
    solution_dict[s.fitness] = s
    # print(s.fitness)
    # result = {"list": fit_list}

    if s.fitness < minimum.fitness:
        return s
    else:
        return minimum


def build_scenario(road_points, path, run):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_frame_on(False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    road_x = []
    road_y = []
    for p in road_points:
        road_x.append(p[0])
        road_y.append(p[1])

    ax.scatter(road_x, road_y, s=150, marker="s", color="k")

    top = cf.model["map_size"] + 1
    bottom = -1

    fig.savefig(
        os.path.join(path, "map" + str(i) + ".png"), bbox_inches="tight", pad_inches=0
    )

    plt.close(fig)


if __name__ == "__main__":

    path_folder = ".\\results"
    if not (os.path.exists(path_folder)):
        os.mkdir(path_folder)
    it = 0
    for it in range(20, 30):
        res_dict = {}

        time_list = []
        m = 0

        base_path = ".\\results" + str(it) + "\\"
        base_path = os.path.join(base_path)
        if not (os.path.exists(base_path)):
            os.mkdir(base_path)

        alg_time = 0
        while alg_time < 7200:

            print("Evaluation ", m)

            res_dict["run" + str(m)] = {}

            eval_num = 0
            minimum = Solution()
            minimum.fitness = 0

            all_routes = {}
            all_maps = {}

            start_time = time.time()
            while eval_num < 4100:
                minimum = evaluate_random(minimum)
                eval_num += 1

                print("Eval num ", eval_num, "Minimum", minimum.fitness)

            path = os.path.join(base_path, "run" + str(m))
            if not (os.path.exists(path)):
                os.mkdir(path)

            end_time = time.time()
            alg_time += end_time - start_time

            map_points = minimum.map_points
            robot_path_x = minimum.robot_path_x
            robot_path_y = minimum.robot_path_y

            routes = []
            i = 0
            p = 0
            while p < len(robot_path_x):
                p_set = {}
                p_set["x"] = robot_path_x[p] - 25
                p_set["y"] = robot_path_y[p] - 25
                routes.append(p_set)
                p += 1

            all_routes["map" + str(i)] = routes
            all_maps["map" + str(i)] = map_points

            out_path = os.path.join(path, "scenarios.json")
            out_path_maps = os.path.join(path, "maps.json")

            # save_path3 = os.path.join(cf.files["tc_file"], "solutions_" + str(gen) + ".json")

            with open(out_path, "w") as outfile:
                json.dump(all_routes, outfile, indent=4)

            with open(out_path_maps, "w") as outfile:
                json.dump(all_maps, outfile, indent=4)

            build_scenario(map_points, path, i)

            m += 1
