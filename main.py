import random
import time


def crossover(parents):
    child = parents[0][:len(parents[0]) // 2]
    for gene in parents[1]:
        if gene not in child:
            child.append(gene)
    return child


def mutation(individual):
    index1, index2 = random.sample(range(1, len(individual)), 2)
    while individual[index1] == individual[index2]:
        index1, index2 = random.sample(range(1, len(individual)), 2)
    individual[index1], individual[index2] = individual[index2], individual[index1]
    return individual


class GeneticAlgorithm:
    def __init__(self, matrix, start_point, num_generations):
        self.matrix = matrix
        self.start_point = start_point
        self.num_generations = num_generations
        self.population_size = len(matrix)
        self.population = self.init_population()

    def init_population(self):
        population = []
        for _ in range(self.population_size):
            individual = list(self.matrix.keys())
            individual.remove(self.start_point)
            random.shuffle(individual)
            individual.insert(0, self.start_point)
            population.append(individual)
        return population

    def fitness(self, individual):
        total_distance = 0
        for i in range(len(individual) - 1):
            if individual[i] in self.matrix and individual[i + 1] in self.matrix[individual[i]]:
                total_distance += self.matrix[individual[i]][individual[i + 1]]
            else:
                return float('inf')  # return infinity if the path is not valid
        return total_distance

    def selection(self):
        self.population.sort(key=self.fitness)
        return self.population[:2]

    def run(self):
        for _ in range(self.num_generations):
            parents = self.selection()
            child = crossover(parents)
            child = mutation(child)
            self.population.append(child)
        self.population.sort(key=self.fitness)
        return self.population[0]


def launch(loop=10, start_point='A', num_generations=100):
    minimum = float('inf')
    min_path = []
    best_generation = 0
    generation_nb = 1
    total_time = 0
    for i in range(loop):
        start = time.time()
        ga = GeneticAlgorithm(matrix, start_point, num_generations)
        shortest_path = ga.run()
        if ga.fitness(shortest_path) < minimum:
            minimum = ga.fitness(shortest_path)
            min_path = shortest_path
            best_generation = generation_nb
        total_time += time.time() - start
        print(
            f"{generation_nb} - The shortest path is {shortest_path} with total distance {ga.fitness(shortest_path)}, time taken: {time.time() - start:.6f} seconds")
        generation_nb += 1
    print(f"\nThe best path is {min_path} with total distance {minimum} found in generation {best_generation}"
          f"\ntotal time taken: {total_time:.6f} seconds"
          f"\naverage time taken: {total_time / loop:.6f} seconds"
          f"\nnumber of generations per loops: {num_generations}"
          f"\nnumber of loops: {loop}"
          f"\nstart point: {start_point}")


matrix = {
    "A": {"B": 10, "C": 4, "D": 9},
    "B": {"A": 10, "C": 13, "D": 5},
    "C": {"A": 4, "B": 13, "D": 11},
    "D": {"A": 9, "B": 5, "C": 11}
}

matrix = {
    "A": {"B": 10, "C": 4, "D": 9, "E": 3, "F": 7},
    "B": {"A": 10, "C": 13, "D": 5, "E": 8, "F": 6},
    "C": {"A": 4, "B": 13, "D": 11, "E": 2, "F": 12},
    "D": {"A": 9, "B": 5, "C": 11, "E": 7, "F": 10},
    "E": {"A": 3, "B": 8, "C": 2, "D": 7, "F": 6},
    "F": {"A": 7, "B": 6, "C": 12, "D": 10, "E": 6}
}

matrix = {
    "A": {"B": 1, "C": 4.5, "D": 5, "E": 4, "F": 2.4, "G": 2.2, "H": 3.1, "I": 4.6, "J": 3.9},
    "B": {"A": 1, "C": 4, "D": 4.5, "E": 4.7, "F": 3.4, "G": 3.2, "H": 3.6, "I": 4.3, "J": 3.7},
    "C": {"A": 4.5, "B": 4, "D": 2, "E": 5.1, "F": 5.8, "G": 5.9, "H": 4.3, "I": 3.9, "J": 2.5},
    "D": {"A": 5, "B": 4.5, "C": 2, "E": 3.5, "F": 5, "G": 5.2, "H": 4.6, "I": 3.8, "J": 3.4},
    "E": {"A": 4, "B": 4.7, "C": 5.1, "D": 3.5, "F": 2.6, "G": 2.7, "H": 2.9, "I": 4.1, "J": 4.5},
    "F": {"A": 2.4, "B": 3.4, "C": 5.8, "D": 5, "E": 2.6, "G": 0.3, "H": 2.1, "I": 3.5, "J": 4.2},
    "G": {"A": 2.2, "B": 3.2, "C": 5.9, "D": 5.2, "E": 2.7, "F": 0.3, "H": 1.9, "I": 3.2, "J": 3.6},
    "H": {"A": 3.1, "B": 3.6, "C": 4.3, "D": 4.6, "E": 2.9, "F": 2.1, "G": 1.9, "I": 4.5, "J": 4.1},
    "I": {"A": 4.6, "B": 4.3, "C": 3.9, "D": 3.8, "E": 4.1, "F": 3.5, "G": 3.2, "H": 4.5, "J": 3.3},
    "J": {"A": 3.9, "B": 3.7, "C": 2.5, "D": 3.4, "E": 4.5, "F": 4.2, "G": 3.6, "H": 4.1, "I": 3.3}
}

matrix = {
    "A": {"B": 10, "C": 45, "D": 50, "E": 40, "F": 24, "G": 22, "H": 31, "I": 46, "J": 39, "K": 25, "L": 36},
    "B": {"A": 10, "C": 40, "D": 45, "E": 47, "F": 34, "G": 32, "H": 36, "I": 43, "J": 37, "K": 22, "L": 30},
    "C": {"A": 45, "B": 40, "D": 20, "E": 51, "F": 58, "G": 59, "H": 43, "I": 39, "J": 25, "K": 50, "L": 46},
    "D": {"A": 50, "B": 45, "C": 20, "E": 35, "F": 50, "G": 52, "H": 46, "I": 38, "J": 34, "K": 40, "L": 35},
    "E": {"A": 40, "B": 47, "C": 51, "D": 35, "F": 26, "G": 27, "H": 29, "I": 41, "J": 45, "K": 30, "L": 38},
    "F": {"A": 24, "B": 34, "C": 58, "D": 50, "E": 26, "G": 3, "H": 21, "I": 35, "J": 42, "K": 30, "L": 40},
    "G": {"A": 22, "B": 32, "C": 59, "D": 52, "E": 27, "F": 3, "H": 19, "I": 32, "J": 36, "K": 33, "L": 38},
    "H": {"A": 31, "B": 36, "C": 43, "D": 46, "E": 29, "F": 21, "G": 19, "I": 45, "J": 41, "K": 25, "L": 33},
    "I": {"A": 46, "B": 43, "C": 39, "D": 38, "E": 41, "F": 35, "G": 32, "H": 45, "J": 33, "K": 40, "L": 37},
    "J": {"A": 39, "B": 37, "C": 25, "D": 34, "E": 45, "F": 42, "G": 36, "H": 41, "I": 33, "K": 28, "L": 32},
    "K": {"A": 25, "B": 22, "C": 50, "D": 40, "E": 30, "F": 30, "G": 33, "H": 25, "I": 40, "J": 28, "L": 15},
    "L": {"A": 36, "B": 30, "C": 46, "D": 35, "E": 38, "F": 40, "G": 38, "H": 33, "I": 37, "J": 32, "K": 15}
}

start_point = 'A'
num_generations = 100
num_loops = 1000

launch(num_loops, start_point, num_generations)
