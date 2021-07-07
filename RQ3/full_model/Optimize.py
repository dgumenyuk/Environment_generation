import config as cf
import numpy as np
from pymoo.algorithms.so_genetic_algorithm import GA
from pymoo.optimize import minimize

from MyProblem import MyProblem
from MyTcMutation import MyTcMutation
from MyTcCrossOver import MyTcCrossover
from MyDuplicates import MyDuplicateElimination
from pymoo.util.termination.f_tol import MultiObjectiveSpaceToleranceTermination
from MyTcSampling import MyTcSampling
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
from pymoo.factory import get_performance_indicator, get_termination
import pandas as pd
import statistics
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
            novelty = x[0].novelty

            image_car_path(road_points, car_path, fitness, novelty, gen, i)

            test_cases["tc" + str(i)] = road_points
            states_tc["tc" + str(i)] = states

        save_path = os.path.join(cf.files["tc_file"], "generation_" + str(gen) + ".json")
        save_path2 = os.path.join(cf.files["tc_file"], "states_" + str(gen) + ".json")
        with open(save_path, "w") as outfile:
            json.dump(test_cases, outfile, indent=4)
        with open(save_path2, "w") as outfile:
            json.dump(states_tc, outfile, indent=4)

    build_convergence(res)



def image_car_path(road_points, car_path, fitness, novelty, generation, i):

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

    ax.set_title( "Test case fitenss " + str(fitness) + " novely " + str(novelty) , fontsize=17)

    ax.set_ylim(bottom, top)
    
    ax.set_xlim(bottom, top)
    ax.legend()


    save_path = os.path.join(cf.files["tc_img"], "generation_" + str(generation))

    fig.savefig(save_path +"\\" + "tc_" + str(i) + ".jpg")
 
    plt.close(fig)






algorithm = NSGA2(
    #n_offsprings=4,
    n_offsprings=25,
    pop_size=cf.ga["population"],
    sampling=MyTcSampling(),
    crossover=MyTcCrossover(cf.ga["cross_rate"]),
    mutation=MyTcMutation(cf.ga["mut_rate"]),
    eliminate_duplicates=MyDuplicateElimination(),
)


algorithm2 = GA(
    n_offsprings=25,
    pop_size=cf.ga["population"],
    sampling=MyTcSampling(),
    crossover=MyTcCrossover(cf.ga["cross_rate"]),
    mutation=MyTcMutation(cf.ga["mut_rate"]),
    eliminate_duplicates=MyDuplicateElimination(),
)


termination2 = MultiObjectiveSpaceToleranceTermination(tol=0.0025,
                                                      n_last=cf.ga["n_gen"],
                                                      nth_gen=5,
                                                      n_max_gen=cf.ga["n_gen"],
                                                      n_max_evals=None)


termination = get_termination("time", "02:00:00")


def calc_novelty(old, new):
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

if __name__ == "__main__":

    res_dict = {}

    time_list = []
    m = 0

    for m in range(10):
        fit_list = []

        print("Evaluation", m)

        t = int(time.time() * 1000)
        seed = ((t & 0xff000000) >> 24) + ((t & 0x00ff0000) >> 8) + ((t & 0x0000ff00) << 8) + ((t & 0x000000ff) << 24)
        print("Seed ", seed)

        res = minimize(
            MyProblem(), algorithm, termination=termination, seed=seed, verbose=True, save_history=True, eliminate_duplicates=True
        )

        print("time", res.exec_time)
        print("time, sec ", res.exec_time)

        time_list.append(res.exec_time)
        res_dict["run" + str(m)] = {}
        res_dict["run" + str(m)]["time"] = res.exec_time

        hv_values = []

        hv = get_performance_indicator("hv", ref_point=np.array([0, 0]))

        for gen in range(0, len(res.history)):

            i = 0
            #print(gen)
            minim = 0
            hv_list = []
            while i < len(res.history[gen].opt):
                result = res.history[gen].pop.get("X")[i]
                hv_item = res.history[gen].pop.get("F")[i]
                hv_list.append(hv_item)

                fit = result[0].fitness
                #print(fit)
                if fit < minim:
                    minim = fit

                i += 1
            fit_list.append(minim)
            #print(min(fit_list))
            hv_values.append(hv.calc(np.array(hv_list)))

        gen = len(res.history)-1

        pop_fitness = []
        failure_list = []
        failed_roads = []

        for i, x in enumerate(res.history[gen].pop.get("X")):
            #road_points = x[0].road_points
            fitness = x[0].oob
            road_points = x[0].intp_points

            pop_fitness.append(fitness)
            if fitness >= 0.85:
                failure_list.append(fitness)
                failed_roads.append(road_points)

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
        res_dict["run" + str(m)]["last_pop"] = pop_fitness
        res_dict["run" + str(m)]["failures"] = failure_list
        res_dict["run" + str(m)]["failed_roads"] = failed_roads


        if len(novelty_list) > 0:
            res_dict["run" + str(m)]["novelty"] = sum(novelty_list)/len(novelty_list)
        else:
            res_dict["run" + str(m)]["novelty"] = 0

        with open("Results_dist4.json", "w") as f:
            json.dump(res_dict, f, indent=4)





    #save_results(res)


    '''
    #solution_list = []
    #for i in range(0, 50):
    #("n_gen", cf.ga["n_gen"])
    #termination,

    # one evaluation
    
    res = minimize(
        MyProblem(), algorithm, termination, seed=cf.ga["seed"], verbose=True, save_history=True, eliminate_duplicates=True
    )
    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
    s = res.X[0]

   # print(len(res.F))


    Scatter().add(res.F).show()
    i = 0
    #results = res.X[np.argsort(res.F[:, 0])]
    gen = len(res.history) - 1

    x_list = []
    y_list = []
    while i < len(res.F):
        result = res.history[gen].pop.get("X")[i]

        fit = result[0].fitness
        novelty = result[0].novelty

        x_list.append(fit)
        y_list.append(novelty)

        i += 1
    print("x", x_list)
    print("y", y_list)

    save_results(res)



   '''

    


    '''
    &&&&&&&&&&&&&&&Old
    # best configuration
    tests = pd.read_csv("GA_configs.csv")
    for i in tests.index:


        num_off = tests.loc[i,"Num_offspring"]
        if num_off == "all":
            num_off = None
        else:
            num_off = int(num_off)



        algorithm = NSGA2(
            n_offsprings=num_off,
            pop_size=tests.loc[i,"Pop_size"],
            sampling=MyTcSampling(),
            crossover=MyTcCrossover(cf.ga["cross_rate"]),
            mutation=MyTcMutation(cf.ga["mut_rate"]),
            eliminate_duplicates=MyDuplicateElimination(),
        )


        fit_list = []
        n_gen_list = []
        diversity_list = []

        print(i)

        volume_list = []
        res_dict = {}

        time_list = []

        for m in range(30):

            print("Evaluation ", m)

            t = int(time.time() * 1000)
            seed = ((t & 0xff000000) >> 24) + ((t & 0x00ff0000) >> 8) + ((t & 0x0000ff00) << 8) + ((t & 0x000000ff) << 24)
            print("Seed ", seed)

            start = time.time()


            res = minimize(
                MyProblem(), algorithm, ("n_gen", tests.loc[i, "Gen_num"]), seed=seed, verbose=False, save_history=False, eliminate_duplicates=True
            )

            stop = time.time()
            secs = stop - start

            hv = get_performance_indicator("hv", ref_point=np.array([0, 0]))

            A = res.F

            print("hv", hv.calc(A))
            print("time, sec ", secs)

            volume_list.append(hv.calc(A))
            time_list.append(secs)


        res_dict[str(i)] = volume_list


        tests.at[i, "Hypervol_ave"] = sum(volume_list)/len(volume_list)
        print( "hyper_av", sum(volume_list)/len(volume_list))
        tests.at[i, "Hypervol_stdev"] = statistics.stdev(volume_list)
        print("hyper_stdev", statistics.stdev(volume_list))

        tests.at[i, "Time_ave"] = sum(time_list)/len(time_list)
        print( "Time_ave", sum(time_list)/len(time_list))
        tests.at[i, "Time_stdev"] = statistics.stdev(time_list)
        print("Time_stdev", statistics.stdev(time_list))



        with open ("Results_dict.json", "w") as f:
            json.dump(res_dict, f, indent=4)



        tests.to_csv("Results.csv",index=False)

'''



# random vs ga
    #save_results(res)
    #s.eval_fitness()
    #s.build_graph()


    '''
    print(s.states)
    print(s.intp_points)
    print(s.fitness)
    print("Just fitnes", s.just_fitness)

    gen = len(res.history)-1
    result = res.history[gen].pop.get("X")[0]
    base_road_points = result[0].intp_points
    p = 1
    novelty_list = []

    while p < 5:
        result = res.history[gen].pop.get("X")[p]

        road_points = result[0].intp_points
        #road_points = check_points(road_points) 
        novelty = max(directed_hausdorff(base_road_points, road_points)[0], directed_hausdorff(road_points, base_road_points)[0])
        novelty_list.append(novelty)
        p += 1
    print("Novelty", novelty_list)
    print("Novelty ave", sum(novelty_list)/len(novelty_list))

    #build_convergence(res, 1)

    for i in res.history[0].pop.get("X"):
        print(i[0].road_points)
        print(i[0].car_path)
        print(i[0].fitness)
        print(i[0].states)

    
    save_results(res)


    '''

    #print(res.history[0].pop.get("X"))
    #print("History", res.pop.get("X")))

    #solution_list.append(s.fitness)

    #opt = [e.opt[0].F for e in res.history]
  
   # with open("ga_res2.csv", 'w+', newline='') as myfile:
    #    wr = csv.writer(myfile)
        #wr.writerow(solution_list)
     #   wr.writerow(opt)

