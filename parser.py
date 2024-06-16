import csv
import random
import argparse
import math


def parse_args():
    parser = argparse.ArgumentParser(description="Generate VRP problem from French cities CSV.")
    parser.add_argument('-p', type=int, help="Minimum population for filtering cities", required=True)
    parser.add_argument('-t', type=int, help="Number of trucks", required=True)
    return parser.parse_args()


def read_cities(filename, min_population):
    cities = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if int(row["ville_population_2012"]) >= min_population and int(row["ville_departement"]) < 96:
                city_id = int(row["ville_id"])
                city_name = row["ville_nom_reel"]
                lat = float(row["ville_latitude_deg"])
                lon = float(row["ville_longitude_deg"])
                cities[city_id] = (city_name, lat, lon)
    return cities


def generate_random_values(cities):
    city_demands = {}
    for city_id in cities:
        city_demands[city_id] = random.randint(1, 3)
    return city_demands


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371.0  # Radius of Earth in kilometers
    distance = c * r
    return distance


def calculate_distances(cities):
    distances = {}
    city_ids = list(cities.keys())
    for i in range(len(city_ids)):
        distances[city_ids[i]] = {}
        for j in range(len(city_ids)):
            if i != j:
                _, lat1, lon1 = cities[city_ids[i]]
                _, lat2, lon2 = cities[city_ids[j]]
                distances[city_ids[i]][city_ids[j]] = haversine(lat1, lon1, lat2, lon2)
    return distances


def generate_trucks(num_trucks):
    trucks = {}
    for i in range(1, num_trucks + 1):
        truck_name = f"truck{i}"
        trucks[truck_name] = random.choice([10, 20, 40])
    return trucks


def main():
    args = parse_args()

    cities = read_cities('french_cities.csv', args.p)
    city_demands = generate_random_values(cities)
    distances = calculate_distances(cities)
    trucks = generate_trucks(args.t)

    city_indices = {i: city_id for i, city_id in enumerate(cities.keys())}

    print("cities = {")
    for i, (city_id, (city_name, _, _)) in enumerate(cities.items()):
        print(f"    {i}: ('{city_name}', {city_demands[city_id]}),")
    print("}")

    print("distances = {")
    for i in range(len(city_indices)):
        print(f"    {i}: {{", end="")
        for j in range(len(city_indices)):
            if i != j:
                print(f"{j}: {distances[city_indices[i]][city_indices[j]]:.2f}, ", end="")
        print("},")
    print("}")

    print("trucks = {")
    for i, (truck_name, capacity) in enumerate(trucks.items()):
        if i < len(trucks) - 1:
            print(f"    '{truck_name}': {capacity},")
        else:
            print(f"    '{truck_name}': {capacity}")
    print("}")

    gene_list = list(range(len(city_indices))) + list(trucks.keys())
    print(f"problem = Problem_Genetic(")
    print(f"    genes={gene_list},")
    print(f"    individuals_length={len(gene_list)},")
    print(f"    decode=decodeVRP,")
    print(f"    fitness=fitnessVRP")
    print(")")


if __name__ == "__main__":
    main()
