import numpy as np
from pymoo.model.mutation import Mutation
import copy
import config as cf
import random as rm

class MyTcMutation(Mutation):
    def __init__(self, mut_rate):
        super().__init__()
        self.mut_rate = mut_rate

    def _do(self, problem, X, **kwargs):

        for i in range(len(X)):
            r = np.random.random()
            s = X[i, 0]
            if s is None:
                print("S i none")

            if (r < self.mut_rate) and (s is not None):  # cf.ga["mut_rate"]:
                #
                # for some reason it seems we must do a deep copy
                # and replace the original object
                # pymoo seems to keep a deep copy of the best object if I change it
                # in a mutation it will not chnage pymoo best individual and we end up
                # with an incosistency in evaluated fitnesses
                sn = copy.deepcopy(s)

                sn.get_points()
                sn.remove_invalid_cases()

                wr = rm.randint(1, 101)
                child = sn.states
                old_states = child

                if wr < 20:

                    candidates = list(np.random.randint(0, high=len(child), size=2))
                    temp = child["st" + str(candidates[0])]
                    child["st" + str(candidates[0])] = child["st" + str(candidates[1])]
                    child["st" + str(candidates[1])] = temp

                elif wr >= 20 and wr <= 40:
                    num = np.random.randint(0, high=len(child))

                    value = "value"
                    duration_list = []
                    if child["st" + str(num)]["state"] == "straight":
                        duration_list = np.arange(
                            cf.model["min_len"],
                            cf.model["max_len"],
                            cf.model["len_step"],
                        )
                    else:
                        duration_list = np.arange(
                            cf.model["min_angle"],
                            cf.model["max_angle"],
                            cf.model["ang_step"],
                        )

                    child["st" + str(num)][value] = int(np.random.choice(duration_list))

                    value = "state"

                    if child["st" + str(num)][value] == "straight":
                        child["st" + str(num)][value] = np.random.choice(
                            ["left", "right"]
                        )
                        duration_list = np.arange(
                            cf.model["min_angle"],
                            cf.model["max_angle"],
                            cf.model["ang_step"],
                        )
                        child["st" + str(num)]["value"] = int(
                            np.random.choice(duration_list)
                        )
                    else:
                        child["st" + str(num)][value] = "straight"
                        duration_list = np.arange(
                            cf.model["min_len"],
                            cf.model["max_len"],
                            cf.model["len_step"],
                        )
                        child["st" + str(num)]["value"] = int(
                            np.random.choice(duration_list)
                        )

                else:

                    cand = list(
                        np.random.randint(0, high=len(child), size=int(len(child) / 2))
                    )
                    while cand:
                        c1 = np.random.choice(cand)
                        cand.remove(c1)
                        if cand:
                            c2 = np.random.choice(cand)
                            cand.remove(c2)
                            temp = child["st" + str(c1)]
                            child["st" + str(c1)] = child["st" + str(c2)]
                            child["st" + str(c2)] = temp
                        else:
                            if child["st" + str(c1)]["state"] == "straight":
                                duration_list = np.arange(
                                    cf.model["min_len"],
                                    cf.model["max_len"],
                                    cf.model["len_step"],
                                )
                            else:
                                duration_list = np.arange(
                                    cf.model["min_angle"],
                                    cf.model["max_angle"],
                                    cf.model["ang_step"],
                                )
                            child["st" + str(c1)]["value"] = int(
                                np.random.choice(duration_list)
                            )

                sn.states = child

                sn.get_points()

                sn.remove_invalid_cases()

                sn.novelty = sn.calc_novelty(old_states, sn.states)


                X[i, 0] = sn

        return X
