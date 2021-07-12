from pymoo.model.duplicate import ElementwiseDuplicateElimination


class MyDuplicateElimination(ElementwiseDuplicateElimination):
    def is_equal(self, a, b):
        return a.X[0].states == b.X[0].states
