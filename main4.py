#---------BIBLIOTHEQUES/MODULES---------
# appel des Modules/Librairies nécessaires
from pyroutelib3 import Router
import folium
import webbrowser
#----------PROGRAMME PRINCIPAL----------
# coordonnées GPS départ et arrivée
eplb_park = [46.548453, 3.286341]
moulins_mairie = [46.566067 , 3.332859]
# type de déplacement : cycle, foot, horse, tram, train, car ?
router = Router("car")
# Création des points de départ et d'arrivée
depart = router.findNode(eplb_park[0],eplb_park[1])
arrivee = router.findNode(moulins_mairie[0],moulins_mairie[1])
# calcul itinéraire : test de l'existence d'une route
status, itineraire = router.doRoute(depart, arrivee)
if status == 'success':
    routeLatLons = list(map(router.nodeLatLon, itineraire)) # liste des points du parcours
# création de la carte
carte= folium.Map(location=[(eplb_park[0]+moulins_mairie[0])/2,(eplb_park[1]+moulins_mairie[1])/2],zoom_start=15)
# ajout des points (noeuds) du parcours à la carte
for indice,coord in enumerate(routeLatLons):
    if indice%10==0:
        coord=list(coord)
        folium.Marker(coord).add_to(carte)
# ajout à la carte du tracé d'une ligne reliant les points/noeuds du parcours
itineraire_coordonnees = list(map(router.nodeLatLon, itineraire)) # liste des points du parcours
folium.PolyLine(
    itineraire_coordonnees,
    color="blue",
    weight=2.5,
    opacity=1
    ).add_to(carte)
# enregistrement et affichage de la carte
carte.save('carte.html')
webbrowser.open('carte.html')