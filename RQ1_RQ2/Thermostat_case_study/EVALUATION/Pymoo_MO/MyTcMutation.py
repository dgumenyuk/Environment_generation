import numpy as np
from pymoo.model.mutation import Mutation
import copy
import config as cf
import random as rm


class MyTcMutation(Mutation):
    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        # print("X mutate", X.shape)
        # for each individual
        for i in range(len(X)):
            r = np.random.random()
            s = X[i, 0]

            # with a probabilty of 40% - change the order of characters
            if r < cf.ga["mut_rate"]:
                #
                # for some reason it seems we must do a deep copy
                # and replace the original object
                # pymoo seems to keep a deep copy of the best object if I change it
                # in a mutation it will not chnage pymoo best individual and we end up
                # with an incosistency in evaluated fitnesses
                sn = copy.deepcopy(s)

                wr = np.random.random()
                child = sn.states
                child_init = child
                if wr < 0.5:


                    candidates = list(np.random.randint(1, high=len(child), size=2))
                    temp = child["st" + str(candidates[0])]
                    child["st" + str(candidates[0])] = child["st" + str(candidates[1])]
                    child["st" + str(candidates[1])] = temp
                    sn.states = child

                else:

                    num = int(np.random.randint(1, high=len(child), size=1))
                    value = np.random.choice(["duration", "temp", "model"])

                    if value == "duration":
                        duration_list = []
                        for m in range(
                            cf.model["duration_min"], cf.model["duration_max"], 5
                        ):
                            duration_list.append(m)
                        child["st" + str(num)][value] = int(
                            np.random.choice(duration_list)
                        )

                        sn.states = child
                    elif value == "temp":
                        maximum = cf.model["temp_max"]
                        minimum = cf.model["temp_min"]
                        jump = cf.model["jump"]
                        action = np.random.choice(["inc", "dec"])
                        temp = child["st" + str(num - 1)][value]

                        if action == "inc":

                            if temp + jump > maximum:
                                result = rm.randint(temp, maximum)
                            else:
                                result = rm.randint(temp, temp + jump)

                            child["st" + str(num)][value] = result

                            sn.states = child

                        elif action == "dec":

                            if temp - jump < minimum:
                                result = rm.randint(minimum, temp)
                            else:
                                result = rm.randint(temp - jump, temp)

                            child["st" + str(num)][value] = result

                            sn.states = child
                    elif value == "model":
                        model = rm.randint(0, cf.model["model_num"] - 1)

                        child["st" + str(num)][value] = model

                        sn.states = child

                sn.states = sn.check_states()
                sn.novelty = sn.calc_novelty(child_init, sn.states)

                X[i, 0] = sn

        return X
