
from pymoo.model.problem import Problem


class MyProblem(Problem):
    def __init__(self):
        super().__init__(n_var=1, n_obj=2, n_constr=1, elementwise_evaluation=True)

    def _evaluate(self, x, out, *args, **kwargs):
        #print("Evaluation")

        s = x[0]
        s.eval_fitness()
        #print(s.fitness)
        #print("Eval %s fitness %f" %(str(s.states), s.fitness))
        #print("novelty", s.novelty)
        out["F"] = [ s.fitness, s.novelty]
        #out["F"] = s.fitness
        #out["G"] = 5-s.fitness*(-1)
        out["G"] = 0.8-s.fitness*(-1)
