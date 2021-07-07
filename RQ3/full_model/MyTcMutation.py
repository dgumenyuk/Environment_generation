import numpy as np
from pymoo.model.mutation import Mutation
import copy
import config as cf
import random as rm
from scipy.spatial.distance import directed_hausdorff

class MyTcMutation(Mutation):
    def __init__(self, mut_rate):
        super().__init__()
        self.mut_rate = mut_rate

    def _do(self, problem, X, **kwargs):
        # print("X mutate", X.shape)
        # for each individual
        #print("MUT1")
        #print("Mutation size", len(X))
        for i in range(len(X)):
            r = np.random.random()
            s = X[i, 0]
            if s is None:
                print("S i none")



            '''

            print("Mut_start*******")
            print("States", s.states)
            print("Mut_end*********")
            '''

            # with a probabilty of 40% - change the order of characters
            if (r < self.mut_rate) and (s is not None):#cf.ga["mut_rate"]:
                #
                # for some reason it seems we must do a deep copy
                # and replace the original object
                # pymoo seems to keep a deep copy of the best object if I change it
                # in a mutation it will not chnage pymoo best individual and we end up
                # with an incosistency in evaluated fitnesses
                sn = copy.deepcopy(s)

                #print("Child before", sn.states)

                sn.get_points()
                sn.remove_invalid_cases()

                #wr = np.random.random()
                wr = rm.randint(1, 101)
                child = sn.states
                old_points = sn.road_points
                old_states = child

                if wr < 20:

                    #print("mut1")

                    # print("mutation MUT1")
                    candidates = list(np.random.randint(0, high=len(child), size=2))
                    temp = child["st" + str(candidates[0])]
                    child["st" + str(candidates[0])] = child["st" + str(candidates[1])]
                    child["st" + str(candidates[1])] = temp
                    #sn.states = child
                    #print("Child after 1", child)

                elif wr >= 20 and wr <= 40 :
                    # print("mutation MUT2")
                    #print("mut2")
                    num = np.random.randint(0, high=len(child) )
                    #value = np.random.choice(["state", "value"])

                    value ="value"
                    duration_list = []
                    if child["st" + str(num)]["state"] == "straight":
                        duration_list = np.arange(cf.model["min_len"], cf.model["max_len"], cf.model["len_step"])   
                    else:
                        duration_list = np.arange(cf.model["min_angle"], cf.model["max_angle"], cf.model["ang_step"])
                            
                    child["st" + str(num)][value] = int(np.random.choice(duration_list))

                        #sn.states = child
                    #elif value == "state":
                    value ="state"

                    if child["st" + str(num)][value] == "straight":
                        child["st" + str(num)][value] = np.random.choice(["left", "right"])
                        duration_list = np.arange(cf.model["min_angle"], cf.model["max_angle"], cf.model["ang_step"])
                        child["st" + str(num)]["value"] = int(np.random.choice(duration_list))
                    else:
                        child["st" + str(num)][value] = "straight"
                        duration_list = np.arange(cf.model["min_len"], cf.model["max_len"], cf.model["len_step"])
                        child["st" + str(num)]["value"] = int(np.random.choice(duration_list))


                

                else:
                    #print("mut 4")
                    cand = list(np.random.randint(0, high=len(child), size=int(len(child)/2)))
                    while cand:
                        c1 =  np.random.choice(cand)
                        cand.remove(c1)
                        if cand:
                            c2 = np.random.choice(cand)
                            cand.remove(c2)
                            temp = child["st" + str(c1)]
                            child["st" + str(c1)] = child["st" + str(c2)]
                            child["st" + str(c2)] = temp
                        else:
                            if child["st" + str(c1)]["state"] == "straight":
                                duration_list =  np.arange(cf.model["min_len"], cf.model["max_len"], cf.model["len_step"])   
                            else:
                                duration_list =  np.arange(cf.model["min_angle"], cf.model["max_angle"], cf.model["ang_step"])
                            child["st" + str(c1)]['value'] = int(np.random.choice(duration_list))

                    #print("after", child)


                #print("MUT")

                


                sn.states = child
                    #print("Child after 2", child)

                #print("sn.states", sn.states)        
                sn.get_points()
                #print("sn.road_points", sn.road_points)
                sn.remove_invalid_cases()
                new_points = sn.road_points
                #sn.novelty = -max(directed_hausdorff(old_points, new_points)[0], directed_hausdorff(old_points, new_points)[0])
                sn.novelty = sn.calc_novelty(old_states, sn.states)
                #print("sn.road_points", sn.road_points)
                #print(sn.eval_fitness())

                X[i, 0] = sn

        return X
        '''
        elif wr >= 0.50 and wr < 0.75:
            print("new mut")
            print("before", child)
            for tc in child:
                state = child[tc]["state"]
                if state == "straight":
                    state = np.random.choice(["left", "right"])
                    child[tc]["state"] = state
                else:
                    child[tc]["state"] = "straight"
            print("after", child)
        '''