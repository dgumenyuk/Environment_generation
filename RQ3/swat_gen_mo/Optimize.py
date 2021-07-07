import swat_gen.config as cf
import numpy as np
from pymoo.algorithms.so_genetic_algorithm import GA
from pymoo.optimize import minimize

from swat_gen.MyProblem import MyProblem
from swat_gen.MyTcMutation import MyTcMutation
from swat_gen.MyTcCrossOver import MyTcCrossover
from swat_gen.MyDuplicates import MyDuplicateElimination
from pymoo.util.termination.f_tol import MultiObjectiveSpaceToleranceTermination
from swat_gen.MyTcSampling import MyTcSampling
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import os
import shutil
from shutil import make_archive
from zipfile import ZipFile
import json
import time
from scipy.spatial.distance import directed_hausdorff
from pymoo.algorithms.nsga2 import NSGA2
from pymoo.visualization.scatter import Scatter
def build_convergence(res):
    #n_evals = np.array([e.evaluator.n_eval/cf.ga["n_gen"] for e in res.history])
    n_evals = np.arange(0, len(res.history), 1)
    opt = np.array([e.opt[0].F for e in res.history])
    
    fig, ax1 = plt.subplots(figsize=(12, 4))
    plt.title("Convergence") 
    plt.plot(n_evals, opt, "o--")
    plt.xlabel("Number of generations")
    plt.ylabel("Fitness function value")
    #plt.show()
    fig.savefig(cf.files["ga_conv"] + "conv.png")
    plt.close(fig)

def save_results(res):

    if os.listdir(cf.files["tc_file"]):
        #now = datetime.now()
        #dt_string = str(now.strftime("%d/%m/%Y %H:%M:%S"))

        dt_string = str(int(time.time()))
        #  create dirtectory
        #os.mkdir(cf.files["ga_archive"] + dt_string)

        #  prepare files
        shutil.make_archive(dt_string + "_tc_img", 'zip', cf.files["tc_img"] )
        shutil.make_archive(dt_string + "_tc_file", 'zip', cf.files["tc_file"] )
        shutil.copyfile(".\\config.py", ".\\"+dt_string+"_config.py")
        shutil.copyfile(".\\conv.png", ".\\"+dt_string+"_conv.png")
        shutil.copyfile(".\\vehicle.py", ".\\"+dt_string+"_vehicle.py")

        zipObj = ZipFile(dt_string + '_results.zip', 'w')

        # Add multiple files to the zip
        zipObj.write(dt_string + "_tc_img.zip")
        zipObj.write(dt_string + "_tc_file.zip")
        zipObj.write(dt_string + "_conv.png")
        zipObj.write(dt_string + "_config.py")
        zipObj.write(dt_string + "_vehicle.py")

        zipObj.close() 

        #  move the archive to the destination folder
        shutil.move(dt_string + '_results.zip', cf.files["ga_archive"]  + dt_string + '_results.zip')

        #  remove files
        os.remove(".\\" + dt_string + "_config.py")
        os.remove(".\\" + dt_string + "_vehicle.py")
        os.remove(".\\" + dt_string + "_conv.png")
        os.remove(".\\" + "conv.png")
        os.remove(".\\" + dt_string + "_tc_img.zip")
        os.remove(".\\" + dt_string + "_tc_file.zip")

        for folder in os.listdir(cf.files["tc_img"]):
            shutil.rmtree(cf.files["tc_img"] + folder)

        for file in os.listdir(cf.files["tc_file"]):
            os.remove(cf.files["tc_file"] + file)

    #  create new folders
    #for gen in range(cf.ga["n_gen"]):
    for gen in [0, len(res.history) - 1]:
        os.mkdir(cf.files["tc_img"] + "generation_" + str(gen))

    #  build images and write tc to file
    #for gen in range(cf.ga["n_gen"]):
    for gen in [0, len(res.history) - 1]:
        test_cases = {}
        states_tc = {}

        for i, x in enumerate(res.history[gen].pop.get("X")):
            #road_points = x[0].road_points
            road_points = x[0].intp_points
            car_path = x[0].car_path
            fitness = x[0].fitness
            states = x[0].states

            image_car_path(road_points, car_path, fitness, gen, i)

            test_cases["tc" + str(i)] = road_points
            states_tc["tc" + str(i)] = states

        save_path = os.path.join(cf.files["tc_file"], "generation_" + str(gen) + ".json")
        save_path2 = os.path.join(cf.files["tc_file"], "states_" + str(gen) + ".json")
        with open(save_path, "w") as outfile:
            json.dump(test_cases, outfile, indent=4)
        with open(save_path2, "w") as outfile:
            json.dump(states_tc, outfile, indent=4)

    build_convergence(res)



def image_car_path(road_points, car_path, fitness, generation, i):

    fig, ax = plt.subplots(figsize=(12, 12))
    #, nodes[closest_index][0], nodes[closest_index][1], 'go'
    #road_points2 = zip(*road_points)
    road_x = []
    road_y = []
    for p in road_points:
        road_x.append(p[0])
        road_y.append(p[1])

    if len(car_path):
        ax.plot(car_path[0], car_path[1], 'bo', label="Car path")

    ax.plot(road_x, road_y, 'yo--', label="Road")

    top = cf.model["map_size"]
    bottom = 0

    ax.set_title( "Test case fitenss " + str(fitness)  , fontsize=17)

    ax.set_ylim(bottom, top)
    
    ax.set_xlim(bottom, top)
    ax.legend()


    save_path = os.path.join(cf.files["tc_img"], "generation_" + str(generation))

    fig.savefig(save_path +"\\" + "tc_" + str(i) + ".jpg")
 
    plt.close(fig)









def optimize():

    algorithm = NSGA2(
    n_offsprings=25,
    pop_size=cf.ga["population"],
    sampling=MyTcSampling(),
    crossover=MyTcCrossover(cf.ga["cross_rate"]),
    mutation=MyTcMutation(cf.ga["mut_rate"]),
    eliminate_duplicates=MyDuplicateElimination())



    termination = MultiObjectiveSpaceToleranceTermination(tol=0.0025,
                                                      n_last=15,
                                                      nth_gen=5,
                                                      n_max_gen=100,
                                                      n_max_evals=None)



    t = int(time.time() *1000) 
    seed = ((t & 0xff000000) >> 24) + ((t & 0x00ff0000) >>  8) +((t & 0x0000ff00) <<  8) +((t & 0x000000ff) << 24)

    res = minimize(
            MyProblem(), algorithm, termination, seed=seed, verbose=False, save_history=True, eliminate_duplicates=True
        )

    print("Best solution found: \nF = %s" % (res.F))
    gen = len(res.history) - 1
    test_cases = {}
    i = 0

    while i < len(res.F):
        result = res.history[gen].pop.get("X")[i]

        road_points = result[0].intp_points
        road_points = remove_invalid_cases(road_points) 
        test_cases["tc" + str(i)] = road_points
        i += 1
    return test_cases




def remove_invalid_cases(points):
    new_list = []
    i = 0
    while i < len(points):
        if point_in_range_2(points[i]) == 1:
            new_list.append(points[i])
        else:
            return new_list
        i+=1

    return new_list


def point_in_range_2(a):
    """check if point is in the acceptable range"""
    if ((0 + 4) < a[0] and a[0] < (cf.model["map_size"]- 4)) and ((0 +4) < a[1] and a[1] < (cf.model["map_size"] - 4)):
        return 1
    else:
        return 0