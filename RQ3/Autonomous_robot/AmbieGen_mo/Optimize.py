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
from pymoo.factory import get_performance_indicator
from RDP import rdp
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

    build_convergence(res)


    if not(os.path.exists(cf.files["tc_img"])):
        os.mkdir(cf.files["tc_img"])

    if not(os.path.exists(cf.files["tc_file"])):
        os.mkdir(cf.files["tc_file"])

    if not(os.path.exists(cf.files["ga_archive"])):
        os.mkdir(cf.files["ga_archive"])

    #if os.listdir(cf.files["tc_img"]):
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
    #shutil.copyfile(".\\vehicle.py", ".\\"+dt_string+"_vehicle.py")

    zipObj = ZipFile(dt_string + '_results.zip', 'w')

    # Add multiple files to the zip
    zipObj.write(dt_string + "_tc_img.zip")
    zipObj.write(dt_string + "_tc_file.zip")
    zipObj.write(dt_string + "_conv.png")
    zipObj.write(dt_string + "_config.py")
    #zipObj.write(dt_string + "_vehicle.py")

    zipObj.close() 

    #  move the archive to the destination folder
    shutil.move(dt_string + '_results.zip', cf.files["ga_archive"]  + dt_string + '_results.zip')

    #  remove files
    os.remove(".\\" + dt_string + "_config.py")
    #os.remove(".\\" + dt_string + "_vehicle.py")
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
        if not(os.path.exists(cf.files["tc_img"] + "generation_" + str(gen))):
            os.mkdir(cf.files["tc_img"] + "generation_" + str(gen))

    #  build images and write tc to file
    #for gen in range(cf.ga["n_gen"]):
    for gen in [0, len(res.history) - 1]:
        test_cases = {}
        states_tc = {}
        all_routes = {}

        for i, x in enumerate(res.history[gen].pop.get("X")):
            #road_points = x[0].road_points
            map_points = x[0].map_points
            robot_path_x = x[0].robot_path_x
            robot_path_y = x[0].robot_path_y
            fitness = x[0].fitness
            states = x[0].states


            points = rdp(list(zip(robot_path_x, robot_path_y)), epsilon=1)

            image_car_path(map_points, robot_path_x, robot_path_y, points, fitness, gen, i)
            #build_scenario(map_points, robot_path_x, robot_path_y, gen, i)

            test_cases["tc" + str(i)] = map_points
            states_tc["tc" + str(i)] = states

            routes = []
            p = 0
            while p < len(robot_path_x):
                p_set = {}
                p_set["x"] = robot_path_x[p] - 24
                p_set["y"] = robot_path_y[p] - 24
                routes.append(p_set)
                p += 1
            all_routes["tc" + str(i)] = routes

        save_path3 = os.path.join(cf.files["tc_file"], "solutions_" + str(gen) + ".json")

        with open(save_path3, "w") as outfile:
            json.dump(all_routes, outfile, indent=4)



def build_scenario2(road_points, car_path_x, car_path_y, generation, i):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_frame_on(False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    road_x = []
    road_y = []
    for p in road_points:
        road_x.append(p[0])
        road_y.append(p[1])

    ax.scatter(road_x, road_y, s=150, marker='s', color='k')

    top = cf.model["map_size"] + 1
    bottom = 0 -1

    save_path = os.path.join(cf.files["tc_img"], "generation_" + str(generation))

    fig.savefig(save_path +"\\" + "map_" + str(i) + ".png", bbox_inches='tight',pad_inches = 0)
    
    plt.close(fig)

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

    ax.scatter(road_x, road_y, s=150, marker='s', color='k')

    top = cf.model["map_size"] + 1
    bottom = - 1


    fig.savefig(os.path.join(path, "map" + str(i) + ".png"), bbox_inches='tight', pad_inches=0)
    
    plt.close(fig)






def image_car_path(road_points, car_path_x, car_path_y, points,  fitness, generation, i):

    fig, ax = plt.subplots(figsize=(12, 12))
    #, nodes[closest_index][0], nodes[closest_index][1], 'go'
    #road_points2 = zip(*road_points)
    road_x = []
    road_y = []
    for p in road_points:
        road_x.append(p[0])
        road_y.append(p[1])



    _x = []
    _y = []
    for p in points:
        _x.append(p[0])
        _y.append(p[1])


    ax.plot(car_path_x, car_path_y, 'or', label="Robot path")
    ax.plot(_x, _y, "ob", label="Approximated path")

    ax.plot(road_x, road_y, '.k', label="Map")

    top = cf.model["map_size"] + 1
    bottom = -1

    ax.set_title( "Test case fitenss " + str(fitness)  , fontsize=17)

    ax.set_ylim(bottom, top)
    
    ax.set_xlim(bottom, top)

    ax.xaxis.set_ticks(np.arange(bottom, top, 5))
    ax.yaxis.set_ticks(np.arange(bottom, top, 5))
    ax.legend()


    save_path = os.path.join(cf.files["tc_img"], "generation_" + str(generation))

    fig.savefig(save_path +"\\" + "tc_" + str(i) + ".png")
 
    plt.close(fig)


algorithm = NSGA2(
    n_offsprings=10,
    pop_size=cf.ga["population"],
    sampling=MyTcSampling(),
    crossover=MyTcCrossover(cf.ga["cross_rate"]),
    mutation=MyTcMutation(cf.ga["mut_rate"]),
    eliminate_duplicates=MyDuplicateElimination(),
)

termination = MultiObjectiveSpaceToleranceTermination(tol=0.0025,
                                                      n_last=15,
                                                      nth_gen=5,
                                                      n_max_gen=cf.ga["n_gen"],
                                                      n_max_evals=None)


def calc_novelty(old, new):
    novelty = 0
    #print("OLD", old)
    #print("NEW", new)

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


if __name__ == "__main__":


    path_folder = ".\\results"
    if not(os.path.exists(path_folder)):
        os.mkdir(path_folder)
    it = 0
    for it in range(0, 30):
        res_dict = {}
     
        time_list = []
        m = 0

        base_path = ".\\results" + str(it) + "\\"
        base_path = os.path.join(base_path)
        if not(os.path.exists(base_path)):
            os.mkdir(base_path)
        

        start_time = time.time()
        alg_time = 0
        while alg_time < 7200:
        #for m in range(30):
                
            fit_list = []

            print("Evaluation new", m)

            t = int(time.time() * 1000)
            seed = ((t & 0xff000000) >> 24) + ((t & 0x00ff0000) >> 8) + ((t & 0x0000ff00) << 8) + ((t & 0x000000ff) << 24)
            print("Seed ", seed)

            start_time = time.time()

            res = minimize(
                MyProblem(), algorithm, ("n_gen", cf.ga["n_gen"]), seed=seed, verbose=True, save_history=True, eliminate_duplicates=True
            )

            end_time = time.time()

            alg_time += end_time - start_time

            print("time", res.exec_time)
            print("time, sec ", res.exec_time)

            time_list.append(res.exec_time)
            res_dict["run" + str(m)] = {}
            res_dict["run" + str(m)]["time"] = res.exec_time

            hv_values = []

            hv = get_performance_indicator("hv", ref_point=np.array([0, 0]))


            path = os.path.join(base_path, "run" + str(m))

            if not(os.path.exists(path)):
                os.mkdir(path)

            #path = ".\\results\\run" + str(m)

            gen = len(res.history) - 1

            #for gen in range(0, len(res.history)):

            i = 0
            #print(gen)
            minim = 0
            hv_list = []

            all_routes = {}
            all_maps = {}
            while i < len(res.history[gen].opt):
                result = res.history[gen].pop.get("X")[i]
                hv_item = res.history[gen].pop.get("F")[i]
                hv_list.append(hv_item)

                fit = result[0].fitness
                if fit < minim:
                    minim = fit

                map_points = result[0].map_points
                robot_path_x = result[0].robot_path_x
                robot_path_y = result[0].robot_path_y



                routes = []
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

                #save_path3 = os.path.join(cf.files["tc_file"], "solutions_" + str(gen) + ".json")

                with open(out_path, "w") as outfile:
                    json.dump(all_routes, outfile, indent=4)

                with open(out_path_maps, "w") as outfile:
                    json.dump(all_maps, outfile, indent=4)

                build_scenario(map_points,  path, i)

                i += 1
                    
                fit_list.append(minim)
                #print(min(fit_list))
                hv_values.append(hv.calc(np.array(hv_list)))


            gen = len(res.history) - 1
            reference = res.history[gen].pop.get("X")[0]
            novelty_list = []
            for i in range(1, len(res.history[gen].opt)):
                current = res.history[gen].pop.get("X")[i]
                nov = calc_novelty(reference[0].states, current[0].states)
                novelty_list.append(nov)


            res_dict["run" + str(m)]["fitness"] = fit_list
            print(min(fit_list))
            res_dict["run" + str(m)]["hv"] = hv_values 


            if len(novelty_list) > 0:
                res_dict["run" + str(m)]["novelty"] = sum(novelty_list)/len(novelty_list)
            else:
                res_dict["run" + str(m)]["novelty"] = 0


            with open("Results.json", "w") as f:
                json.dump(res_dict, f, indent=4)

            save_results(res)

            print("Time remaining ", (7200 - (alg_time))/3600, " hours")

            m += 1