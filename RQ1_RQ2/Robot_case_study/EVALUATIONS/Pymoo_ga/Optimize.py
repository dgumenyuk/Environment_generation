'''
Main module to launch the experiments and save the results
'''

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
from zipfile import ZipFile
import json
import time
from pymoo.algorithms.so_genetic_algorithm import GA


def build_convergence(res):
    # n_evals = np.array([e.evaluator.n_eval/cf.ga["n_gen"] for e in res.history])
    n_evals = np.arange(0, len(res.history), 1)
    opt = np.array([e.opt[0].F for e in res.history])

    fig, ax1 = plt.subplots(figsize=(12, 4))
    plt.title("Convergence")
    plt.plot(n_evals, opt, "o--")
    plt.xlabel("Number of generations")
    plt.ylabel("Fitness function value")
    # plt.show()
    fig.savefig(cf.files["ga_conv"] + "conv.png")
    plt.close(fig)


def save_results(res):


    build_convergence(res)

    if os.listdir(cf.files["tc_img"]):

        dt_string = str(int(time.time()))

        #  prepare files
        shutil.make_archive(dt_string + "_tc_img", "zip", cf.files["tc_img"])
        shutil.make_archive(dt_string + "_tc_file", "zip", cf.files["tc_file"])
        shutil.copyfile(".\\config.py", ".\\" + dt_string + "_config.py")
        shutil.copyfile(".\\conv.png", ".\\" + dt_string + "_conv.png")
        # shutil.copyfile(".\\vehicle.py", ".\\"+dt_string+"_vehicle.py")

        zipObj = ZipFile(dt_string + "_results.zip", "w")

        # Add multiple files to the zip
        zipObj.write(dt_string + "_tc_img.zip")
        zipObj.write(dt_string + "_tc_file.zip")
        zipObj.write(dt_string + "_conv.png")
        zipObj.write(dt_string + "_config.py")
        # zipObj.write(dt_string + "_vehicle.py")

        zipObj.close()

        #  move the archive to the destination folder
        shutil.move(
            dt_string + "_results.zip",
            cf.files["ga_archive"] + dt_string + "_results.zip",
        )

        #  remove files
        os.remove(".\\" + dt_string + "_config.py")
        # os.remove(".\\" + dt_string + "_vehicle.py")
        os.remove(".\\" + dt_string + "_conv.png")
        os.remove(".\\" + "conv.png")
        os.remove(".\\" + dt_string + "_tc_img.zip")
        os.remove(".\\" + dt_string + "_tc_file.zip")

        for folder in os.listdir(cf.files["tc_img"]):
            shutil.rmtree(cf.files["tc_img"] + folder)

        for file in os.listdir(cf.files["tc_file"]):
            os.remove(cf.files["tc_file"] + file)

    #  create new folders
    # for gen in range(cf.ga["n_gen"]):
    for gen in [0, len(res.history) - 1]:
        if not (os.path.exists(cf.files["tc_img"] + "generation_" + str(gen))):
            os.mkdir(cf.files["tc_img"] + "generation_" + str(gen))

    #  build images and write tc to file
    # for gen in range(cf.ga["n_gen"]):
    for gen in [0, len(res.history) - 1]:
        test_cases = {}
        states_tc = {}

        for i, x in enumerate(res.history[gen].pop.get("X")):
            # road_points = x[0].road_points
            map_points = x[0].map_points
            robot_path_x = x[0].robot_path_x
            robot_path_y = x[0].robot_path_y
            fitness = x[0].fitness
            states = x[0].states

            image_car_path(map_points, robot_path_x, robot_path_y, fitness, gen, i)

            test_cases["tc" + str(i)] = map_points
            states_tc["tc" + str(i)] = states

        save_path = os.path.join(
            cf.files["tc_file"], "generation_" + str(gen) + ".json"
        )
        save_path2 = os.path.join(cf.files["tc_file"], "states_" + str(gen) + ".json")




def image_car_path(road_points, car_path_x, car_path_y, fitness, generation, i):

    fig, ax = plt.subplots(figsize=(12, 12))
    # , nodes[closest_index][0], nodes[closest_index][1], 'go'
    # road_points2 = zip(*road_points)
    road_x = []
    road_y = []
    for p in road_points:
        road_x.append(p[0])
        road_y.append(p[1])

    ax.plot(car_path_x, car_path_y, "-r", label="Car path")

    ax.plot(road_x, road_y, ".k", label="Road")

    top = cf.model["map_size"]
    bottom = 0

    ax.set_title("Test case fitenss " + str(fitness), fontsize=17)

    ax.set_ylim(bottom, top)

    ax.set_xlim(bottom, top)
    ax.legend()

    save_path = os.path.join(cf.files["tc_img"], "generation_" + str(generation))

    fig.savefig(save_path + "\\" + "tc_" + str(i) + ".jpg")

    plt.close(fig)


termination = MultiObjectiveSpaceToleranceTermination(
    tol=0.0025, n_last=15, nth_gen=5, n_max_gen=cf.ga["n_gen"], n_max_evals=None
)


algorithm = GA(
    n_offsprings=10,
    pop_size=cf.ga["population"],
    sampling=MyTcSampling(),
    crossover=MyTcCrossover(cf.ga["cross_rate"]),
    mutation=MyTcMutation(cf.ga["mut_rate"]),
    eliminate_duplicates=MyDuplicateElimination(),
)


def calc_novelty(old, new):
    novelty = 0
    # print("OLD", old)
    # print("NEW", new)

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
    # print("NOVELTY", novelty)
    return -novelty


if __name__ == "__main__":

    res_dict = {}

    time_list = []
    m = 0

    for m in range(30):

        fit_list = []
        print("Evaluation new", m)

        t = int(time.time() * 1000)
        seed = (
            ((t & 0xFF000000) >> 24)
            + ((t & 0x00FF0000) >> 8)
            + ((t & 0x0000FF00) << 8)
            + ((t & 0x000000FF) << 24)
        )
        print("Seed ", seed)

        res = minimize(
            MyProblem(),
            algorithm,
            ("n_gen", cf.ga["n_gen"]),
            seed=seed,
            verbose=True,
            save_history=True,
            eliminate_duplicates=True,
        )

        print("time", res.exec_time)
        print("time, sec ", res.exec_time)

        time_list.append(res.exec_time)
        res_dict["run" + str(m)] = {}
        res_dict["run" + str(m)]["time"] = res.exec_time

        for gen in range(0, len(res.history)):

            # print(len(res.history[gen].pop.get("X")))
            # print(len(res.history[gen].opt))

            i = 0
            # print(gen)
            minim = 0
            hv_list = []
            # while i < len(res.history[gen].opt):

            result = res.history[gen].pop.get("X")[0]

            fit = result[0].fitness
            fit_list.append(fit)

        gen = len(res.history) - 1
        reference = res.history[gen].pop.get("X")[0]
        novelty_list = []
        for i in range(1, 5):
            current = res.history[gen].pop.get("X")[i]
            nov = calc_novelty(reference[0].states, current[0].states)
            novelty_list.append(nov)

        res_dict["run" + str(m)]["fitness"] = fit_list
        res_dict["run" + str(m)]["novelty"] = sum(novelty_list) / len(novelty_list)

        with open("Results_dict2.json", "w") as f:
            json.dump(res_dict, f, indent=4)

    save_results(res)
