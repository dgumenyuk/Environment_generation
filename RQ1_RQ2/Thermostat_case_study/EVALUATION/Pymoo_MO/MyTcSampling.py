import numpy as np
from pymoo.model.sampling import Sampling
from Solution import Solution
import config as cf
from schedule_gen import ScheduleGen


class MyTcSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        schedules = ScheduleGen(
            cf.model["temp_min"],
            cf.model["temp_max"],
            cf.model["jump"],
            cf.model["duration_min"],
            cf.model["duration_max"],
            cf.model["model_num"],
        )

        X = np.full((n_samples, 1), None, dtype=np.object)

        for i in range(n_samples):
            schedule = schedules.test_case_generate()
            s = Solution()
            s.states = schedule

            X[i, 0] = s

        return X
