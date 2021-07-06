import numpy as np

from robot_map import Map

from a_star import AStarPlanner
import matplotlib.pyplot as plt

from dynamic_window_approach import main
class MapGen:
    """Class for generating roads"""

    def __init__(
        self,
        map_size,
        min_len,  # minimal possible distance in meters
        max_len,  # maximal possible disance to go straight in meters
        step_pos,
        step_len

    ):

        self.map_points = []
        self.init_states = ["horizontal", "vertical"]

        self.map_size = map_size


        # state matrix
        self.transitionName = [
            ["HH", "HV"],
            ["VH", "VV"]
        ]

        self.transitionMatrix = [
            [0.5, 0.5],
            [0.5, 0.5]
        ]  # probabilities of switching states



        self.min_len = min_len
        self.max_len = max_len
        self.step_pos = step_pos
        self.step_len = step_len

        self.min_pos = 1
        self.max_pos = map_size - 1

        self.len_values = [
            i for i in range(self.min_len, self.max_len + 1, self.step_len)
        ]  # a list of distance to go forward
        self.pos_values = [
            i for i in range(self.min_pos, self.max_pos + 1, self.step_pos)
        ]  # a list of angles to turn



    def test_case_generate(self): 
        """Function that produces a list with states and road points"""

        # initialization

        self.map_points = []

        self.robot_map = Map(self.map_size)


        state = np.random.choice(self.init_states)
        value = np.random.choice(self.len_values)
        position = np.random.choice(self.pos_values)


        if state == "horizontal":
            new_points = self.robot_map.horizontal(value, position)
            self.map_points.append(new_points)
        elif state == "vertical":
            new_points = self.robot_map.vertical(value, position)
            self.map_points.append(new_points)
        else:
            print("Invalid state")


        self.states = [[state, value, position]]

        for i in range(1, self.map_size - 1):
            #self.robot_map.current_level = i
            if state == "horizontal":
                change = np.random.choice(
                    self.transitionName[0], p=self.transitionMatrix[0]
                )  # choose the next state
                if change == "HH":  # stay in the same state
                    value = np.random.choice(self.len_values)
                    position = np.random.choice(self.pos_values)
                    self.states.append([state, value, position])
                    new_points = self.robot_map.horizontal(value, position)
                    self.map_points.append(new_points)
                elif change == "HV":  # change from go straight to turn left
                    state = "vertical"
                    value = np.random.choice(self.len_values)
                    position = np.random.choice(self.pos_values)
                    self.states.append([state, value, position])
                    new_points = self.robot_map.vertical(value, position)
                    self.map_points.append(new_points)

            elif state == "vertical":
                change = np.random.choice(
                    self.transitionName[1], p=self.transitionMatrix[1]
                )
                if change == "VH":
                    state = "horizontal"
                    value = np.random.choice(self.len_values)
                    position = np.random.choice(self.pos_values)
                    self.states.append([state, value, position])
                    new_points = self.robot_map.horizontal(value, position)
                    self.map_points.append(new_points)
                elif change == "VV":
                    value = np.random.choice(self.len_values)
                    position = np.random.choice(self.pos_values)
                    self.states.append([state, value, position])
                    new_points = self.robot_map.vertical(value, position)
                    self.map_points.append(new_points)

        return self.robot_map.all_map_points, self.states_to_dict()




    def states_to_dict(self):
        """Transforms a list of test cases
        to a dictionary"""
        test_cases = {}
        i = 0
        for element in self.states:
            test_cases["st" + str(i)] = {}
            test_cases["st" + str(i)]["state"] = element[0]
            test_cases["st" + str(i)]["value"] = element[1]
            test_cases["st" + str(i)]["position"] = element[2]
            i += 1

        map_points = {}
        i = 0
        for element in self.map_points:
            map_points["st" + str(i)] = element
            i += 1

        return test_cases
if __name__ == "__main__":

    # steps = [5, 6, 7]
    i = 0
    road = MapGen(50, 4, 10, 1, 1)
    points, states = road.test_case_generate()

    print(states)

    ox = [t[0] for t in points]
    oy = [t[1] for t in points]

    sx = 1.0  # [m]
    sy = 1.0  # [m]
    gx = 47.0  # [m]
    gy = 47.0  # [m]

    grid_size = 1  # [m]
    robot_radius = 0.5  # [m]

    plt.plot(ox, oy, ".k")
    plt.plot(sx, sy, "og")
    plt.plot(gx, gy, "xb")
    plt.grid(True)
    plt.axis("equal")

    a_star = AStarPlanner(ox, oy, grid_size, robot_radius)
    rx, ry, time = a_star.planning(sx, sy, gx, gy)

    print("Total_time", time)

    plt.plot(rx, ry, "-r")

    plt.show()

