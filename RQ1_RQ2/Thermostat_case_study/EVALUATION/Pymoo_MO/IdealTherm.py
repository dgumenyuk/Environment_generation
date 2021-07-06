from ExpModel2Cof import ExpModel2Cof
from ModelPool import ModelPool
import config as cf


class Thermostat:
    def __init__(self, smpl_rate, threshold):
        self.ideal_temp_list = []
        self.system_temp_list = []
        # self.init = init_temp
        self.sample_rate = smpl_rate
        self.threshold = threshold
        self.on = ExpModel2Cof(1)
        self.off = ExpModel2Cof(-1)
        self.model_pool = ModelPool(cf.files["models"])

    def read_test_case(self, test_case):
        # print(test_case)
        self.ideal_temp_list = []
        self.system_temp_list = [test_case["st0"]["temp"]]

        for state in test_case:
            self.set_ideal_temp(test_case[state]["temp"], test_case[state]["duration"])
            model = self.model_pool.get_model(test_case[state]["model"])
            self.set_system_temp(
                model, test_case[state]["temp"], test_case[state]["duration"]
            )

        del self.system_temp_list[-1]

    def set_ideal_temp(self, goal_temp, steps):
        current_step = 1
        while current_step <= steps:
            self.ideal_temp_list.append(goal_temp)
            current_step += self.sample_rate
        return

    def set_system_temp(self, model, goal, duration):
        system_time = 1
        system_temp = self.system_temp_list[-1]

        while system_time <= duration:

            start_temp = system_temp

            state_time = self.sample_rate
            # print(goal)

            while (system_temp < (goal + self.threshold)) and system_time <= duration:
                # print("goal", goal)
                system_temp = self.on.next_step(state_time, start_temp, model)

                self.system_temp_list.append(system_temp)
                system_time += self.sample_rate
                state_time += self.sample_rate

            if system_time > duration:
                break

            start_temp = system_temp
            state_time = self.sample_rate

            while (system_temp >= (goal - self.threshold)) and system_time <= duration:
                system_temp = self.off.next_step(state_time, start_temp, model)
                self.system_temp_list.append(system_temp)
                system_time += self.sample_rate
                state_time += self.sample_rate

        return
