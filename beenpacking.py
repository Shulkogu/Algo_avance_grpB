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
    result_window.geometry("800x600")

    canvas = tk.Canvas(result_window, bg="#ffffff")
    scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for camion in camions:
        camion_frame = ttk.LabelFrame(scrollable_frame, text=f"Camion {camion.id}", style="Custom.TLabelframe")
        camion_frame.pack(fill="x", padx=5, pady=5)

        details = f"Volume maximum: {camion.volume_max} m³\nVolume occupé: {camion.volume_occupe} m³\nColis:\n"
        for colis in camion.colis:
            details += f"  Colis {colis.id} (Volume: {colis.volume} m³)\n"
        
        label = ttk.Label(camion_frame, text=details, style="Custom.TLabel")
        label.pack()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def main():
    def start_simulation():
        try:
            num_colis = int(entry_num_colis.get())

            camions = []
            for i, (capacite_entry, qty_entry) in enumerate(camion_entries):
                capacite_camion = capacite_entry.get()
                capacite_largeur, capacite_hauteur, capacite_profondeur = map(int, capacite_camion.split(','))
                quantity = int(qty_entry.get())
                for _ in range(quantity):
                    camions.append(Camion(len(camions) + 1, capacite_largeur, capacite_hauteur, capacite_profondeur))

            random.seed(42)
            colis = [Colis(i, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)) for i in range(num_colis)]

            camions = simuler_bin_packing(colis, camions)
            afficher_resultats(camions)
        except ValueError:
            messagebox.showerror("Erreur de saisie", "Veuillez entrer des valeurs valides.")

    root = tk.Tk()
    root.title("Simulation de Bin Packing")
    root.geometry("800x600")
    root.configure(bg="#ffffff")

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), padding=10, background="#1E90FF", foreground="#000000", relief="flat")
    style.map('TButton', background=[('active', '#1C86EE')])
    style.configure('TLabel', font=('Helvetica', 12), padding=5, background="#ffffff", foreground="#000000")
    style.configure('TEntry', font=('Helvetica', 12), padding=5, foreground="#000000")
    style.configure('TLabelframe', font=('Helvetica', 12), background="#f5f5f5", borderwidth=1, relief="solid", foreground="#000000")
    style.configure('TLabelframe.Label', font=('Helvetica', 14, 'bold'), background="#f5f5f5", foreground="#000000")

    # Custom styles for rounded buttons
    style.configure('Custom.TButton', font=('Helvetica', 12), padding=10, background="#1E90FF", foreground="#000000", borderwidth=0, relief="solid")
    style.map('Custom.TButton', background=[('active', '#1C86EE')], relief=[('pressed', 'flat')])
    style.configure('Custom.TLabel', font=('Helvetica', 12), background="#ffffff", foreground="#000000")
    style.configure('Custom.TLabelframe', background="#f5f5f5", borderwidth=1, relief="solid", foreground="#000000")
    style.configure('Custom.TLabelframe.Label', font=('Helvetica', 14, 'bold'), background="#f5f5f5", foreground="#000000")

    main_frame = ttk.Frame(root, padding="10", style="Custom.TFrame")
    main_frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(main_frame)
    header_frame.grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")

    title_label = ttk.Label(header_frame, text="Simulation de Bin Packing", font=('Helvetica', 16, 'bold'), style="Custom.TLabel")
    title_label.pack()

    form_frame = ttk.Frame(main_frame)
    form_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

    label_num_colis = ttk.Label(form_frame, text="Nombre de colis:", style="Custom.TLabel")
    label_num_colis.grid(column=0, row=0, sticky="w", padx=5)
    entry_num_colis = ttk.Entry(form_frame)
    entry_num_colis.grid(column=1, row=0, sticky="ew", padx=5)

    camion_entries = []

    def add_camion_entry():
        row = len(camion_entries) + 1
        label_capacite = ttk.Label(camion_frame, text=f"Capacité du type de camion {row} (L, H, P):", style="Custom.TLabel")
        label_capacite.grid(column=0, row=row, sticky="w", padx=5)
        entry_capacite = ttk.Entry(camion_frame)
        entry_capacite.grid(column=1, row=row, sticky="ew", padx=5)

        label_quantity = ttk.Label(camion_frame, text="Quantité:", style="Custom.TLabel")
        label_quantity.grid(column=2, row=row, sticky="w", padx=5)
        entry_quantity = ttk.Entry(camion_frame)
        entry_quantity.grid(column=3, row=row, sticky="ew", padx=5)

        camion_entries.append((entry_capacite, entry_quantity))

    # Scrollable camion frame
    camion_canvas = tk.Canvas(main_frame, bg="#ffffff")
    camion_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=camion_canvas.yview)
    camion_scrollable_frame = ttk.Frame(camion_canvas)

    camion_scrollable_frame.bind(
        "<Configure>",
        lambda e: camion_canvas.configure(
            scrollregion=camion_canvas.bbox("all")
        )
    )

    camion_canvas.create_window((0, 0), window=camion_scrollable_frame, anchor="nw")
    camion_canvas.configure(yscrollcommand=camion_scrollbar.set)

    camion_frame = ttk.Frame(camion_scrollable_frame)
    camion_frame.pack(fill="x", expand=True)

    camion_canvas.grid(row=2, column=0, columnspan=4, pady=10, sticky="nsew")
    camion_scrollbar.grid(row=2, column=4, sticky="ns")

    add_camion_btn = ttk.Button(main_frame, text="Ajouter un type de camion", command=add_camion_entry, style="Custom.TButton")
    add_camion_btn.grid(row=3, column=0, columnspan=4, pady=10)

    start_btn = ttk.Button(main_frame, text="Démarrer la simulation", command=start_simulation, style="Custom.TButton")
    start_btn.grid(row=4, column=0, columnspan=4, pady=10)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.columnconfigure(2, weight=1)
    main_frame.columnconfigure(3, weight=1)
    main_frame.rowconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    main_frame.rowconfigure(2, weight=1)
    main_frame.rowconfigure(3, weight=1)
    main_frame.rowconfigure(4, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main()
