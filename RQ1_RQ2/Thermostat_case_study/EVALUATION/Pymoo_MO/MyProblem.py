from pymoo.model.problem import Problem


from multiprocessing.pool import ThreadPool


class MyProblem(Problem):
    def __init__(self, **kwargs):
        super().__init__(
            n_var=1, n_obj=2, n_constr=1, elementwise_evaluation=True, **kwargs
        )


    def _evaluate(self, x, out, *args, **kwargs):
        s = x[0]

        s.eval_fitness()
        out["F"] = [s.fitness, s.novelty]
        out["G"] = 1.5 - s.fitness * (-1)  #  restriction on fitness values (only lower than -1.5)
