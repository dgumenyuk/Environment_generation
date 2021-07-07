import numpy as np
from pymoo.model.crossover import Crossover
from swat_gen.Solution import Solution
import random as rm
from scipy.spatial.distance import directed_hausdorff
import copy
class MyTcCrossover(Crossover):
    def __init__(self, cross_rate):

        # define the crossover: number of parents and number of offsprings
        super().__init__(2, 2)
        self.cross_rate = cross_rate

    def _do(self, problem, X, **kwargs):
        #print("CROSS")
        #print()
        # print("X cross shape", X.shape)
        # The input of has the following shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape
        #print("Number of mationgs", n_matings)
        #print("X cross shape", X.shape)

        # The output owith the shape (n_offsprings, n_matings, n_var)
        # Because there the number of parents and offsprings are equal it keeps the shape of X
        Y = np.full_like(X, None, dtype=np.object)

        # for each mating provided

        for k in range(n_matings):

            r = np.random.random()


            # get the first and the second parent
            s_a, s_b = X[0, k, 0], X[1, k, 0]
                #s_a = copy.deepcopy(sa)
                #s_b = copy.deepcopy(sb)


            
            s_a.get_points()
            #print("sa_road_before", s_a.road_points)
            #print("sa_state_before", s_a.states)
            s_a.remove_invalid_cases()
            #print("sa_road_after", s_a.road_points)
            #print("sa_state_after", s_a.states)

            s_b.get_points()
            #print("sb_road_before", s_b.road_points)
            #print("sb_state_before", s_b.states)
            s_b.remove_invalid_cases()
            #print("sb_road_after", s_b.road_points)
            #print("sb_state_before", s_b.states)

            if r < self.cross_rate:



                tc_a = s_a.states
                tc_b = s_b.states

                old_points_a = s_a.road_points
                old_points_b = s_b.road_points


                #print("Par A", tc_a)
                #print("Par B", tc_b)
                #s_a.eval_fitness()
                #s_b.eval_fitness()
                #print("fitness a", s_a.fitness) 
                #print("fitness b", s_b.fitness)
                if len(tc_a) < len(tc_b):
                    crossover_point = rm.randint(1, len(tc_a)-1)
                elif len(tc_b) < len(tc_a):
                    crossover_point = rm.randint(1, len(tc_b)-1)
                else:
                    crossover_point = rm.randint(1, len(tc_a)-1)
                #
                # we need to have 2 or more queens to do mating  or it makes no sense
                # the problem is the X-over can choose a sub-set of rows where there is no queen
                #
                # I should do better for now just check we have enough queens in both boards
                #
                if s_a.n_states > 2 and s_b.n_states > 2:

                    # cut point

                    # x_cross = random.randint(0, s_a.board_size - 1)

                    # create two empty solutions

                    offa = {}
                    offb = {}



                    # one point crossover

                    
                    
                    for i in range(0, crossover_point):
                        offa["st" + str(i)] = tc_a["st" + str(i)]
                        offb["st" + str(i)] = tc_b["st" + str(i)]
                    for m in range(crossover_point, len(tc_b)):
                        #print("A", m)
                        #print(i)
                        offa["st" + str(m)] = tc_b["st" + str(m)]
                    for n in range(crossover_point, len(tc_a)):
                        #print("B", n)
                        #print(i)
                        offb["st" + str(n)] = tc_a["st" + str(n)]
                        #print(off_b.states["st" + str(n)])
                    
                    
                    


                                       

                    
                    '''
                    if len(tc_a) <= len(tc_b):
                        smaller = tc_a
                    else:
                        smaller = tc_b

                    for i in range(0, len(smaller)):
                        offa["st" + str(i)] = np.random.choice([ tc_a["st" + str(i)],tc_b["st" + str(i)] ])

                    for i in range(0, len(smaller)):
                        offb["st" + str(i)] = np.random.choice([ tc_a["st" + str(i)],tc_b["st" + str(i)] ])

                    '''

                    
                    
                    
                    


                    #
                    # rebuild placement now
                    #
                    off_a = Solution()
                    off_b = Solution()

                    off_a.states = offa
                    off_b.states = offb


                    # fill the kids  and set the output
                    #Y[0, k, 0], Y[1, k, 0] = off_a, off_b
                    #print("Off a", off_a.states)
                else:
                    # if we do not have enough queen createv 2 new solutions .... I know is not the best !
                    print("Not enough states!")

                
                '''

                print("Cross_start**********************")
                print("X cross shape", X.shape)
                print("Par_A", tc_a, "len", len(tc_a))
                print("Par_B", tc_b, "len", len(tc_b))
                print("Cross point", crossover_point)
                print("OFF_A", off_a.states)
                print("OFF_B", off_b.states)
                print("Cross_end*********************")
                '''
                #print("CROSS")

                off_a.get_points()
                off_a.remove_invalid_cases()
                new_points_a = off_a.road_points
                #off_a.novelty = -max(directed_hausdorff(old_points_a, new_points_a)[0], directed_hausdorff(old_points_a, new_points_a)[0])
                off_a.novelty = off_a.calc_novelty(tc_a, off_a.states)

                #off_b.road_points = off_b.road_builder.get_points_from_states(off_b.states)
                #off_b.states, off_b.road_points = off_b.road_builder.remove_invalid_cases(off_b.road_points, off_b.states)

                off_b.get_points()
                off_b.remove_invalid_cases()
                new_points_b = off_b.road_points
                #off_b.novelty = -max(directed_hausdorff(old_points_b, new_points_b)[0], directed_hausdorff(old_points_b, new_points_b)[0])
                off_b.novelty = off_b.calc_novelty(tc_b, off_b.states)


            #print("STATES", self.states)




            #off_a.eval_fitness()
            #off_b.eval_fitness()

                Y[0, k, 0], Y[1, k, 0] = off_a, off_b

            else:
                Y[0, k, 0], Y[1, k, 0] = s_a, s_b


        return Y



