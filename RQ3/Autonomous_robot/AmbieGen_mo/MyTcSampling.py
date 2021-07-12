import numpy as np
from pymoo.model.sampling import Sampling
from Solution import Solution

from room_gen import MapGen

import config as cf
class MyTcSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):

        generator = MapGen(cf.model["map_size"], cf.model["min_len"], cf.model["max_len"], cf.model["len_step"], cf.model["pos_step"])
        X = np.full((n_samples, 1), None, dtype=np.object)

        for i in range(n_samples):
            map_points, states = generator.test_case_generate()
            s = Solution()
            s.map_points = map_points
            s.states = states

            # print("STATES", states)
            #print("POINTS", s.map_points)
            X[i, 0] = s

        return X
 