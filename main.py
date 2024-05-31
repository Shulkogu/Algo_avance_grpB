import random
from random import randrange
from tqdm import tqdm
import time
import map
import excel

class Problem_Genetic(object):
    def __init__(self, genes, individuals_length, decode, fitness):
        self.genes = genes
        self.individuals_length = individuals_length
        self.decode = decode
        self.fitness = fitness

    def mutation(self, chromosome, prob):
        def inversion_mutation(chromosome_aux):
            chromosome = chromosome_aux
            index1 = randrange(0, len(chromosome))
            index2 = randrange(index1, len(chromosome))
            chromosome_mid = chromosome[index1:index2]
            chromosome_mid.reverse()
            chromosome_result = chromosome[0:index1] + chromosome_mid + chromosome[index2:]
            return chromosome_result

        aux = chromosome[:]
        for i in range(len(aux)):
            if random.random() < prob:
                aux = inversion_mutation(aux)
        return aux

    def crossover(self, parent1, parent2):
        def process_gen_repeated(copy_child1, copy_child2):
            count1 = 0
            for gen1 in copy_child1[:pos]:
                repeat = copy_child1.count(gen1)
                if repeat > 1:
                    count2 = 0
                    for gen2 in parent1[pos:]:
                        if gen2 not in copy_child1:
                            child1[count1] = parent1[pos:][count2]
                        count2 += 1
                count1 += 1

            count1 = 0
            for gen1 in copy_child2[:pos]:
                repeat = copy_child2.count(gen1)
                if repeat > 1:
                    count2 = 0
                    for gen2 in parent2[pos:]:
                        if gen2 not in copy_child2:
                            child2[count1] = parent2[pos:][count2]
                        count2 += 1
                count1 += 1

            return [child1, child2]

        pos = random.randrange(1, self.individuals_length - 1)
        child1 = parent1[:pos] + parent2[pos:]
        child2 = parent2[:pos] + parent1[pos:]
        return process_gen_repeated(child1, child2)

    def is_valid_chromosome(self, chromosome):
        truck_count = sum(1 for gene in chromosome if gene in trucks)
        return truck_count == len(trucks) and chromosome[-1] in trucks


def decodeVRP(chromosome):
    decoded = []
    sub_route = []
    start_city = 'Paris'
    for gene in chromosome:
        if gene in trucks:
            if sub_route:
                sub_route.insert(0, start_city)  # Insert 'Paris' at the start
                sub_route.append(start_city)  # Append 'Paris' at the end
                decoded.extend(sub_route)
                sub_route = []
            decoded.append(f"{gene}")
            start_city = 'Paris'
        else:
            if start_city is None:
                start_city = cities[gene][0]
            sub_route.append(cities[gene][0])
    if sub_route:
        sub_route.insert(0, start_city)  # Insert 'Paris' at the start
        sub_route.append(start_city)  # Append 'Paris' at the end
        decoded.extend(sub_route)
    return decoded


def penalty_capacity(chromosome):
    actual = chromosome
    value_penalty = 0
    capacity_list = []
    index_cap = 0

    truck_keys = list(trucks.keys())
    current_capacity = trucks[truck_keys[index_cap]]

    for gene in actual:
        if gene not in trucks:
            capacity_list.append(gene)
            if sum(cities[city][1] for city in capacity_list) > current_capacity:
                value_penalty += 100
        else:
            index_cap += 1
            if index_cap >= len(truck_keys):
                break
            current_capacity = trucks[truck_keys[index_cap]]
            capacity_list = []

    return value_penalty


def fitnessVRP(chromosome):
    def distanceTrip(index, city):
        w = distances.get(index, {})
        return w.get(city, 1000000)

    actualChromosome = chromosome
    fitness_value = 0

    penalty_cap = penalty_capacity(actualChromosome)
    sub_route = []
    start_city = 'Paris'
    for key in range(len(actualChromosome)):
        if actualChromosome[key] in trucks:
            if sub_route:
                start_idx = sub_route[0]
                end_idx = sub_route[-1]
                fitness_value += distanceTrip(end_idx, start_idx)
                sub_route = []
            start_city = 'Paris'
        else:
            if start_city is None:
                start_city = actualChromosome[key]
            if sub_route:
                fitness_value += distanceTrip(sub_route[-1], actualChromosome[key])
            sub_route.append(actualChromosome[key])
    if sub_route:
        start_idx = sub_route[0]
        end_idx = sub_route[-1]
        fitness_value += distanceTrip(end_idx, start_idx)

    fitness_value += penalty_cap
    return fitness_value


def max_age_from_fitness(fitness_value, min_fitness, max_fitness, min_age, max_age):
    if max_fitness == min_fitness:
        return max_age
    return int(min_age + (max_age - min_age) * (max_fitness - fitness_value) / (max_fitness - min_fitness))


def genetic_algorithm_t(Problem_Genetic, k, opt, ngen, size, prob_mutate, min_age, max_age):
    def initial_population(Problem_Genetic, size):
        def generate_chromosome():
            chromosome = []
            for i in Problem_Genetic.genes:
                chromosome.append(i)
            random.shuffle(chromosome)
            while not Problem_Genetic.is_valid_chromosome(chromosome):
                random.shuffle(chromosome)
            while chromosome[-1] not in trucks:
                random.shuffle(chromosome)
            return chromosome

        return [(generate_chromosome(), 0) for _ in range(size)]

    def new_generation_t(Problem_Genetic, k, opt, population, n_parents, n_directs, prob_mutate, min_age, max_age):
        def tournament_selection(Problem_Genetic, population, n, k, opt):
            winners = []
            for _ in range(n):
                elements = random.sample(population, k)
                winners.append(opt(elements, key=lambda x: Problem_Genetic.fitness(x[0])))
            return winners

        def cross_parents(Problem_Genetic, parents):
            childs = []
            for i in range(0, len(parents), 2):
                children = Problem_Genetic.crossover(parents[i][0], parents[i + 1][0])
                for child in children:
                    if Problem_Genetic.is_valid_chromosome(child):
                        childs.append((child, 0))
            return childs

        def mutate(Problem_Genetic, population, prob):
            for i in range(len(population)):
                mutated_chromosome = Problem_Genetic.mutation(population[i][0], prob)
                if Problem_Genetic.is_valid_chromosome(mutated_chromosome):
                    population[i] = (mutated_chromosome, population[i][1])
            return population

        def age_population(population, min_age, max_age, min_fitness, max_fitness):
            aged_population = []
            for chromosome, age in population:
                fitness_value = Problem_Genetic.fitness(chromosome)
                individual_max_age = max_age_from_fitness(fitness_value, min_fitness, max_fitness, min_age, max_age)
                if age <= individual_max_age:
                    aged_population.append((chromosome, age + 1))
            return aged_population

        min_fitness = min(population, key=lambda x: Problem_Genetic.fitness(x[0]))[1]
        max_fitness = max(population, key=lambda x: Problem_Genetic.fitness(x[0]))[1]

        directs = tournament_selection(Problem_Genetic, population, n_directs, k, opt)
        crosses = cross_parents(Problem_Genetic, tournament_selection(Problem_Genetic, population, n_parents, k, opt))
        mutations = mutate(Problem_Genetic, crosses, prob_mutate)
        new_generation = directs + mutations

        return age_population(new_generation, min_age, max_age, min_fitness, max_fitness)

    population = initial_population(Problem_Genetic, size)

    best_fitness = float('inf')
    best_gen = -1  # Initialize the best generation number

    for gen in tqdm(range(ngen), desc="Generation progress"):
        population = new_generation_t(Problem_Genetic, k, opt, population, 500, 500, prob_mutate, min_age, max_age)
        if not population:  # In case all individuals get aged out
            population = initial_population(Problem_Genetic, size)

        # Update the best fitness and generation number
        current_best_fitness = min(Problem_Genetic.fitness(ind[0]) for ind in population)
        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_gen = gen

    execution_time = time.time() - start_time
    bestChromosome, _ = opt(population, key=lambda x: Problem_Genetic.fitness(x[0]))
    print("Chromosome: ", bestChromosome)
    genotype = Problem_Genetic.decode(bestChromosome)
    print("Solution: ", (genotype, Problem_Genetic.fitness(bestChromosome)))
    map.generate_map(map.generate_coordinates(genotype, trucks))


    data = [k, ngen, size, prob_mutate, min_age, max_age, len(cities), Problem_Genetic.fitness(bestChromosome),
            best_gen, execution_time, execution_time/len(cities)]

    excel.add_data_to_excel(data)

    return genotype, Problem_Genetic.fitness(bestChromosome)


# Usage
cities = {
    0: ('Nice', 1),
    1: ('Marseille', 2),
    2: ('Toulouse', 2),
    3: ('Bordeaux', 2),
    4: ('Montpellier', 3),
    5: ('Rennes', 3),
    6: ('Nantes', 3),
    7: ('Lille', 3),
    8: ('Strasbourg', 1),
    9: ('Lyon', 1),
    10: ('Paris', 3),
}
distances = {
    0: {1: 157.63, 2: 468.03, 3: 634.77, 4: 271.08, 5: 845.04, 6: 789.25, 7: 832.95, 8: 544.36, 9: 297.66, 10: 686.20, },
    1: {0: 157.63, 2: 320.06, 3: 504.50, 4: 125.16, 5: 763.58, 6: 695.18, 7: 834.30, 8: 615.75, 9: 277.05, 10: 661.20, },
    2: {0: 468.03, 1: 320.06, 3: 210.25, 4: 197.28, 5: 553.78, 6: 464.64, 7: 791.72, 8: 737.27, 9: 360.82, 10: 589.06, },
    3: {0: 634.77, 1: 504.50, 2: 210.25, 4: 380.17, 5: 371.36, 6: 275.68, 7: 699.62, 8: 758.28, 9: 435.26, 10: 499.40, },
    4: {0: 271.08, 1: 125.16, 2: 197.28, 3: 380.17, 5: 658.78, 6: 584.23, 7: 784.49, 8: 629.05, 9: 251.72, 10: 596.71, },
    5: {0: 845.04, 1: 763.58, 2: 553.78, 3: 371.36, 4: 658.78, 6: 96.88, 7: 445.65, 8: 699.09, 9: 558.63, 10: 309.19, },
    6: {0: 789.25, 1: 695.18, 2: 464.64, 3: 275.68, 4: 584.23, 5: 96.88, 7: 507.84, 8: 709.27, 9: 515.29, 10: 342.32, },
    7: {0: 832.95, 1: 834.30, 2: 791.72, 3: 699.62, 4: 784.49, 5: 445.65, 6: 507.84, 8: 407.11, 9: 557.70, 10: 203.89, },
    8: {0: 544.36, 1: 615.75, 2: 737.27, 3: 758.28, 4: 629.05, 5: 699.09, 6: 709.27, 7: 407.11, 9: 383.31, 10: 397.64, },
    9: {0: 297.66, 1: 277.05, 2: 360.82, 3: 435.26, 4: 251.72, 5: 558.63, 6: 515.29, 7: 557.70, 8: 383.31, 10: 392.81, },
    10: {0: 686.20, 1: 661.20, 2: 589.06, 3: 499.40, 4: 596.71, 5: 309.19, 6: 342.32, 7: 203.89, 8: 397.64, 9: 392.81, },
}
trucks = {
    'truck1': 20,
    'truck2': 10,
    'truck3': 40,
    'truck4': 20
}
problem = Problem_Genetic(
    genes=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'truck1', 'truck2', 'truck3', 'truck4'],
    individuals_length=15,
    decode=decodeVRP,
    fitness=fitnessVRP
)

start_time = time.time()

best_solution = genetic_algorithm_t(problem, 3, min, 10, 200, 0.15, 5, 20)
