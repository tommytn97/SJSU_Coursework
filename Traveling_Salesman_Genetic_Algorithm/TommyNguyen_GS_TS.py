"""Tommy Nguyen
CS 223
Genetic algorithm program
"""

import random
import pandas as pd
import math
import statistics
import os
import sys


# Get distance between 2 cities
def get_distance(city1, city2, distance_between_cities):
    distance = distance_between_cities[city1][city2]
    return distance


# Create starting population
def create_starting_population(population_size, distance_between_cities):
    # start_pop is generation zero
    start_pop = []
    # appends lists of 8 length into start_pop
    for i in range(population_size):
        city_and_length = []
        city_and_length = random.sample(distance_between_cities.index.tolist(), len(distance_between_cities))
        start_pop.append(city_and_length)
    return start_pop


# Calculate the distances for each element (individual) in the population list
def population_distances(population, distance_between_cities):
    list_of_distances = []
    total_distance = 0
    for i in population:
        for city in range(0, len(i) - 1):
            total_distance += get_distance(i[city], i[city + 1], distance_between_cities)
        list_of_distances.append(total_distance)
        total_distance = 0
    return list_of_distances


# formula based off of Week 5 slide
def get_fitness(list_of_distances):
    fitness_numbers = []
    for d in list_of_distances:
        fitness_formula = 1 / (d * 10000)
        fitness_numbers.append(fitness_formula)
    return fitness_numbers

# take individuals based on the elite_percentage
# use floor to round down to the nearest integer (cannot have a partial
# individual)
def elite_selection(df, elite_percentage):
    elite_list = []
    num_elite = math.floor(len(df) * elite_percentage)
    for i in range(num_elite):
        elite_list.append(df.iloc[i, 0])
    return elite_list

# uniform crossover function for two parents and return child
def uniform_crossover(parent1, parent2):
    p = [[parent1], [parent2]]
    child = []
    for i in range(len(p[0])):
        if p[1][i] in child or p[1][i] in p[0][i:]:
            child.append(p[0][i])
        else:
            child.append(p[random.randint(0, 1)][i])
        # flatten list
        child = [city for sublist in child for city in sublist]
    return child

# Converts fitness scores to percentages and adds two columns to the dataframe
# used in the genetic algorithm
def fitness_to_percentage(df):
    total_fitness = df["Fitness"].sum()
    df["Fitness_percentage"] = (df["Fitness"] / total_fitness) * 100
    df["Cumulative_percentage"] = df["Fitness_percentage"].cumsum()


# Roulette wheel selection, using a threshold value, a pool of parents is made based on
# the threshold value. Parents under that threshold value will be randomly selected
# to reproduce and make a child. The threshold value is relative to the cumulative percentage
# from the cities_df
def roulette_wheel(df, population_size, elite_fitness_selection, fitness_percentage):
    child_crossover = []
    # threshold value can be changed, for now it will be 20 if the population is
    # small, threshold value will change accordingly
    threshold = fitness_percentage * 100
    if threshold == df['Cumulative_percentage'][0]:
        threshold = df['Cumulative_percentage'][0]
    for i in range(population_size - len(elite_fitness_selection)):
        parent1 = random.choices(df[df["Cumulative_percentage"] <= threshold].iloc[:, 0],
                                 weights=df[df["Cumulative_percentage"] <= threshold]
                                 ["Fitness_percentage"].tolist())

        # flatten the list
        parent1 = [city for sublist in parent1 for city in sublist]

        parent2 = random.choices(df[df["Cumulative_percentage"] <= threshold].iloc[:, 0],
                                 weights=df[df["Cumulative_percentage"] <= threshold]
                                 ["Fitness_percentage"].tolist())
        # flatten the list
        parent2 = [city for sublist in parent2 for city in sublist]
        child_crossover.append(uniform_crossover(parent1, parent2))
    for i in range(len(child_crossover)):
        length_of_parent = len(child_crossover[i])
        child_crossover[i] = scramble_mutation(length_of_parent, child_crossover[i])
    return child_crossover


# Shuffle the slice of a list
def shuffle_slice(child, start, stop):
    i = start
    while (i < stop - 1):
        idx = random.randrange(i, stop)
        child[i], child[idx] = child[idx], child[i]
        i += 1


# Shuffle a subset of cities of the child
def scramble_mutation(length_of_parent, child):
    num1 = random.randrange(length_of_parent)
    num2 = random.randrange(length_of_parent)
    subset_start, subset_end = min(num1, num2), (max(num1, num2) + 1)
    shuffle_slice(child, subset_start, subset_end)
    return child


# perform crossover and mutation and return child
def make_child(parent1, parent2):
    child = uniform_crossover(parent1, parent2)
    length_of_parent = len(parent1)
    child = scramble_mutation(length_of_parent, child)
    return child


# Genetic algorithm with all relevant functions
def genetic_algorithm_TS(population, distance_between_cities, population_size, elite_percentage, fitness_percentage,
                         generation_count):
    # Create starting population
    distances_of_cities = population_distances(population, distance_between_cities)
    # Get fitness of the individuals
    fitness_of_individuals = get_fitness(distances_of_cities)
    # Create dataframe for data management
    cities_df = pd.DataFrame({
        "Individuals": population,
        "Distances": distances_of_cities,
        "Fitness": fitness_of_individuals
    })

    cities_df = cities_df.sort_values("Fitness", ascending=False, ignore_index=True)

    # Convert fitness scores into percentages and add a cumulative sum for the
    # fitness scores
    fitness_to_percentage(cities_df)
    # Subset of population based on elitism
    elite_fitness_selection = elite_selection(cities_df, elite_percentage)

    # Make a child from parents done by roulette wheel selection, uniform
    # crossover and scramble mutation is also done
    child = roulette_wheel(cities_df, population_size, elite_fitness_selection, fitness_percentage)

    # Make new generation by combining the elites and child
    new_generation = elite_fitness_selection + child
    # Calculate the new generation distances and fitness
    new_generation_distances = population_distances(new_generation, distance_between_cities)
    new_generation_fitness = get_fitness(new_generation_distances)

    new_df = pd.DataFrame({
        "Individuals": new_generation,
        "Distances": new_generation_distances,
        "Fitness": new_generation_fitness
    })

    new_df = new_df.sort_values("Fitness", ascending=False, ignore_index=True)

    best_route = new_df.iloc[0, 0]
    best_route_string = ' '.join([str(city) for city in best_route])
    best_distance = new_df.iloc[0, 1]

    print("Best route of generation " + str(generation_count), ": " + best_route_string)
    print("Summation of the best route: " + str(best_distance) + "\n")

    return new_generation, best_distance, new_generation_fitness


def main(population_size=100, fitness_percentage=0.2,  elite_percentage=0.05, generations=25, minima_iterations=15):
    """ population_size: population size for a generation \n
        fitness_percentage: percentage that implements a threshold of selecting only the best \n
        elite_percentage: elitism, takes only the top individuals to be used in the next generation \n
        generations: maximum number of generations to create \n
        minima_iterations: number in which the program breaks if no improvement in the best distance \n
    """
    # Sets working directory to script's directory
    path = os.path.abspath(sys.argv[0])
    directory = os.path.dirname(path)
    os.chdir(directory)

    # Read in Traveling Salesman CSV
    distance_between_cities = pd.read_csv("TS_Distances_Between_Cities.csv", index_col=0).dropna()

    # Initialize variables
    population = create_starting_population(population_size, distance_between_cities)
    current_best_distance = 0
    minima_count = 0
    generation_count = 0

    # Open file to write each generation's statistics
    gen_stats = open("TommyNguyen_GA_TS_Info.txt", 'w')

    # Run the genetic algorithm in a loop based on generations
    for i in range(generations):
        population, best_distance, new_generation_fitness = genetic_algorithm_TS(
            population, distance_between_cities, population_size, elite_percentage, fitness_percentage, generation_count)

        # Write out the new generation's stats
        gen_stats.write("Population size is " + str(population_size) + " for iteration " + str(generation_count)
                                + "\n")
        gen_stats.write('Average fitness score : ' + str(statistics.mean(new_generation_fitness)) + '\n')
        gen_stats.write('Median fitness score : ' + str(statistics.median(new_generation_fitness)) + '\n')
        gen_stats.write('STD of fitness scores : ' + str(statistics.stdev(new_generation_fitness)) + '\n')
        gen_stats.write('Size of the selected subset of the population : ' + str(
            int(population_size * fitness_percentage)) + '\n\n')

        generation_count += 1

        # Ends loop if best_distance does not change after n iterations
        if current_best_distance == best_distance:
            minima_count += 1
        else:
            current_best_distance = best_distance
            minima_count = 0

        if minima_count == minima_iterations:
            print("Local minima was found after " + str(minima_iterations), "iterations")
            print("Program terminated after " + str(generation_count) + " generations")
            print("Minima first reach on generation " + str(generation_count - minima_count - 1))
            break

    # Write out the best result
    results = open("TommyNguyen_GA_TS_Result.txt", 'w')
    final_route = population[0]

    for city in final_route:
        results.write(str(distance_between_cities.index.tolist().index(city)) + " " + str(city) + "\n")

    results.close()
    gen_stats.close()

main(population_size=200, elite_percentage=0.3, fitness_percentage=0.3, generations=50, minima_iterations=15)