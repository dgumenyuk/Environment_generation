from code_pipeline.tests_generation import RoadTestFactory
from time import sleep
from swat_gen.road_gen import RoadGen
import logging as log
from code_pipeline.validation import TestValidator
from code_pipeline.tests_generation import RoadTestFactory
from scipy.interpolate import splprep, splev, interp1d, splrep
from shapely.geometry import  LineString, Point, GeometryCollection
from numpy.ma import arange
from swat_gen.Solution import Solution
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

        #road = RoadGen(self.map_size, 5, 30, 10, 80)

        while self.executor.get_remaining_time() > 0:
            # Some debugging
            log.info(
                "Starting test generation. Remaining time %s",
                self.executor.get_remaining_time(),
            )

            # generate the road points. 
            # class input values correspond to maximum distance to go stright and rotation angle
            #points = road.test_case_generate()
            
            #points = interpolate_road(road.road_points)
            #points = remove_invalid_cases(points, self.map_size)
            #
            
            points = evaluate_random(self.map_size)
            '''
            for tc in points:
                tc = remove_invalid_cases(tc, self.map_size)

                the_test = RoadTestFactory.create_road_test(tc)
            '''
            points = remove_invalid_cases(points, self.map_size)
            #

            # Some more debugging
            #log.info("Generated test using: %s", points)
            #the_test = RoadTestFactory.create_road_test(road.road_points)
            the_test = RoadTestFactory.create_road_test(points)

            # Try to execute the test
            test_outcome, description, execution_data = self.executor.execute_test(
                the_test
            )

            # Print the result from the test and continue
            log.info("test_outcome %s", test_outcome)
            log.info("description %s", description)

            if self.executor.road_visualizer:
                sleep(5)




def evaluate_random(map_size):
    fit_list = []
    generator = RoadGen(map_size, 5, 50, 10, 80)
    minimum = 0
    for i in range((5090)):
        states = generator.test_case_generate()
        s = Solution()
        #s.road_points = road_points
        s.states = states

        s.get_points()
        s.remove_invalid_cases()
        s.eval_fitness()
        #print(s.fitness)
        if s.fitness < minimum:
            minimum = s.fitness
            points = s.intp_points
            #fit_list.append(points)

    #return fit_list[-5:]
    return points

def interpolate_road(road):
    #road.sort()
    #print(road)
    test_road = LineString([(t[0], t[1]) for t in road])

    length = test_road.length

    #print("Length", length)

    old_x_vals = [t[0] for t in road]
    old_y_vals = [t[1] for t in road]

    if len(old_x_vals) == 2:
    # With two points the only option is a straight segment
        k = 1
    elif len(old_x_vals) == 3:
    # With three points we use an arc, using linear interpolation will result in invalid road tests
        k = 2
    else:
    # Otheriwse, use cubic splines
        k = 3
    f2, u = splprep([old_x_vals, old_y_vals], s=0, k=k)


    step_size = 1 / (length) * 10
    xnew = arange(0, 1 + step_size, step_size) 

    x2, y2 = splev(xnew, f2)

    nodes = list(zip(x2,y2))

    return nodes


def remove_invalid_cases(points, map_size):
    new_list = []
    i = 0
    while i < len(points):
        if point_in_range_2(points[i], map_size) == 1:
            new_list.append(points[i])
        else:
            return new_list
        i+=1

    return new_list


def point_in_range_2(a, map_size):
    """check if point is in the acceptable range"""
    if ((0 + 4) < a[0] and a[0] < (map_size- 4)) and ((0 +4) < a[1] and a[1] < (map_size - 4)):
        return 1
    else:
        return 0

if __name__ == "__main__":
    tests = SwatTestGenerator(time_budget=250000, executor="mock", map_size=200)
    tests.start()
