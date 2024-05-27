import pandas as pd
import matplotlib.pyplot as plt
import random
from deap import base, creator, tools, algorithms
import numpy as np
from sklearn.cluster import KMeans
from mpl_toolkits.basemap import Basemap
from tqdm import tqdm
import time

min_population = 50000  # Population minimale pour une ville
k = 10  # Nombre de camions

# Charger les données depuis le fichier CSV
file_path = 'french_cities.csv'
cities = pd.read_csv(file_path)

# Filtrer les villes avec une population >= min_population
filtered_cities = cities[cities['ville_population_2012'] >= min_population]

# Filtrer pour exclure les départements d'outre-mer
filtered_cities = filtered_cities[filtered_cities['ville_departement'].apply(lambda x: str(x).isdigit())]
filtered_cities = filtered_cities[filtered_cities['ville_departement'].astype(int) < 96]

print("Nombre de villes : ", len(filtered_cities))

# Définir la fonction de distance entre deux villes
def distance(city1, city2):
    return ((city1['ville_longitude_deg'] - city2['ville_longitude_deg']) ** 2 +
            (city1['ville_latitude_deg'] - city2['ville_latitude_deg']) ** 2) ** 0.5

# Définir la fonction de fitness pour le VRP
def fitness(individual, cities, k):
    routes = [[] for _ in range(k)]
    for i, city_index in enumerate(individual):
        routes[i % k].append(cities.iloc[city_index])

    max_distance = 0
    total_distance = 0
    visited_cities = set()

    for route in routes:
        if len(route) > 1:
            # Ajouter le retour au point de départ pour faire une boucle
            route.append(route[0])
            route_distance = sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))
            total_distance += route_distance
            max_distance = max(max_distance, route_distance)
        for city in route:
            visited_cities.add(city['ville_nom'])

    # Penalize if not all cities are visited
    unvisited_cities_penalty = len(cities) - len(visited_cities)

    return max_distance + unvisited_cities_penalty,

# Configuration de l'algorithme génétique
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# Utiliser KMeans pour initialiser les trajets
def generate_individual_with_constraints(cities, k):
    coords = cities[['ville_longitude_deg', 'ville_latitude_deg']].values
    kmeans = KMeans(n_clusters=k, random_state=42).fit(coords)
    clusters = kmeans.labels_

    individual = []
    for cluster in range(k):
        cluster_indices = [i for i, x in enumerate(clusters) if x == cluster]
        individual.extend(random.sample(cluster_indices, len(cluster_indices)))

    return individual

toolbox.register("individual", tools.initIterate, creator.Individual, lambda: generate_individual_with_constraints(filtered_cities, k))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", fitness, cities=filtered_cities, k=k)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.15)
toolbox.register("select", tools.selTournament, tournsize=3)

def main(k):
    random.seed(42)
    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(1)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", min)
    stats.register("avg", np.mean)

    generations = 500
    start_time = time.time()

    for gen in tqdm(range(generations), desc="Générations"):
        offspring = algorithms.varAnd(pop, toolbox, cxpb=0.7, mutpb=0.2)
        fits = list(map(toolbox.evaluate, offspring))
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        pop = toolbox.select(offspring, k=len(pop))

    end_time = time.time()
    print(f"Temps total d'exécution : {end_time - start_time:.2f} secondes")

    hof.update(pop)
    return pop, stats, hof

if __name__ == "__main__":
    pop, stats, hof = main(k)
    best_solution = hof[0]
    print("Meilleure solution trouvée : ", best_solution)

    # Calculer les distances des routes et les afficher
    routes = [[] for _ in range(k)]
    for i, city_index in enumerate(best_solution):
        routes[i % k].append(filtered_cities.iloc[city_index])

    for idx, route in enumerate(routes):
        route.append(route[0])  # Assurez-vous que le trajet revient au point de départ
        route_distance = sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))
        route_names = [city['ville_nom'] for city in route]
        print(f"Route {idx + 1}: {route_names}, Distance: {route_distance:.2f}")

    # Visualiser les routes optimisées sur une carte
    plt.figure(figsize=(12, 10))
    m = Basemap(projection='merc', llcrnrlat=41, urcrnrlat=51, llcrnrlon=-5, urcrnrlon=10, resolution='i')

    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary()

    colors = ['r', 'g', 'b', 'y', 'm', 'c', 'k', 'orange', 'purple', 'brown']
    for i, route in enumerate(routes):
        for j in range(len(route) - 1):
            lon1, lat1 = route[j]['ville_longitude_deg'], route[j]['ville_latitude_deg']
            lon2, lat2 = route[j + 1]['ville_longitude_deg'], route[j + 1]['ville_latitude_deg']
            x1, y1 = m(lon1, lat1)
            x2, y2 = m(lon2, lat2)
            m.plot([x1, x2], [y1, y2], colors[i % len(colors)], label=f'Route {i + 1}' if j == 0 else "")
        x, y = m(route[0]['ville_longitude_deg'], route[0]['ville_latitude_deg'])
        m.plot(x, y, 'bo', markersize=5)
        plt.text(x, y, route[0]['ville_nom'], fontsize=9)

    for i, row in filtered_cities.iterrows():
        x, y = m(row['ville_longitude_deg'], row['ville_latitude_deg'])
        plt.text(x, y, row['ville_nom'], fontsize=9)

    plt.title('Routes Optimisées pour les Livraisons')
    plt.legend()
    plt.show()
