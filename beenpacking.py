import random
from typing import List

class Colis:
    def __init__(self, identifiant: int, largeur: int, hauteur: int, profondeur: int):
        self.id = identifiant
        self.largeur = largeur
        self.hauteur = hauteur
        self.profondeur = profondeur
        self.volume = largeur * hauteur * profondeur

class Camion:
    def __init__(self, identifiant: int, capacite_largeur: int, capacite_hauteur: int, capacite_profondeur: int):
        self.id = identifiant
        self.capacite_largeur = capacite_largeur
        self.capacite_hauteur = capacite_hauteur
        self.capacite_profondeur = capacite_profondeur
        self.volume_max = capacite_largeur * capacite_hauteur * capacite_profondeur
        self.colis = []
        self.volume_occupe = 0

    def peut_ajouter_colis(self, colis: Colis) -> bool:
        return self.volume_occupe + colis.volume <= self.volume_max

    def ajouter_colis(self, colis: Colis):
        if self.peut_ajouter_colis(colis):
            self.colis.append(colis)
            self.volume_occupe += colis.volume

def simuler_bin_packing(colis: List[Colis], camions: List[Camion]):
    for c in colis:
        for camion in camions:
            if camion.peut_ajouter_colis(c):
                camion.ajouter_colis(c)
                break
    return camions

def afficher_resultats(camions: List[Camion]):
    for camion in camions:
        print(f"Camion {camion.id}:")
        print(f"  Volume maximum: {camion.volume_max} m³")
        print(f"  Volume occupé: {camion.volume_occupe} m³")
        print(f"  Colis:")
        for colis in camion.colis:
            print(f"    Colis {colis.id} (Volume: {colis.volume} m³)")
        print()

def main():
    # Saisir le nombre de camions et de colis
    num_camions = int(input("Entrez le nombre de camions: "))

    camions = []
    for i in range(num_camions):
        capacite_camion = input(f"Entrez la capacité du camion {i+1} (L, H, P) en mètres: ")
        capacite_largeur, capacite_hauteur, capacite_profondeur = map(int, capacite_camion.split(','))
        camions.append(Camion(i+1, capacite_largeur, capacite_hauteur, capacite_profondeur))

    num_colis = int(input("Entrez le nombre de colis: "))

    # Générer des colis aléatoires
    random.seed(42)
    colis = [Colis(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(num_colis)]

    # Simuler le bin packing
    camions = simuler_bin_packing(colis, camions)

    # Afficher les résultats
    afficher_resultats(camions)

if __name__ == "__main__":
    main()
message.txt
3 Ko
