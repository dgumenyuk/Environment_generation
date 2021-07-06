
from pymoo.model.problem import Problem


class MyProblem(Problem):
    def __init__(self):
        super().__init__(n_var=1, n_obj=2, n_constr=1, elementwise_evaluation=True)

    def _evaluate(self, x, out, *args, **kwargs):
        #print("Evaluation")

        s = x[0]
        s.eval_fitness()
        out["F"] = [s.fitness, s.novelty]
        out["G"] = 120 - s.fitness*(-1)
