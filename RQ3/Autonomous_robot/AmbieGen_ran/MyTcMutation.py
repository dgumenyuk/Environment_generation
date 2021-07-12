import numpy as np
from pymoo.model.mutation import Mutation
import copy
import config as cf


class MyTcMutation(Mutation):
    def __init__(self, mut_rate):
        super().__init__()
        self.mut_rate = mut_rate

    def _do(self, problem, X, **kwargs):

        for i in range(len(X)):
            r = np.random.random()
            s = X[i, 0]

            # with a probabilty of 40% - change the order of characters
            if r < self.mut_rate:  # cf.ga["mut_rate"]:
                #
                # for some reason it seems we must do a deep copy
                # and replace the original object
                # pymoo seems to keep a deep copy of the best object if I change it
                # in a mutation it will not chnage pymoo best individual and we end up
                # with an incosistency in evaluated fitnesses
                sn = copy.deepcopy(s)

                wr = np.random.random()
                child = sn.states
                old_states = child
                if wr < 0.2:
                    candidates = list(np.random.randint(0, high=len(child), size=2))
                    temp = child["st" + str(candidates[0])]
                    child["st" + str(candidates[0])] = child["st" + str(candidates[1])]
                    child["st" + str(candidates[1])] = temp
                elif wr >= 0.2 and wr < 0.6:
                    num = np.random.randint(0, high=len(child))
                    value = np.random.choice(["state", "value", "position"])

                    if value == "value":
                        duration_list = [
                            i
                            for i in range(
                                cf.model["min_len"],
                                cf.model["max_len"] + 1,
                                cf.model["len_step"],
                            )
                        ]
                        child["st" + str(num)][value] = int(
                            np.random.choice(duration_list)
                        )
                    elif value == "state":
                        if child["st" + str(num)][value] == "horizontal":
                            child["st" + str(num)][value] = "vertical"
                        else:
                            child["st" + str(num)][value] = "horizontal"
                    elif value == "position":
                        duration_list = [
                            i
                            for i in range(
                                cf.model["min_len"],
                                cf.model["map_size"] - cf.model["min_len"],
                                cf.model["pos_step"],
                            )
                        ]
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
                            duration_list = [
                                i
                                for i in range(
                                    cf.model["min_len"],
                                    cf.model["max_len"] + 1,
                                    cf.model["len_step"],
                                )
                            ]
                            child["st" + str(num)][value] = int(
                                np.random.choice(duration_list)
                            )

                sn.states = child

                sn.get_points()

                sn.novelty = sn.calc_novelty(old_states, sn.states)
                X[i, 0] = sn

        return X
