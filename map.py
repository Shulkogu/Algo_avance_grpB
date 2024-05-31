import openrouteservice as ors
import folium
import csv


def read_csv(file):
    with open(file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        cities_dict = {}
        for row in csv_reader:
            if int(row["ville_departement"]) < 96:
                cities_dict[row["ville_nom_reel"]] = {
                    "ville_latitude_deg": row["ville_latitude_deg"],
                    "ville_longitude_deg": row["ville_longitude_deg"]
                }
        return cities_dict


def get_coordinates(city, cities_dict):
    if city in cities_dict:
        return cities_dict[city]["ville_longitude_deg"], cities_dict[city]["ville_latitude_deg"]
    else:
        return None


def generate_coordinates(cities, trucks):
    cities_dict = read_csv('french_cities.csv')
    sub_routes = []
    sub_route = []
    for city in cities:
        if city in trucks:
            if sub_route:
                sub_routes.append(sub_route)
                sub_route = []
            sub_routes.append([city])  # Ajout du truck comme une sous-route unique
        else:
            sub_route.append(city)

    if sub_route:
        sub_routes.append(sub_route)

    coordinates = []
    for sub_route in sub_routes:
        sub_route_coords = [get_coordinates(city, cities_dict) for city in sub_route]
        sub_route_coords = [coord for coord in sub_route_coords if coord is not None]  # Filtrage des None
        if sub_route_coords:
            coordinates.append(sub_route_coords)

    return coordinates


def generate_map(coords):
    client = ors.Client(base_url='http://10.54.128.130:8082/ors')
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
    for i, coord in enumerate(coords):
        route = client.directions(coordinates=coord, profile='driving-car', format='geojson')
        fg = folium.FeatureGroup(name=f'<span style="color: {colors[i]};">Truck {i + 1}</span>')
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
                        color=colors[i]).add_to(fg)
        folium.Marker(
            location=[coord[0][1], coord[0][0]],
            popup=f"Point de départ de la route {i + 1}",
            icon=folium.Icon(color=colors[i], icon='glyphicon-map-marker')
        ).add_to(fg)

        fg.add_to(m)
    folium.LayerControl().add_to(m)
    m.save('map.html')
    import webbrowser
    webbrowser.open('map.html')
