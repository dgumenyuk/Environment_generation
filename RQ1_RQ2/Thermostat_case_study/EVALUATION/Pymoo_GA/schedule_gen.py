'''
Module to generate random schedules
'''


import numpy as np
import random as rm
import json
import os


class ScheduleGen:
    """Class for generating thermostat"""

    def __init__(
        self,
        min_temp,  # minimal possible temperature in tc
        max_temp,  # maximal possible temperature in tc
        max_jump,  # biggest possible change in temperature
        min_interval_duration,  # minimal duration of a state (dividable by 10)
        max_interval_duration,  # maximal duration of a state (dividable by 10)
        model_num,
    ):
        self.file = "schedules2.json"
        self.init_states = ["inc_tmp", "dec_tmp"]

        self.model_num = model_num

        self.transitionName = [["S1S1", "S1S2"], ["S2S1", "S2S2"]]

        self.transitionMatrix = [
            [0.3, 0.7],
            [0.7, 0.3],
        ]  # probabilities of switching states

        self.time = 0  # counter of the total tc duration
        self.states = []

        self.max_time = (
            480  # maximal duration of the tc in time units - 1 time unit is 3 min
        )

        self.min_temp = min_temp
        self.max_temp = max_temp

        self.min_step = min_interval_duration
        self.max_step = max_interval_duration
        self.max_jump = max_jump  # maximal difference between temperatures in the tc

        self.step_values = self.define_intervals()  # a list of duration values

    def get_temp_inc(self, temp):
        """Function to produce the next value for
        increasing the temperature"""
        if temp + self.max_jump > self.max_temp:
            result = rm.randint(temp, self.max_temp)
        else:
            result = rm.randint(temp, temp + self.max_jump)
        return result

    def get_temp_dec(self, temp):
        """Function to produce the next value for
        decreasing the temperature"""
        if temp - self.max_jump < self.min_temp:
            result = rm.randint(self.min_temp, temp)
        else:
            result = rm.randint(temp - self.max_jump, temp)
        return result

    def define_intervals(self):
        """Function for generating state duration
        vales"""
        i = 5  # a step of increment
        interval_sum = self.min_step
        interval_list = [self.min_step]
        while interval_sum < self.max_step:
            interval_sum += i
            interval_list.append(interval_sum)
        # interval_list.append(self.max_step)
        # print("Intervals", interval_list)
        return interval_list

    def test_case_generate(self):
        """Function that produces triplets of
        states"""

        # initialization
        state = np.random.choice(self.init_states)
        model = rm.randint(0, self.model_num - 1)
        duration = np.random.choice(self.step_values)
        temp = rm.randint(self.min_temp, self.max_temp)

        self.states = [[model, duration, temp]]
        self.time = duration

        while self.time < self.max_time:
            if state == "inc_tmp":
                change = np.random.choice(
                    self.transitionName[0], p=self.transitionMatrix[0]
                )  # choose the next state
                if change == "S1S1":  # stay in the same state
                    temp = self.get_temp_inc(temp)
                    model = rm.randint(0, self.model_num - 1)
                    diff = (
                        self.max_time - self.time
                    )  # this is for ensuring the maximum duration is not exceeded
                    if (diff) < self.max_step and (diff) > self.min_step:
                        duration = diff
                        self.states.append([model, duration, temp])
                        return self.states_to_dict()
                    elif diff < self.min_step:
                        self.states[len(self.states) - 1][1] += diff
                        return self.states_to_dict()
                    else:
                        duration = np.random.choice(self.step_values)
                    self.time += duration
                    self.states.append([model, duration, temp])

                elif change == "S1S2":  # change from increase to decrease
                    temp = self.get_temp_dec(temp)
                    model = rm.randint(0, self.model_num - 1)
                    state = "dec_tmp"

                    diff = self.max_time - self.time
                    if (diff) < self.max_step and (diff) > self.min_step:
                        duration = diff
                        self.states.append([model, duration, temp])
                        return self.states_to_dict()
                    elif diff < self.min_step:
                        self.states[len(self.states) - 1][1] += diff
                        return self.states_to_dict()
                    else:
                        duration = np.random.choice(self.step_values)
                    self.time += duration
                    self.states.append([model, duration, temp])
                else:
                    print("Error")

            elif state == "dec_tmp":
                change = np.random.choice(
                    self.transitionName[1], p=self.transitionMatrix[1]
                )
                if change == "S2S1":
                    temp = self.get_temp_inc(temp)
                    model = rm.randint(0, self.model_num - 1)
                    state = "inc_tmp"
                    diff = self.max_time - self.time
                    if (diff) < self.max_step and (diff) > self.min_step:
                        duration = diff
                        self.states.append([model, duration, temp])
                        return self.states_to_dict()
                    elif diff < self.min_step:
                        self.states[len(self.states) - 1][1] += diff
                        return self.states_to_dict()
                    else:
                        duration = np.random.choice(self.step_values)

                    self.time += duration
                    self.states.append([model, duration, temp])

                elif change == "S2S2":
                    temp = self.get_temp_dec(temp)
                    model = rm.randint(0, self.model_num - 1)

                    diff = self.max_time - self.time
                    if (diff) < self.max_step and (diff) > self.min_step:
                        duration = diff
                        self.states.append([model, duration, temp])
                        return self.states_to_dict()
                    elif diff < self.min_step:
                        self.states[len(self.states) - 1][1] += diff
                        return self.states_to_dict()
                    else:
                        duration = np.random.choice(self.step_values)
                    self.time += duration
                    self.states.append([model, duration, temp])

                else:
                    print("Error")
                    pass
            else:
                print("Error")

        return self.states_to_dict()

    def states_to_dict(self):
        """Transforms a list of test cases
        to a dictionary"""
        test_cases = {}
        i = 0
        for element in self.states:
            test_cases["st" + str(i)] = {}
            test_cases["st" + str(i)]["model"] = int(element[0])
            test_cases["st" + str(i)]["duration"] = int(element[1])
            test_cases["st" + str(i)]["temp"] = int(element[2])
            i += 1

        return test_cases

    def write_states_to_file(self):
        """Writes the generated test case to file"""
        if os.stat(self.file).st_size == 0:
            test_cases = {}
        else:
            with open(self.file) as file:
                test_cases = json.load(file)

        num = len(test_cases)

        tc = "tc" + str(num)
        test_cases[tc] = {}
        i = 0
        for element in self.states:
            test_cases[tc]["st" + str(i)] = {}
            test_cases[tc]["st" + str(i)]["model"] = int(element[0])
            test_cases[tc]["st" + str(i)]["duration"] = int(element[1])
            test_cases[tc]["st" + str(i)]["temp"] = int(element[2])
            i += 1

        with open(self.file, "w") as outfile:
            json.dump(test_cases, outfile)

    def check_states(self):
        total_dur = 0
        for state in self.states:
            total_dur += state[1]
        print("TC total duration:", total_dur)
        return total_dur


if __name__ == "__main__":

    # steps = [5, 6, 7]
    i = 0
    while i < 10:  # generate N number of schedules
        print("generating test case" + str(i))
        # num = rm.randint(5, 12)
        schedule = ScheduleGen(16, 25, 5, 20, 80)
        x = schedule.test_case_generate()
        # print(schedule.define_intervals())
        # print(schedule.states)
        schedule.check_states()
        print(x)
        i += 1
        # schedule.write_states_to_file()
