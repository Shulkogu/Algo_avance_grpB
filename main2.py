import csv
import math
import random
import time
from tqdm import tqdm
import matplotlib.pyplot as plt


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
        for _ in tqdm(range(self.num_generations), desc="Generation"):
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


# Fonction pour calculer la distance euclidienne entre deux points géographiques
def distance(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en kilomètres
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(
        dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


# Charger les données depuis le fichier CSV
def load_cities_from_csv(filename):
    cities = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = {
                'nom': row['ville_nom_reel'],
                'latitude': float(row['ville_latitude_deg']),
                'longitude': float(row['ville_longitude_deg'])
            }
            cities[row['ville_nom_reel']] = city
    return cities


# Sélectionner un sous-ensemble aléatoire de villes
def select_random_cities(cities, num_cities):
    return random.sample(list(cities.keys()), num_cities)


# Construire la matrice de distances entre les villes
# Construire la matrice de distances entre les villes
def build_distance_matrix(cities):
    matrix = {}
    for city1, data1 in cities.items():
        matrix[city1] = {}
        for city2, data2 in cities.items():
            if city1 != city2:
                matrix[city1][city2] = distance(data1['latitude'], data1['longitude'], data2['latitude'],
                                                data2['longitude'])
    return matrix


def plot_best_path(cities, best_path):
    # Extraire les coordonnées des villes du meilleur chemin
    x = [cities[city]['longitude'] for city in best_path]
    y = [cities[city]['latitude'] for city in best_path]

    # Tracer le trajet
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='b')
    plt.title('Trajet de la meilleure génération')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()


# Paramètres pour l'algorithme génétique
start_point = 'Paris'
num_generations = 10
num_loops = 1

# Charger les données des villes
cities = load_cities_from_csv('french_cities.csv')

# Sélectionner les villes spécifiques
selected_cities = {
    'Paris': cities['Paris'],
    'Lille': cities['Lille'],
    'Nancy': cities['Nancy'],
    'Lyon': cities['Lyon'],
    'Saint-Étienne': cities['Saint-Étienne'],
    'Marseille': cities['Marseille'],
    'Toulouse': cities['Toulouse']
}

# Sélectionner 1000 villes aléatoires supplémentaires
additional_cities = select_random_cities(cities, 1000)

# Fusionner les deux ensembles de villes
selected_cities.update({city: cities[city] for city in additional_cities})

# Construire la matrice de distances entre les villes sélectionnées
matrix = build_distance_matrix(selected_cities)

# Initialiser l'instance de l'algorithme génétique
ga = GeneticAlgorithm(matrix, start_point, num_generations)

# Exécuter l'algorithme génétique
launch(num_loops, start_point, num_generations)

# À la fin des générations, obtenir le meilleur chemin et tracer le trajet
best_path = ga.population[0]
plot_best_path(matrix, best_path)
