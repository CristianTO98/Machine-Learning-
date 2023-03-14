# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:18:28 2023

@author: agust
"""

import random
import math
from matplotlib import pyplot as plt


# función objetivo a optimizar en el programa,se desea encontrar su mínimo global
def apply_function(individual):
    x = individual["x"]  # toma como entrada un diccionario individual###
    y = individual["y"]
    firstSum = x**2.0 + y**2.0
    secondSum = math.cos(2.0*math.pi*x) + math.cos(2.0*math.pi*y)
    n = 2
    return -(-20.0*math.exp(-0.2*math.sqrt(firstSum/n)) - math.exp(secondSum/n) + 20 + math.e)
# devuelve el "fitness" (aptitud) del individuo.


###genera una población inicial de individuos###
def generate_population(size, x_boundaries, y_boundaries):
    lower_x_boundary, upper_x_boundary = x_boundaries  # límites inferior
    lower_y_boundary, upper_y_boundary = y_boundaries  # limite superior para x e y

    population = []
    for i in range(size):
        individual = {
            "x": random.uniform(lower_x_boundary, upper_x_boundary),
            "y": random.uniform(lower_y_boundary, upper_y_boundary),
        }
        population.append(individual)

    return population


# 1# selección por torneo. eligen al azar dos individuos de la población y se selecciona el mejor
def select_by_tournament(population, tournament_size):
    tournament = random.sample(population, tournament_size)
    individual = max(tournament, key=apply_function)
    return individual

 # recibe una población y la ordena según el valor de su función de aptitud


def sort_population_by_fitness(population):
    return sorted(population, key=apply_function)


# 2# cruce de BLX-alpha
def crossover(individual_a, individual_b, alpha):
    xa = individual_a["x"]
    ya = individual_a["y"]

    xb = individual_b["x"]
    yb = individual_b["y"]

    x_min = min(xa, xb)
    x_max = max(xa, xb)
    y_min = min(ya, yb)
    y_max = max(ya, yb)

    x_diff = x_max - x_min
    y_diff = y_max - y_min

    new_x_min = x_min - alpha * x_diff
    new_x_max = x_max + alpha * x_diff
    new_y_min = y_min - alpha * y_diff
    new_y_max = y_max + alpha * y_diff

    new_x = random.uniform(new_x_min, new_x_max)
    new_y = random.uniform(new_y_min, new_y_max)

    return {"x": new_x, "y": new_y}


# 3. mutación con tamaño adaptativo. los individuos con peores aptitudes tendrían una probabilidad más alta de mutar.
def mutate(individual, population_size, position,  offset=0.01, x_boundaries=(-5, 5), y_boundaries=(-5, 5)):

    # Dar orden inverso a la posición
    actual_position = population_size - position-1
    actual_population_size = population_size - 1

    # Calculate mutation probability based on population size
    mutation_prob = actual_position/actual_population_size + offset
    print(position, mutation_prob)

    # Adjust mutation range based on current population values
    x_range = x_boundaries[1] - x_boundaries[0]
    y_range = y_boundaries[1] - y_boundaries[0]

    x_mutation_range = mutation_prob * x_range
    y_mutation_range = mutation_prob * y_range

    # Apply mutation with adaptive range
    next_x = individual["x"] + random.gauss(0, x_mutation_range)
    next_y = individual["y"] + random.gauss(0, y_mutation_range)

    # Adjust bounds of mutated values
    lower_x_boundary, upper_x_boundary = x_boundaries
    lower_y_boundary, upper_y_boundary = y_boundaries

    next_x = min(max(next_x, lower_x_boundary), upper_x_boundary)
    next_y = min(max(next_y, lower_y_boundary), upper_y_boundary)

    return {"x": next_x, "y": next_y}


# 4# Reemplazo por elitismo
def make_next_generation(previous_population, elite_size=2, tournament_proportion=.2, alpha=.5):
    next_generation = []
    sorted_by_fitness_population = sort_population_by_fitness(
        previous_population)
    population_size = len(previous_population)
    tournament_size = int(population_size*tournament_proportion)

    for i in range(population_size - elite_size):
        father = select_by_tournament(
            sorted_by_fitness_population, tournament_size)
        mother = select_by_tournament(
            sorted_by_fitness_population, tournament_size)

        individual = crossover(father, mother, alpha)
       

        next_generation.append(individual)

    # Mutaciones
    next_generation = sort_population_by_fitness(next_generation)
    next_generation_size = len(next_generation)
    for count, ind in enumerate(next_generation):
        
        next_generation[count] = mutate(
                        next_generation[count],  
                        next_generation_size, 
                        count)

    elite = sorted_by_fitness_population[-elite_size:]
    next_generation.extend(elite)

    return next_generation


# =============================================================================
# MAIN
# =============================================================================

elite_size = 1
tournament_proportion = 0.3
alpha=.5
generations = 100
# se crea una población inicial
population = generate_population(
    size=10, x_boundaries=(-5, 5), y_boundaries=(-5, 5))

i = 1  # se itera una cantidad igual a la cantidad de generaciones definidas
bestFitness = []
while True:

    print(str(i))

    """
    for individual in population:
        print(individual, apply_function(individual))
    """
    if i == generations:
        break

    i += 1

    population = make_next_generation(population, elite_size=elite_size,
                                      tournament_proportion=tournament_proportion,
                                      alpha=.5
                                      )

    best_individual = sort_population_by_fitness(population)[-1]
    bestFitness.append(apply_function(best_individual))

best_individual = sort_population_by_fitness(population)[-1]
plt.plot(bestFitness)

print("\nFINAL RESULT")
print(best_individual, apply_function(best_individual))
print(len(population))

# =============================================================================
# Detecta lo que hace que el algoritmo no funcione constantemente mejor a lo largo de generaciones
# 1-el tamaño de la población es bastante pequeño (10 individuos)
# el algoritmo puede no explorar suficientemente el espacio de soluciones y puede quedarse atrapado en soluciones subóptimas
# 2-  los padres se seleccionan con una ruleta de selección.
# Este operador no garantiza que los descendientes tengan características favorables de los padres.
# 3- la mutación se realiza con una distribución normal con media cero y una desviación estándar de 0.1
# Esta mutación puede generar grandes cambios en las características de un individuo, lo que podría alejarlo del óptimo global en lugar de acercarlo.
# =============================================================================
