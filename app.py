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
            font-family: Arial, sans-serif;
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
            left: 55px;
            width: 350px;
            max-height: 90%;
            padding: 20px;
            background: white;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            z-index: 1000;
            overflow-y: auto;
            transition: width 0.3s, height 0.3s;
        }
        #dashboard h2, #dashboard h3 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #fee030;
            margin: 10px
        }
        .inputs-container {
            margin-bottom: 20px;
        }
        .inputs-container label {
            width: 130px;
            font-weight: bold;
            color: #555;
        }
        .inputs-container input, .inputs-container select {
            width: calc(100% - 140px);
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        #toggle-button {
            position: absolute;
            top: 5px;
            right: 5px;
            padding: 5px 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button {
            padding: 10px 15px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        #logo {
           
            top: 10px;
            left: 10px;
            width: 50px;
            height: 50px;
        }
    </style>
</head>
<body>
    <div id="dashboard">
        <img id="logo" src="https://tse1.mm.bing.net/th?id=OIP.vxMdjujloffCSJiblGLTvQAAAA&pid=Api&P=0&h=180" alt="Logo">
        <button id="toggle-button" onclick="toggleDashboard()">Réduire</button>
        <h2>Paramètres</h2>
        <h3>Colis</h3>
        <div id="colis-container" class="inputs-container">
            <div class="colis-inputs">
                <label>Type de colis:</label>
                <select name="colis-type">
                    <option value="1">Type 1</option>
                    <option value="2">Type 2</option>
                    <option value="3">Type 3</option>
                </select>
                <label>Nombre:</label>
                <input type="number" name="colis-count" min="1" placeholder="Nombre">
            </div>
        </div>
        <button type="button" onclick="addColis()">Ajouter un type de colis</button><br><br>
        <h3>Véhicules</h3>
        <div id="vehicles-container" class="inputs-container">
            <div class="vehicle-inputs">
                <label>Type de véhicule:</label>
                <select name="vehicle-type">
                    <option value="1">Type 1</option>
                    <option value="2">Type 2</option>
                    <option value="3">Type 3</option>
                </select>
                <label>Nombre:</label>
                <input type="number" name="vehicle-count" min="1" placeholder="Nombre">
            </div>
        </div>
        <button type="button" onclick="addVehicle()">Ajouter un type de véhicule</button><br><br>
        <button type="button" onclick="submitForm()">Soumettre</button>
    </div>
    <div id="map"></div>
    {{ map_html|safe }}
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"></script>
    <script>
        function addColis() {
            const container = document.getElementById('colis-container');
            const div = document.createElement('div');
            div.className = 'colis-inputs';
            div.innerHTML = `
                <label>Type de colis:</label>
                <select name="colis-type">
                    <option value="1">Type 1</option>
                    <option value="2">Type 2</option>
                    <option value="3">Type 3</option>
                </select>
                <label>Nombre:</label>
                <input type="number" name="colis-count" min="1" placeholder="Nombre">
            `;
            container.appendChild(div);
        }

        function addVehicle() {
            const container = document.getElementById('vehicles-container');
            const div = document.createElement('div');
            div.className = 'vehicle-inputs';
            div.innerHTML = `
                <label>Type de véhicule:</label>
                <select name="vehicle-type">
                    <option value="1">Type 1</option>
                    <option value="2">Type 2</option>
                    <option value="3">Type 3</option>
                </select>
                <label>Nombre:</label>
                <input type="number" name="vehicle-count" min="1" placeholder="Nombre">
            `;
            container.appendChild(div);
        }

        function toggleDashboard() {
            const dashboard = document.getElementById('dashboard');
            const toggleButton = document.getElementById('toggle-button');
            if (dashboard.style.width === '350px' || dashboard.style.width === '') {
                dashboard.style.width = '100px';
                dashboard.style.height = '50px';
                toggleButton.textContent = 'Agrandir';
            } else {
                dashboard.style.width = '350px';
                dashboard.style.height = 'auto';
                toggleButton.textContent = 'Réduire';
            }
        }

        function submitForm() {
            const colisTypes = document.getElementsByName('colis-type');
            const colisCounts = document.getElementsByName('colis-count');
            const vehicleTypes = document.getElementsByName('vehicle-type');
            const vehicleCounts = document.getElementsByName('vehicle-count');

            const colis = [];
            for (let i = 0; i < colisTypes.length; i++) {
                colis.push({
                    type: colisTypes[i].value,
                    count: colisCounts[i].value
                });
            }

            const vehicles = [];
            for (let i = 0; i < vehicleTypes.length; i++) {
                vehicles.push({
                    type: vehicleTypes[i].value,
                    count: vehicleCounts[i].value
                });
            }

            const data = {
                colis: colis,
                vehicles: vehicles
            };

            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                updateRoutes(data.routes);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }

        function updateRoutes(routes) {
            routes.forEach((route, index) => {
                L.polyline(route.coordinates, {color: route.color}).addTo(map);
            });
        }

        var map = L.map('map').setView([46.603354, 1.888334], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19
        }).addTo(map);

        var features = null;
        features = {features: [
        ]};
        if (features) {
            L.geoJSON(features).addTo(map);
        }
    </script>
</body>
</html>






"""
from flask import Flask, request, render_template_string, jsonify
import openrouteservice as ors
import folium

app = Flask(__name__)

# Initialisation du client ORS
client = ors.Client(base_url='http://10.54.128.130:8082/ors')

# Coordonnées des villes
coords = [
    [[2.3504654202840927, 48.856792432605204], [5.368997166566657, 43.30257966694749],
     [1.2603793307070963, 45.833380719467556], [2.3504654202840927, 48.856792432605204]],  # Paris et Marseille
    [[7.265252, 43.710173], [-1.553621, 47.218371]],  # Nice et Nantes
    [[3.877729, 43.611931], [7.752111, 48.573405]]    # Montpellier et Strasbourg
]

colors = ['blue', 'red', 'green']

def create_map():
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    folium.LayerControl(collapsed=False).add_to(m)
    return m._repr_html_()

@app.route('/')
def index():
    map_html = create_map()
    return render_template_string(dashboard_html, map_html=map_html)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    colis = data.get('colis')
    vehicles = data.get('vehicles')

    print(f'Nombre de colis: {colis}')
    print(f'Véhicules: {vehicles}')
    
    routes = []
    color_index = 0

    for vehicle in vehicles:
        count = int(vehicle["count"])
        vehicle_type = int(vehicle["type"]) - 1  # Adjusting index to 0-based
        for _ in range(count):
            if color_index < len(coords):
                coord = coords[vehicle_type]
                route = client.directions(coordinates=coord, profile='driving-car', format='geojson')
                route_coordinates = [list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']]
                routes.append({"coordinates": route_coordinates, "color": colors[vehicle_type]})
                color_index += 1
            else:
                break

    return jsonify({"status": "success", "message": "Données reçues avec succès", "routes": routes})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
