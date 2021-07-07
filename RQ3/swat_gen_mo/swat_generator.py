from code_pipeline.tests_generation import RoadTestFactory
from time import sleep
from swat_gen.road_gen import RoadGen
import logging as log
from code_pipeline.validation import TestValidator
import swat_gen.Optimize as optim

import json
class SwatTestGenerator:
    """
    This simple test generator creates roads using affine tratsformations of vectors.
    To generate the sequences of action, e.g "go straight", "turn right", "turn left"
    a Markov chain used.
    This generator can quickly create a number of tests, however their fault revealing power
    isn't optimized and the roads can intersect.
    """

    def __init__(self, time_budget=None, executor=None, map_size=None):
        self.map_size = map_size
        self.time_budget = time_budget
        self.executor = executor

    def start(self):


        #with open("generation_49.json") as f:
        while self.executor.get_remaining_time() > 0:
        
            cases = optim.optimize()

            for case in cases:


                # Some debugging
                log.info(
                    "Starting test generation. Remaining time %s",
                    self.executor.get_remaining_time(),
                )

                # generate the road points. 
                # class input values correspond to maximum distance to go stright and rotation angle
                #road = RoadGen(self.map_size, 5, 50, 10, 70)
                #road.test_case_generate()

                #the_test = RoadTestFactory.create_road_test(road.road_points)



                the_test = RoadTestFactory.create_road_test(cases[case])
                #the_test = RoadTestFactory.create_road_test( [(10.000000000000002, 120.0), (17.151072407833222, 128.72047158684998), (26.258629231436576, 131.2339846963721), (36.7099854366325, 129.57961671050728), (47.89245598924342, 125.7964450111964), (59.19335585509179, 121.92354698038034), (70.0, 120.0), (79.7129055298604, 122.01619016696736), (88.77557600746688, 126.1246316358691), (98.4590729891444, 127.87261296798465), (108.76448038078044, 128.1409033709342), (119.46834303168887, 128.29827905903466), (129.68008658207347, 129.8103071467211), (138.25988103340273, 134.178718716282), (144.12335459356453, 142.30952995696518), (146.4362587202482, 152.44242691421562), (144.76618912154007, 162.35748206028032), (140.48634959177386, 171.4199029949029), (135.33262219444845, 179.9865577124887), (130.33265114800628, 188.6467302148469), (125.16067219004356, 197.26066653891561), (120.94028748866391, 206.13935317303697), (119.2736530619402, 215.7649251451143), (121.76292492960306, 226.61951748364376)])
    #leads to failure
    #[[10.0, 120.0], [38.19077862357725, 139.73939570022995], [45.03118149009064, 158.5332481159481], [48.64739878499814, 165.47993690670944], [78.43140544367583, 177.81687640654422], [104.85405420928015, 186.14790556131402], [120.85781231486871, 194.4789347160838], [150.64181897354632, 182.14199521624883], [172.6017080197863, 169.4634473640278]]
    #[[10.0, 120.0], [14.688500797007123, 120.41019066867038], [36.73226705555081, 114.50358130155317], [43.847311844003784, 105.23107440433964], [43.847311844003784, 82.40968827034187], [37.508037917893276, 68.81507146479213], [24.448420734902594, 55.75545428180148], [8.961856953424322, 33.638349085998726], [24.448420734902523, 6.814833781822385], [33.50590874771463, 4.387887183334788]]
                # Some more debugging
                #log.info("Generated test using: %s", road.road_points)
                #the_test = RoadTestFactory.create_road_test(road.road_points)

                # Try to execute the test
                test_outcome, description, execution_data = self.executor.execute_test(
                    the_test
                )

                # Print the result from the test and continue
                log.info("test_outcome %s", test_outcome)
                log.info("description %s", description)

                if self.executor.road_visualizer:
                    sleep(5)


if __name__ == "__main__":
    tests = SwatTestGenerator(time_budget=250000, executor="mock", map_size=200)
    tests.start()
