'''
Python script to run all the maps generated for robot and saved in the ".results" folder.
'''


import json
import re
from RDP import rdp
import os
import time


def modify(points, map_name):

    '''
    Funtion to modify the "autonomous_agents", "events" and "stage" files 
    to enter the new pooints and map name.
    '''

    # modifing the points for robot and events
    with open("autonomous_agents.json", "r") as f:
        agents = json.load(f)

    with open("events.json", "r") as f:
        events = json.load(f)

    points_list = []

    for point in points:
        x = point["x"]
        y = point["y"]
        points_list.append([x, y])

    points = rdp(points_list, epsilon=0.5)
    #points = points_list

    routes = []
    p = 0
    while p < len(points):
        p_set = {}
        p_set["x"] = points[p][0]
        p_set["y"] = points[p][1]
        routes.append(p_set)
        p += 1

    agents["agents"]["Autonomous1"]["waypoints"] = routes
    events["events"]["waypoint_arrival"]["agents"]["Autonomous1"] = routes

    with open("autonomous_agents.json", "w") as f:
        json.dump(agents, f, indent=4)

    with open("events.json", "w") as f:
        json.dump(events, f, indent=4)

    # modifying the map name

    with open("stage.world", "r") as f:
        file = f.read()

    file = re.sub(r"(?<=e_/)(.*?)(?=\")", map_name, file)

    with open("stage.world", "w") as f:
        f.write(file)


if __name__ == "__main__":

    '''
    Executes every map in "results" subdirectories and save the 
    execution summary (failed (1) or success (0) to "fails.json" file)
    '''
    base_folder = "./results"
    for directory in os.listdir(base_folder):
        res_folder = os.path.join(base_folder, directory)

        failure_record = {}
        fail_num = 0
        start_time = time.time()
        for folder in os.listdir(res_folder):
            if "fails" not in folder:
                map_path = os.path.join(res_folder, folder)
                test_path = os.path.join(res_folder, folder, "scenarios.json")
                failure_record[str(folder)] = {}
                with open(test_path, "r") as f:
                    all_waypoints = json.load(f)
                    # print(all_waypoints)
                for file in sorted(os.listdir(map_path)):
                    if "png" in file:
                        print(os.path.splitext(file)[0])
                        map_name = os.path.splitext(file)[0]
                        map_name_path = os.path.join(map_path, file)
                        print(map_name_path)

                        waypoints = all_waypoints[map_name]
                        modify(waypoints, map_name_path)

                        print(folder, map_name)
                        os.system("./go.sh")

                        with open("eventdetector.log", "r") as f:
                            data = f.read()

                        if ("loit" in data) or ("stal" in data):
                            failure_record[str(folder)][map_name] = 1
                            fail_num += 1
                        elif "failed" in data:
                            failure_record[str(folder)][map_name] = -1
                        else:
                            failure_record[str(folder)][map_name] = 0

                        with open(
                            os.path.join(map_path, "eventdetector_" + map_name + ".log"),
                            "w",
                        ) as f:
                            f.write(data)

        end_time = time.time()

        failure_record["failures"] = fail_num
        failure_record["total_time"] = (end_time - start_time) / 60

        with open(os.path.join(res_folder, "fails.json"), "w") as f:
            json.dump(failure_record, f, indent=4)

        print("Total time", (end_time - start_time) / 60)

