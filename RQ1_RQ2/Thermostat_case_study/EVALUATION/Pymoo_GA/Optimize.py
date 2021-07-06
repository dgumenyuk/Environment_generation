'''
Main module to run the search and save results
'''


import config as cf
import numpy as np
from pymoo.algorithms.so_genetic_algorithm import GA
from pymoo.optimize import minimize

from MyProblem import MyProblem
from MyTcMutation import MyTcMutation
from MyTcCrossOver import MyTcCrossover
from MyDuplicates import MyDuplicateElimination
from MyTcSampling import MyTcSampling
import matplotlib.pyplot as plt
import os
import shutil
from zipfile import ZipFile
import json
import time


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

    if os.listdir(cf.files["tc_file"]):

        dt_string = str(int(time.time()))

        #  prepare files
        shutil.make_archive(dt_string + "_tc_img", "zip", cf.files["tc_img"])
        shutil.make_archive(dt_string + "_tc_file", "zip", cf.files["tc_file"])
        shutil.copyfile(".\\config.py", ".\\" + dt_string + "_config.py")
        shutil.copyfile(".\\conv.png", ".\\" + dt_string + "_conv.png")

        zipObj = ZipFile(dt_string + "_results.zip", "w")

        # Add multiple files to the zip
        zipObj.write(dt_string + "_tc_img.zip")
        zipObj.write(dt_string + "_tc_file.zip")
        zipObj.write(dt_string + "_conv.png")
        zipObj.write(dt_string + "_config.py")

        zipObj.close()

        #  move the archive to the destination folder
        shutil.move(
            dt_string + "_results.zip",
            cf.files["ga_archive"] + dt_string + "_results.zip",
        )

        #  remove files
        os.remove(".\\" + dt_string + "_config.py")
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
        os.mkdir(cf.files["tc_img"] + "generation_" + str(gen))

    #  build images and write tc to file
    for gen in [0, len(res.history) - 1]:
        states_tc = {}

        for i, x in enumerate(res.history[gen].pop.get("X")):

            states = x[0].states

            x[0].build_graph(gen, i)

            states_tc["tc" + str(i)] = states
            if i > 20:
                break

        save_path2 = os.path.join(cf.files["tc_file"], "states_" + str(gen) + ".json")

        with open(save_path2, "w") as outfile:
            json.dump(states_tc, outfile, indent=4)



algorithm = GA(
    # n_offsprings=2,
    pop_size=cf.ga["population"],
    sampling=MyTcSampling(),
    crossover=MyTcCrossover(),
    mutation=MyTcMutation(),
    eliminate_duplicates=MyDuplicateElimination(),
)


def calc_novelty(old, new):
    novelty = 0
    difference = abs(len(new) - len(old)) / 2
    novelty += difference
    if len(new) <= len(old):
        shorter = new
    else:
        shorter = old
    for tc in shorter:
        if old[tc]["temp"] == new[tc]["temp"]:
            value_list = [old[tc]["duration"], new[tc]["duration"]]
            ratio = max(value_list) / min(value_list)
            if ratio >= 2:
                novelty += 0.5
        else:
            novelty += 1

    return -novelty


if __name__ == "__main__":

    res_dict = {}

    time_list = []

    m = 0

    for m in range(30):

        fit_list = []
        print("Evaluation start", m)

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


        #  save fitness values to a list

        for gen in range(0, len(res.history)):

            i = 0
            minim = 0
            hv_list = []

            result = res.history[gen].pop.get("X")[0]

            fit = result[0].fitness
            fit_list.append(fit)


        #  evaluate the diversity

        gen = len(res.history) - 1
        reference = res.history[gen].pop.get("X")[0]
        novelty_list = []
        for i in range(1, 5):
            current = res.history[gen].pop.get("X")[i]
            nov = calc_novelty(reference[0].states, current[0].states)
            novelty_list.append(nov)

        res_dict["run" + str(m)]["fitness"] = fit_list
        res_dict["run" + str(m)]["novelty"] = sum(novelty_list) / len(novelty_list)

        with open("Results.json", "w") as f:
            json.dump(res_dict, f, indent=4)

        #  build illustrations

        save_results(res)
