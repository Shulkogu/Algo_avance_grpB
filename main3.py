import pandas as pd
import folium
from pyroutelib3 import Router


def filter_cities(data):
    data = data[data['ville_population_2012'] > 100000]
    data = data[pd.to_numeric(data['ville_departement'], errors='coerce') < 96]
    return data


# Load the data from the CSV file
def load_data_from_csv(filename):
    data = filter_cities(pd.read_csv(filename, low_memory=False))
    return data


# Create a map centered on France
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# Load the city data
cities = load_data_from_csv('french_cities.csv')

# print the number of cities
print(len(cities))

# Add the city points to the map
for index, row in cities.iterrows():
    folium.Marker([row['ville_latitude_deg'], row['ville_longitude_deg']], popup=row['ville_nom_reel']).add_to(m)

def get_coordinates(city):
    return [city['ville_latitude_deg'], city['ville_longitude_deg']]

# Get the coordinates of the cities
paris = cities[cities['ville_nom_reel'] == 'Paris'].iloc[0]
lyon = cities[cities['ville_nom_reel'] == 'Lyon'].iloc[0]

# Create a router
router = Router("car", "./france-latest.osm.pbf", localfileType="pbf")

# Find the nodes closest to the cities
depart = router.findNode(paris['ville_latitude_deg'], paris['ville_longitude_deg'])
arrivee = router.findNode(lyon['ville_latitude_deg'], lyon['ville_longitude_deg'])



# Save the map to an HTML file
m.save('map.html')