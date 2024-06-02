import openrouteservice as ors
import folium
import webbrowser
import distinctipy

# Initialisation du client ORS
client = ors.Client(base_url='http://projectors.airdns.org:15865/ors')

# Coordonnées des villes
coords = [
    [[2.3504654202840927, 48.856792432605204], [5.368997166566657, 43.30257966694749],
     [1.2603793307070963, 45.833380719467556], [2.3504654202840927, 48.856792432605204]],  # Paris et Marseille
    [[7.265252, 43.710173], [-1.553621, 47.218371]],  # Nice et Nantes
    [[3.877729, 43.611931], [7.752111, 48.573405]]    # Montpellier et Strasbourg
]

# Création de la carte
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# Couleurs des itinéraires
num_routes = len(coords)
colors = distinctipy.get_colors(num_routes)
hex_colors = [distinctipy.get_hex(color) for color in colors]

# Tracé des itinéraires à vol d'oiseau avec la même couleur que les itinéraires routiers
for i, coord in enumerate(coords):
    fg = folium.FeatureGroup(name=f'<span style="color: {hex_colors[i]};">Itinéraire à vol d\'oiseau {i + 1}</span>')
    for j in range(len(coord) - 1):
        folium.PolyLine(locations=[[coord[j][1], coord[j][0]], [coord[j+1][1], coord[j+1][0]]],
                        color=hex_colors[i], dash_array='5, 10').add_to(fg)
    fg.add_to(m)

# Tracé des itinéraires routiers
for i, coord in enumerate(coords):
    route = client.directions(coordinates=coord, profile='driving-car', format='geojson')

    # Créer une nouvelle FeatureGroup pour chaque itinéraire
    fg = folium.FeatureGroup(name=f'<span style="color: {hex_colors[i]};">Route {i + 1}</span>')

    # Ajouter le tracé à la FeatureGroup
    folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
                    color=hex_colors[i]).add_to(fg)

    # Ajouter le point de départ à la FeatureGroup
    folium.Marker(
        location=[coord[0][1], coord[0][0]],
        popup=f"Point de départ de la route {i + 1}",
        icon=folium.Icon(color='', icon_color=hex_colors[i], icon='glyphicon-map-marker')
    ).add_to(fg)

    fg.add_to(m)

# Ajouter le contrôle des couches
folium.LayerControl(collapsed=False).add_to(m)

# Sauvegarde de la carte au format HTML
m.save('carte_route.html')

# Lire le fichier HTML généré
with open('models/carte_route.html', 'r', encoding='utf-8') as f:
    map_html = f.read()

# Contenu HTML pour le tableau de bord
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

# Combinaison du contenu de la carte et du tableau de bord
final_html = dashboard_html.replace('{map_html}', map_html)

# Enregistre le fichier HTML final
with open('models/carte_route.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

# Ouverture du fichier HTML dans le navigateur
webbrowser.open('models/carte_route.html')
