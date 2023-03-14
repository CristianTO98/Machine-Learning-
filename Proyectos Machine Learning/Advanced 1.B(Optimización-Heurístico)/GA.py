import numpy as np
import random
import math


def distance(gen_a, gen_b):
    return math.dist(gen_a[0:2], gen_b[0:2])


def euclidean(individual):
    i = 0
    total_distance = 0
    while i < len(individual) - 1:
        actual, nextt = individual[i], individual[i + 1]
        total_distance += distance(actual, nextt)
        i += 1
    total_distance += distance(individual[0],
                               individual[len(individual) - 1])
    return total_distance


def select_by_tournament(population, tournament_size, fitness_function):
    tournament = random.sample(population, tournament_size)
    individual = min(tournament, key=fitness_function)
    return individual


def crossover_two_points(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []

    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))

    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])

    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child


def mutate(individual, mutationRate, **params):
    for swapped in range(len(individual)):
        if (random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))

            city1 = individual[swapped]
            city2 = individual[swapWith]

            individual[swapped] = city2
            individual[swapWith] = city1
    return individual


def mutate_max_range(individual, mutationRate, **params):
    for swapped in range(len(individual)):
        if (random.random() < mutationRate):
            chosen = int(random.random() * params['max_range'])
            if random.random() < 0.5:
                swapWith = (swapped - chosen) % len(individual)
            else:
                swapWith = (swapped + chosen) % len(individual)

            city1 = individual[swapped]
            city2 = individual[swapWith]

            individual[swapped] = city2
            individual[swapWith] = city1
    return individual


def mutate_inverse_generation(individual, mutationRate, **params):
    max_range = params['generation'] / params['max_generations']
    for swapped in range(len(individual)):
        if (random.random() < mutationRate):
            chosen = int(random.random() * max_range)
            if random.random() < 0.5:
                swapWith = (swapped - chosen) % len(individual)
            else:
                swapWith = (swapped + chosen) % len(individual)

            city1 = individual[swapped]
            city2 = individual[swapWith]

            individual[swapped] = city2
            individual[swapWith] = city1
    return individual


def mutate_opt_2(individual, mutationRate, **params):
    if random.random() > mutationRate:
        return individual

    r1 = random.randint(0, len(individual)-1)
    while True:
        r2 = random.randint(0, len(individual)-1)
        if r1 != r2:
            break
    return individual[:r1] + list(reversed(individual[r1:r2])) + individual[r2:]


def mutate_opt_3(individual, mutationRate, **params):
    if random.random() > mutationRate:
        return individual

    while True:
        i = random.randint(0, len(individual)-3)
        j = random.randint(i+1, len(individual)-2)
        k = random.randint(j+1, len(individual)-1)
        if i != j & j != k & k != i:
            break
    new_individual = individual.copy()
    A, B, C, D, E, F = new_individual[i-1], new_individual[i], new_individual[j -
                                                                              1], new_individual[j], new_individual[k-1], new_individual[k % len(new_individual)]
    d0 = distance(A, B) + distance(C, D) + distance(E, F)
    d1 = distance(A, C) + distance(B, D) + distance(E, F)
    d2 = distance(A, B) + distance(C, E) + distance(D, F)
    d3 = distance(A, D) + distance(E, B) + distance(C, F)
    d4 = distance(F, B) + distance(C, D) + distance(E, A)

    if d0 > d1:
        new_individual[i:j] = reversed(new_individual[i:j])
        return new_individual
    elif d0 > d2:
        new_individual[j:k] = reversed(new_individual[j:k])
        return new_individual
    elif d0 > d4:
        new_individual[i:k] = reversed(new_individual[i:k])
        return new_individual
    elif d0 > d3:
        tmp = new_individual[j:k] + new_individual[i:j]
        new_individual[i:k] = tmp
        return new_individual

    return individual


class genetic_algorithm_class():
    def __init__(self,
                 crossover,
                 mutate,
                 selection_method,
                 fitness_function,
                 population_size=10,
                 elite_size=1,
                 tournament_proportion=0.3,
                 generations=100,
                 mutation_rate=0.01,
                 range_of_mutation=None):
        self.crossover = crossover
        self.mutate = mutate
        self.selection_method = selection_method
        self.fitness_function = fitness_function
        self.population_size = population_size
        self.elite_size = elite_size
        self.tournament_proportion = tournament_proportion
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.range_of_mutation = range_of_mutation

    def sort_population_by_fitness(self, population):
        return sorted(population, key=self.fitness_function)

    def generate_population(self, data):
        population = []

        for _ in range(self.population_size):
            population.append(random.sample(data, len(data)))

        return population

    def make_next_generation(self, previous_population, generation):
        next_generation = []
        sorted_by_fitness_population = self.sort_population_by_fitness(
            previous_population)
        tournament_size = max(
            1, int(self.population_size * self.tournament_proportion))

        for i in range(self.population_size - self.elite_size):
            father = select_by_tournament(sorted_by_fitness_population,
                                          tournament_size,
                                          self.fitness_function)
            mother = select_by_tournament(sorted_by_fitness_population,
                                          tournament_size,
                                          self.fitness_function)

            individual = self.crossover(father, mother)
            individual = self.mutate(individual,
                                     self.mutation_rate,
                                     max_range=self.range_of_mutation,
                                     generation=generation,
                                     max_generations=self.generations)
            next_generation.append(individual)

        if self.elite_size > 0:
            elite = sorted_by_fitness_population[:self.elite_size]
            next_generation.extend(elite)

        return next_generation

    def solve(self, data):
        population = self.generate_population(data)

        i = 1  # se itera una cantidad igual a la cantidad de generaciones definidas
        bestFitness = []
        while True:
            if i == self.generations:
                break

            i += 1

            population = self.make_next_generation(population, i)

            best_individual = self.sort_population_by_fitness(population)[0]
            bestFitness.append(self.fitness_function(best_individual))

        best_individual = self.sort_population_by_fitness(population)[0]
        return best_individual, bestFitness, population

    def __str__(self):
        result = "ga(population_size={}, elite_size={}, tournament_proportion={}, generations={}, mutation_rate={}, range_of_mutation={})"
        return result.format(self.population_size, self.elite_size,
                             self.tournament_proportion, self.generations,
                             self.mutation_rate,
                             self.range_of_mutation)
