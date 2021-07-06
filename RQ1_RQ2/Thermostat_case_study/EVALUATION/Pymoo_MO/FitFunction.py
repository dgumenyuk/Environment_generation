import numpy as np


class FitFunction:
    def __init__(self):

        pass

    def calculate_rms(self, ideal_temp, system_temp):
        if len(ideal_temp) > len(system_temp):
            system_temp.append(system_temp[len(system_temp) - 1])
            print("L1>L2")
        if len(ideal_temp) < len(system_temp):
            ideal_temp.append(ideal_temp[len(ideal_temp) - 1])
            print("L1<L2")
        return np.sqrt(((np.array(ideal_temp) - np.array(system_temp)) ** 2).mean())
