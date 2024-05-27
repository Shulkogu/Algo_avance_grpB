import tkinter as tk
from tkinter import ttk, messagebox
import random

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

def simuler_bin_packing(colis, camions):
    for c in colis:
        for camion in camions:
            if camion.peut_ajouter_colis(c):
                camion.ajouter_colis(c)
                break
    return camions

def afficher_resultats(camions):
    result_window = tk.Toplevel()
    result_window.title("Résultats de la Simulation")
    result_window.geometry("600x400")

    for camion in camions:
        camion_frame = ttk.LabelFrame(result_window, text=f"Camion {camion.id}")
        camion_frame.pack(fill="x", padx=5, pady=5)

        details = f"Volume maximum: {camion.volume_max} m³\nVolume occupé: {camion.volume_occupe} m³\nColis:\n"
        for colis in camion.colis:
            details += f"  Colis {colis.id} (Volume: {colis.volume} m³)\n"
        
        label = ttk.Label(camion_frame, text=details)
        label.pack()

def main():
    def start_simulation():
        try:
            num_camions = int(entry_num_camions.get())
            num_colis = int(entry_num_colis.get())

            camions = []
            for i in range(num_camions):
                capacite_camion = entry_capacites[i].get()
                capacite_largeur, capacite_hauteur, capacite_profondeur = map(int, capacite_camion.split(','))
                camions.append(Camion(i+1, capacite_largeur, capacite_hauteur, capacite_profondeur))

            random.seed(42)
            colis = [Colis(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(num_colis)]

            camions = simuler_bin_packing(colis, camions)
            afficher_resultats(camions)
        except ValueError:
            messagebox.showerror("Erreur de saisie", "Veuillez entrer des valeurs valides.")

    root = tk.Tk()
    root.title("Simulation de Bin Packing")
    root.geometry("400x400")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill="both", expand=True)

    label_num_camions = ttk.Label(main_frame, text="Nombre de camions:")
    label_num_camions.grid(column=0, row=0, sticky="W")
    entry_num_camions = ttk.Entry(main_frame)
    entry_num_camions.grid(column=1, row=0, sticky="EW")

    label_num_colis = ttk.Label(main_frame, text="Nombre de colis:")
    label_num_colis.grid(column=0, row=1, sticky="W")
    entry_num_colis = ttk.Entry(main_frame)
    entry_num_colis.grid(column=1, row=1, sticky="EW")

    entry_capacites = []

    def generate_camion_entries():
        for widget in camion_frame.winfo_children():
            widget.destroy()

        num_camions = int(entry_num_camions.get())
        for i in range(num_camions):
            label_capacite = ttk.Label(camion_frame, text=f"Capacité du camion {i+1} (L, H, P):")
            label_capacite.grid(column=0, row=i, sticky="W")
            entry_capacite = ttk.Entry(camion_frame)
            entry_capacite.grid(column=1, row=i, sticky="EW")
            entry_capacites.append(entry_capacite)

    generate_camion_btn = ttk.Button(main_frame, text="Générer les champs des camions", command=generate_camion_entries)
    generate_camion_btn.grid(column=0, row=2, columnspan=2, pady=5)

    camion_frame = ttk.Frame(main_frame)
    camion_frame.grid(column=0, row=3, columnspan=2, pady=5)

    start_btn = ttk.Button(main_frame, text="Démarrer la simulation", command=start_simulation)
    start_btn.grid(column=0, row=4, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
