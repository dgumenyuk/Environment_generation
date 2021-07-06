'''
Module to convert the model number and type (ON/OFF) to the corresponding coefficient 
'''


import numpy as np


class ExpModel2Cof:
    def __init__(self, mod_type=None):
        self.mod_type = mod_type

    def simulate_steps(self, steps, start_temp, coefficients):
        result = []
        for i in range(1, steps + 1):
            result.append(self.next_step(i, start_temp, coefficients))
        return result

    def next_step(self, current_step, start_temp, coefficients):
        if self.mod_type == 1:
            temp = (
                coefficients["k1_on"]
                * (1 - np.exp(-coefficients["k2_on"] * (current_step)))
                + start_temp
            )
            return temp
        elif self.mod_type == -1:
            temp = (
                coefficients["k1_off"]
                * (np.exp(-coefficients["k2_off"] * current_step))
                + start_temp
                - coefficients["k1_off"]
            )
            return temp
        else:
            raise KeyError("wrong mode...")
