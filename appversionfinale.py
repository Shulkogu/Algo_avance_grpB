from flask import Flask, request, render_template_string, jsonify
import openrouteservice as ors
import folium
import random

app = Flask(__name__)

# Initialisation du client ORS
client = ors.Client(base_url='http://85.95.212.63:8082/ors')

# Coordonnées des villes
coords = [
    [[2.3504654202840927, 48.856792432605204], [5.368997166566657, 43.30257966694749],
     [1.2603793307070963, 45.833380719467556], [2.3504654202840927, 48.856792432605204]],  # Paris et Marseille
    [[7.265252, 43.710173], [-1.553621, 47.218371]],  # Nice et Nantes
    [[3.877729, 43.611931], [7.752111, 48.573405]]    # Montpellier et Strasbourg
]

colors = ['blue', 'red', 'green']

vehicle_volumes = {
    "1": 20.0,
    "2": 30.0,
    "3": 40.0
}

vehicle_weights = {
    "1": 1000.0,  # en kg
    "2": 1500.0,
    "3": 2000.0
}

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
            margin: 10px;
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
        #result-container {
            position: absolute;
            top: 80px;
            right: 55px;
            width: 350px;
            max-height: 90%;
            padding: 20px;
            background: white;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            z-index: 1000;
            overflow-y: auto;
            transition: width 0.3s, height 0.3s;
            display: none;
        }
        #result-container h2 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #007bff;
        }
        #close-result-button {
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
        <button type="button" onclick="toggleResult()">Afficher les camions et leur contenu</button>
    </div>
    <div id="result-container">
        <button id="close-result-button" onclick="toggleResult()">Fermer</button>
        <h2>Résultats</h2>
        <div id="result-content"></div>
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

        function toggleResult() {
            const resultContainer = document.getElementById('result-container');
            resultContainer.style.display = resultContainer.style.display === 'none' ? 'block' : 'none';
        }

        function submitForm() {
            const colisTypes = document.getElementsByName('colis-type');
            const colisCounts = document.getElementsByName('colis-count');
            const vehicleTypes = document.getElementsByName('vehicle-type');
            const vehicleCounts = document.getElementsByName('vehicle-count');

            const colis = [];
            for (let i = 0; i < colisTypes.length; i++) {
                const count = parseInt(colisCounts[i].value);
                for (let j = 0; j < count; j++) {
                    colis.push({
                        type: colisTypes[i].value,
                        weight: parseFloat((Math.random() * 100).toFixed(2)), // Poids aléatoire entre 0 et 100 kg
                        volume: parseFloat((Math.random() * 2).toFixed(2)), // Volume aléatoire entre 0 et 2 m³
                        id: `${i + 1}-${j + 1}` // Numéro de colis
                    });
                }
            }

            const vehicles = [];
            for (let i = 0; i < vehicleTypes.length; i++) {
                vehicles.push({
                    type: vehicleTypes[i].value,
                    count: parseInt(vehicleCounts[i].value)
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
                updateResults(data.assignments, data.total_colis, data.total_vehicles);
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

        function updateResults(assignments, totalColis, totalVehicles) {
            const resultContent = document.getElementById('result-content');
            resultContent.innerHTML = '';
            resultContent.innerHTML += '<h3>Colis</h3>';
            totalColis.forEach((colis, index) => {
                resultContent.innerHTML += `<p>Colis ${index + 1}: Type ${colis.type}, Nombre total: ${colis.count}, Poids total: ${colis.weight.toFixed(2)} kg, Volume total: ${colis.volume.toFixed(2)} m³</p>`;
            });
            resultContent.innerHTML += '<h3>Camions total</h3>';
            totalVehicles.forEach((vehicle, index) => {
                resultContent.innerHTML += `<p>Type de véhicule ${vehicle.type}, Nombre total: ${vehicle.count}</p>`;
            });
            assignments.forEach((assignment, index) => {
                const vehicle = assignment.vehicle;
                const colis = assignment.colis;
                let totalWeight = 0;
                let totalVolume = 0;
                let colisByType = {};
                colis.forEach((c) => {
                    totalWeight += c.weight;
                    totalVolume += c.volume;
                    if (!colisByType[c.type]) {
                        colisByType[c.type] = {
                            count: 0,
                            weight: 0,
                            volume: 0,
                            indices: []
                        };
                    }
                    colisByType[c.type].count += 1;
                    colisByType[c.type].weight += c.weight;
                    colisByType[c.type].volume += c.volume;
                    colisByType[c.type].indices.push(c.id);
                });
                const vehicleElement = document.createElement('div');
                vehicleElement.innerHTML = `<h4>Camion ${index + 1} (Type ${vehicle.type})</h4>`;
                vehicleElement.innerHTML += `<p>type ${vehicle.type} : ${vehicle.initial_weight}kg ${vehicle.initial_volume}m³</p>`;
                vehicleElement.innerHTML += `<p>Contenu total: Poids ${(vehicle.initial_weight - vehicle.weight).toFixed(2)} kg, Volume ${(vehicle.initial_volume - vehicle.volume).toFixed(2)} m³</p>`;
                vehicleElement.innerHTML += `<p>Contenu utilisé: Poids ${(vehicle.initial_weight - vehicle.weight).toFixed(2)} kg, Volume ${(vehicle.initial_volume - vehicle.volume).toFixed(2)} m³</p>`;
                vehicleElement.innerHTML += `<p>Contenu restant: Poids ${vehicle.weight.toFixed(2)} kg, Volume ${vehicle.volume.toFixed(2)} m³</p>`;
                vehicleElement.innerHTML += `<h5>Colis:</h5>`;
                for (const [type, details] of Object.entries(colisByType)) {
                    vehicleElement.innerHTML += `<p>Colis type ${type}: Nombre total: ${details.count}, Poids total: ${details.weight.toFixed(2)} kg, Volume total: ${details.volume.toFixed(2)} m³, Numéros de colis: ${details.indices.join('; ')}</p>`;
                }
                resultContent.appendChild(vehicleElement);
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
    
    # Bin packing logic using Best Fit algorithm
    assignments = []
    vehicle_list = []

    for vehicle in vehicles:
        for _ in range(vehicle['count']):
            vehicle_list.append({
                'type': vehicle['type'],
                'volume': vehicle_volumes[vehicle['type']],
                'initial_volume': vehicle_volumes[vehicle['type']],
                'weight': vehicle_weights[vehicle['type']],
                'initial_weight': vehicle_weights[vehicle['type']],
                'colis': []
            })

    for col in colis:
        col_volume = col['volume']
        col_weight = col['weight']

        best_fit_index = -1
        min_remaining_volume = float('inf')
        min_remaining_weight = float('inf')

        for i, v in enumerate(vehicle_list):
            if v['volume'] >= col_volume and v['weight'] >= col_weight:
                remaining_volume = v['volume'] - col_volume
                remaining_weight = v['weight'] - col_weight
                if remaining_volume < min_remaining_volume and remaining_weight < min_remaining_weight:
                    best_fit_index = i
                    min_remaining_volume = remaining_volume
                    min_remaining_weight = remaining_weight

        if best_fit_index != -1:
            vehicle_list[best_fit_index]['colis'].append(col)
            vehicle_list[best_fit_index]['volume'] -= col_volume
            vehicle_list[best_fit_index]['weight'] -= col_weight

    assignments = [{"vehicle": v, "colis": v['colis']} for v in vehicle_list]

    total_colis = [
        {"type": col['type'], "count": sum(1 for c in colis if c['type'] == col['type']),
         "weight": sum(c['weight'] for c in colis if c['type'] == col['type']),
         "volume": sum(c['volume'] for c in colis if c['type'] == col['type'])}
        for col in colis
    ]
    total_colis = list({frozenset(item.items()): item for item in total_colis}.values())

    total_vehicles = [
        {"type": v['type'], "count": sum(vehicle['count'] for vehicle in vehicles if vehicle['type'] == v['type'])}
        for v in vehicles
    ]
    total_vehicles = list({frozenset(item.items()): item for item in total_vehicles}.values())

    # Generate routes and responses based on assignments
    routes = []
    color_index = 0

    for vehicle in vehicle_list:
        if color_index < len(coords):
            coord = coords[int(vehicle['type']) - 1]
            route = client.directions(coordinates=coord, profile='driving-car', format='geojson')
            route_coordinates = [list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']]
            routes.append({"coordinates": route_coordinates, "color": colors[int(vehicle['type']) - 1]})
            color_index += 1

    return jsonify({"status": "success", "message": "Données reçues avec succès", "routes": routes, "assignments": assignments, "total_colis": total_colis, "total_vehicles": total_vehicles})

if __name__ == '__main__':
    app.run(port=5000, debug=True)

