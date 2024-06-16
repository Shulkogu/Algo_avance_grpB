import webbrowser
import distinctipy
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
        return float(cities_dict[city]["ville_longitude_deg"]), float(cities_dict[city]["ville_latitude_deg"])
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
    client = ors.Client(base_url='http://projectors.airdns.org:15865/ors')
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    num_routes = len(coords)
    colors = distinctipy.get_colors(num_routes)
    hex_colors = [distinctipy.get_hex(color) for color in colors]
    for i, coord in enumerate(coords):
        route = client.directions(coordinates=coord, profile='driving-car', format='geojson')
        fg = folium.FeatureGroup(name=f'<span style="color: {hex_colors[i]};">Route {i + 1}</span>')
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
                        color=hex_colors[i]).add_to(fg)
        folium.Marker(
            location=[coord[0][1], coord[0][0]],
            popup=f"Point de départ de la route {i + 1}",
            icon=folium.Icon(color='', icon_color=hex_colors[i], icon='glyphicon-map-marker')
        ).add_to(fg)

        fg.add_to(m)

    for i, coord in enumerate(coords):
        fg = folium.FeatureGroup(
            name=f'<span style="color: {hex_colors[i]};">Itinéraire à vol d\'oiseau {i + 1}</span>')
        for j in range(len(coord) - 1):
            folium.PolyLine(locations=[[coord[j][1], coord[j][0]], [coord[j + 1][1], coord[j + 1][0]]],
                            color=hex_colors[i], dash_array='5, 10').add_to(fg)
        fg.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    m.save('map.html')
    with open('map.html', 'r', encoding='utf-8') as f:
        map_html = f.read()
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Carte des Routes</title>
        <style>
            body, html {
                height: 100%;
                margin: 0;
                padding: 0;
            }
            #map {
                position: absolute;
                top: 0;
                bottom: 0;
                width: 100%;
            }
            #dashboard {
                position: absolute;
                top: 80px;
                left: 10px;
                width: 320px;
                max-height: 90%;
                padding: 10px;
                background: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                border-radius: 5px;
                z-index: 1000;
                overflow-y: auto;
                transition: width 0.3s, height 0.3s;
            }
            #dashboard h2, #dashboard h3 {
                margin-top: 0;
            }
            .vehicle-inputs {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                margin-bottom: 10px;
            }
            .vehicle-inputs label {
                margin-right: 5px;
            }
            .vehicle-inputs input {
                margin-right: 10px;
                margin-bottom: 5px;
                width: 70px;
            }
            #toggle-button {
                position: absolute;
                top: 5px;
                right: 5px;
                padding: 5px 10px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 3px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div id="dashboard">
            <button id="toggle-button" onclick="toggleDashboard()">Réduire</button>
            <h2>Paramètres</h2>
            <label for="colis">Nombre de colis:</label>
            <input type="number" id="colis" name="colis" min="1" max="100"><br><br>
            <h3>Véhicules</h3>
            <div id="vehicles-container"></div>
            <button onclick="addVehicle()">Ajouter un type de véhicule</button>
        </div>
        <div id="map"></div>
        {map_html}
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"></script>
        <script>
            // Fonction pour ajouter un type de véhicule
            function addVehicle() {
                const container = document.getElementById('vehicles-container');
                const div = document.createElement('div');
                div.className = 'vehicle-inputs';
                div.innerHTML = `
                    <label>Longueur:</label>
                    <input type="number" name="vehicle-length" placeholder="mètres">
                    <label>Largeur:</label>
                    <input type="number" name="vehicle-width" placeholder="mètres">
                    <label>Hauteur:</label>
                    <input type="number" name="vehicle-height" placeholder="mètres">
                    <label>Nombre:</label>
                    <input type="number" name="vehicle-count" min="1" placeholder="Nombre">
                `;
                container.appendChild(div);
            }

            // Fonction pour basculer la taille du tableau de bord
            function toggleDashboard() {
                const dashboard = document.getElementById('dashboard');
                const toggleButton = document.getElementById('toggle-button');
                if (dashboard.style.width === '320px' || dashboard.style.width === '') {
                    dashboard.style.width = '100px';
                    dashboard.style.height = '50px';
                    toggleButton.textContent = 'Agrandir';
                } else {
                    dashboard.style.width = '320px';
                    dashboard.style.height = 'auto';
                    toggleButton.textContent = 'Réduire';
                }
            }

            // Initialisation de la carte Folium dans la div map
            var map = L.map('map').setView([46.603354, 1.888334], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19
            }).addTo(map);

            // Ajouter les itinéraires depuis la carte Folium
            var features = null;
            // Insertion des features JSON générées par Folium
            features = {features: [
                // Vos features ici (générés par Folium)
            ]};
            if (features) {
                L.geoJSON(features).addTo(map);
            }
        </script>
    </body>
    </html>
    """
    final_html = dashboard_html.replace('{map_html}', map_html)
    with open('map.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    webbrowser.open('map.html')
