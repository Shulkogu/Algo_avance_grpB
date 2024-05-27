# Livrable Modélisation

# Importation des bibliothèques nécessaires
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix
import random
import time


# Contexte et description du problème
# Depuis les années 90, il y a eu une véritable prise de conscience mondiale de la nécessité de réduire la consommation d'énergie et des émissions de gaz à effet de serre...
# Voir le texte complet ci-dessus pour le contexte.

# Réformulation du problème de manière formelle
# Problème de Tournée de Livraison (Traveling Salesman Problem, TSP) avec prise en compte du trafic routier et des fenêtres de temps pour les livraisons.

# Génération aléatoire des villes et des distances (version de base du problème)
def generate_random_cities(n):
    return np.random.rand(n, 2) * 100  # Génération de n villes dans un carré 100x100


# Exemple avec 1000 villes
n_cities = 500
cities = generate_random_cities(n_cities)

# Calcul des distances entre les villes
distances = distance_matrix(cities, cities)

# Affichage des villes et des distances
plt.figure(figsize=(10, 10))
plt.scatter(cities[:, 0], cities[:, 1], c='red')
for i, city in enumerate(cities):
    plt.text(city[0], city[1], str(i), fontsize=12)
plt.title('Emplacement des villes')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.show()


# Fonction de coût : somme des distances
def tour_cost(tour, distance_matrix):
    return sum(distance_matrix[tour[i], tour[i + 1]] for i in range(len(tour) - 1)) + distance_matrix[tour[-1], tour[0]]


# Algorithme de recherche locale : Recherche Tabou
def tabu_search(distance_matrix, initial_tour, n_iterations, tabu_list_size):
    n_cities = len(initial_tour)
    best_tour = initial_tour
    best_cost = tour_cost(best_tour, distance_matrix)
    current_tour = best_tour[:]
    tabu_list = []

    for iteration in range(n_iterations):
        neighborhood = []
        for i in range(n_cities):
            for j in range(i + 1, n_cities):
                neighbor = current_tour[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                if neighbor not in tabu_list:
                    neighborhood.append((neighbor, tour_cost(neighbor, distance_matrix)))

        if not neighborhood:
            break

        neighborhood.sort(key=lambda x: x[1])
        best_neighbor = neighborhood[0]

        if best_neighbor[1] < best_cost:
            best_tour = best_neighbor[0]
            best_cost = best_neighbor[1]

        current_tour = best_neighbor[0]
        tabu_list.append(current_tour)
        if len(tabu_list) > tabu_list_size:
            tabu_list.pop(0)

        print(f"Iteration {iteration + 1}/{n_iterations}: Cost = {best_cost}")

    return best_tour, best_cost


# Exécution de l'algorithme
initial_tour = list(range(n_cities))
random.shuffle(initial_tour)

n_iterations = 100
tabu_list_size = 50

start_time = time.time()
best_tour, best_cost = tabu_search(distances, initial_tour, n_iterations, tabu_list_size)
end_time = time.time()

# Affichage des résultats
print(f"Best tour: {best_tour}")
print(f"Best cost: {best_cost}")
print(f"Time taken: {end_time - start_time} seconds")

# Affichage de la tournée
plt.figure(figsize=(10, 10))
plt.scatter(cities[:, 0], cities[:, 1], c='red')
for i in range(len(best_tour)):
    plt.text(cities[best_tour[i], 0], cities[best_tour[i], 1], str(best_tour[i]), fontsize=12)
for i in range(len(best_tour)):
    start_city = cities[best_tour[i]]
    end_city = cities[best_tour[(i + 1) % n_cities]]
    plt.plot([start_city[0], end_city[0]], [start_city[1], end_city[1]], 'b-')
plt.title('Meilleure tournée trouvée')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.show
