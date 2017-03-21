from functools import partial, partialmethod

from deap.tools import selNSGA2, selBest
import numpy as np

from glyph.gp.individual import AExpressionTree, ANDimTree, numpy_primitive_set, numpy_phenotype, nd_phenotype
from glyph.gp.breeding import cxonepoint, nd_crossover, mutuniform, nd_mutation
from glyph.gp.algorithms import AgeFitness
from glyph.utils.numeric import rmse


pset = numpy_primitive_set(1, categories=('algebraic', 'symc'))
MyTree = type("MyTree", (AExpressionTree,), dict(pset=pset))
MyNDTree = type("MyNDTree", (ANDimTree,), dict(base=MyTree))
MyNDTree.create_population = partialmethod(MyNDTree.create_population, ndim=2)


def target(x):
    return np.array([f(x) for f in [lambda x: x**2, lambda x: x]])

x = np.linspace(-1, 1, 30)
y = target(x)


def evaluate_(individual, x, y):
    func = nd_phenotype(individual, backend=numpy_phenotype)
    yhat = func(x)
    for i in range(len(yhat)):
        if np.isscalar(yhat[i]):
            yhat[i] = np.ones_like(y[i]) * yhat[i]
    yhat = np.array(yhat)
    return rmse(yhat, y),

evaluate = partial(evaluate_, x=x, y=y)


def update_fitness(population):
    invalid = [p for p in population if not p.fitness.valid]
    fitnesses = map(evaluate, invalid)
    for ind, fit in zip(invalid, fitnesses):
        ind.fitness.values = fit
    return population


def main():
    pop_size = 100
    mutate = partial(nd_mutation, mut1d=mutuniform(pset=pset))
    mate = partial(nd_crossover, cx1d=cxonepoint())

    algorithm = AgeFitness(mate, mutate, selNSGA2, MyNDTree.create_population)

    pop = update_fitness(MyNDTree.create_population(pop_size))

    for gen in range(20):
        pop = algorithm.evolve(pop)
        pop = update_fitness(pop)
        best = selBest(pop, 1)[0]
        print(best, best.fitness.values)


if __name__ == "__main__":
    main()
