import numpy as np
from pymoo.model.crossover import Crossover
from Solution import Solution
import random as rm


class MyTcCrossover(Crossover):
    def __init__(self):

        # define the crossover: number of parents and number of offsprings
        super().__init__(2, 2)

    def _do(self, problem, X, **kwargs):

        _, n_matings, n_var = X.shape
        # print("X cross shape", X.shape)

        # The output owith the shape (n_offsprings, n_matings, n_var)
        # Because there the number of parents and offsprings are equal it keeps the shape of X
        Y = np.full_like(X, None, dtype=np.object)

        # for each mating provided
        for k in range(n_matings):

            # get the first and the second parent
            s_a, s_b = X[0, k, 0], X[1, k, 0]

            tc_a = s_a.states
            tc_b = s_b.states

            s_a.eval_fitness()
            s_b.eval_fitness()


            # find the crossover point

            if len(tc_a) < len(tc_b):
                crossover_point = rm.randint(1, len(tc_a) - 1)
            elif len(tc_b) < len(tc_a):
                crossover_point = rm.randint(1, len(tc_b) - 1)
            else:
                crossover_point = rm.randint(1, len(tc_a) - 1)

            #  we need at least two states to do crossover

            if len(s_a.states) > 2 and len(s_b.states) > 2:


                # create two empty solutions
                off_a = Solution()
                off_b = Solution()

                for i in range(0, crossover_point):
                    off_a.states["st" + str(i)] = tc_a["st" + str(i)]
                    off_b.states["st" + str(i)] = tc_b["st" + str(i)]
                for i in range(crossover_point, len(tc_b)):
                    off_a.states["st" + str(i)] = tc_b["st" + str(i)]
                for i in range(crossover_point, len(tc_a)):
                    off_b.states["st" + str(i)] = tc_a["st" + str(i)]
                #

                off_a.states = off_a.check_states()
                off_b.states = off_b.check_states()
                off_a.novelty = off_a.calc_novelty(tc_a, off_a.states)
                off_b.novelty = off_b.calc_novelty(tc_b, off_b.states)
            else:

                off_a.novelty = off_a.calc_novelty(tc_a, off_a.states)
                off_b.novelty = off_b.calc_novelty(tc_b, off_b.states)
                print("Not enough states!")

            Y[0, k, 0], Y[1, k, 0] = off_a, off_b

        return Y
