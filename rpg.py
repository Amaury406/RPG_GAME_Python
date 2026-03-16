import json
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog
import os


class Personnage:
    def __init__(self, sante=0, exp=0, atq=0):
        self._sante = sante
        self._exp = exp
        self._atq = atq
        self.type = ""
        self._max_sante = sante
        self._boost = 0
        self._vivant = True
        self.niveau = 1

    @property
    def sante(self):
        return self._sante

    @sante.setter
    def sante(self, valeur):
        if valeur <= 0:
            self._sante = 0
            self._vivant = False
        else:
            self._sante = min(valeur, self._max_sante)

    @property
    def max_sante(self):
        return self._max_sante

    @property
    def atq(self):
        return self._atq + self._boost

    @property
    def boost(self):
        return self._boost

    @boost.setter
    def boost(self, valeur):
        self._boost = valeur

    @property
    def vivant(self):
        return self._vivant

    @vivant.setter
    def vivant(self, valeur):
        self._vivant = valeur

    def gagner_exp(self, points):
        self._exp += points
        if self._exp >= self.niveau * 100:
            self.niveau += 1
            self._max_sante += 20
            self._sante = self._max_sante
            self._atq += 10
            return True
        return False

    def vikings(self):
        self._sante = 120
        self._max_sante = 120
        self._exp = 1
        self._atq = 50
        self.type = "vikings"
        self.emoji = "⚔️"

    def sorcier(self):
        self._sante = 80
        self._max_sante = 80
        self._exp = 1
        self._atq = 0
        self.type = "sorcier"
        self.emoji = "🔮"

    def ases(self):
        self._sante = 70
        self._max_sante = 70
        self._exp = 1
        self._atq = 0
        self.type = "ases"
        self.emoji = "✨"

    def __str__(self):
        return f"{self.emoji} {self.type} (PV: {self._sante}/{self._max_sante}, ATQ: {self.atq})"


class Guilde:
    def __init__(self, nom=""):
        self.nom = nom
        self.equipe = []
        self.actif = None
        self.score = 0

    def ajouter_personnage(self, type_perso):
        perso = Personnage()
        if type_perso == "vikings":
            perso.vikings()
        elif type_perso == "sorcier":
            perso.sorcier()
        elif type_perso == "ases":
            perso.ases()
        self.equipe.append(perso)

    def personnages_vivants(self):
        return [p for p in self.equipe if p.vivant]

    def composition_texte(self):
        types = {}
        for perso in self.equipe:
            if perso.vivant:
                types[perso.type] = types.get(perso.type, 0) + 1
        return ", ".join([f"{count} {type_}{'s' if count > 1 else ''}" for type_, count in types.items()])

    def sauvegarder(self, nom_fichier):

        if not os.path.exists("saves"):
            os.makedirs("saves")

        chemin = os.path.join("saves", nom_fichier)

        sauvegarde = []
        for p in self.equipe:
            sauvegarde.append({
                "type": p.type,
                "sante": p._sante,
                "max_sante": p._max_sante,
                "atq": p._atq,
                "boost": p._boost,
                "vivant": p._vivant,
                "exp": p._exp,
                "niveau": p.niveau
            })
        with open(chemin, "w") as f:
            json.dump(sauvegarde, f, indent=4)

    def charger(self, nom_fichier):
        try:

            chemin = os.path.join("saves", nom_fichier)
            with open(chemin, "r") as f:
                sauvegarde = json.load(f)

            self.equipe = []
            for data in sauvegarde:
                perso = Personnage()
                perso.type = data["type"]
                perso._sante = data["sante"]
                perso._max_sante = data["max_sante"]
                perso._atq = data["atq"]
                perso._boost = data["boost"]
                perso._vivant = data["vivant"]
                perso._exp = data.get("exp", 1)
                perso.niveau = data.get("niveau", 1)

                if perso.type == "vikings":
                    perso.emoji = "⚔️"
                elif perso.type == "sorcier":
                    perso.emoji = "🔮"
                elif perso.type == "ases":
                    perso.emoji = "✨"

                self.equipe.append(perso)
            return True
        except FileNotFoundError:
            return False


class InterfaceCombat:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚔️ Combat de Guildes - BTS SIO ⚔️")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')

        if not os.path.exists("saves"):
            os.makedirs("saves")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TButton', font=('Arial', 10, 'bold'))

        self.guilde1 = None
        self.guilde2 = None
        self.combat = None

        self.creer_menu_principal()
        self.root.mainloop()

    def creer_menu_principal(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        titre = tk.Label(main_frame, text="⚔️ COMBAT DE GUILDES ⚔️",
                         font=('Arial', 28, 'bold'),
                         bg='#2c3e50', fg='#ecf0f1')
        titre.pack(pady=30)

        sous_titre = tk.Label(main_frame, text="BTS SIO - Projet Python",
                              font=('Arial', 14),
                              bg='#2c3e50', fg='#bdc3c7')
        sous_titre.pack(pady=10)

        btn_frame = tk.Frame(main_frame, bg='#2c3e50')
        btn_frame.pack(expand=True)

        btn_nouveau = tk.Button(btn_frame, text="🆕 Nouvelle Partie",
                                command=self.nouvelle_partie,
                                font=('Arial', 14, 'bold'),
                                bg='#27ae60', fg='white',
                                width=20, height=2,
                                relief='raised', bd=3)
        btn_nouveau.pack(pady=10)

        btn_charger = tk.Button(btn_frame, text="📂 Charger Partie",
                                command=self.charger_partie,
                                font=('Arial', 14, 'bold'),
                                bg='#2980b9', fg='white',
                                width=20, height=2,
                                relief='raised', bd=3)
        btn_charger.pack(pady=10)

        btn_quitter = tk.Button(btn_frame, text="❌ Quitter",
                                command=self.root.quit,
                                font=('Arial', 14, 'bold'),
                                bg='#c0392b', fg='white',
                                width=20, height=2,
                                relief='raised', bd=3)
        btn_quitter.pack(pady=10)

        footer = tk.Label(main_frame,
                          text="Développé dans le cadre du BTS SIO",
                          font=('Arial', 10),
                          bg='#2c3e50', fg='#7f8c8d')
        footer.pack(side='bottom', pady=20)

    def nouvelle_partie(self):
        self.creation_guilde(1)

    def creation_guilde(self, numero_joueur):
        creation = tk.Toplevel(self.root)
        creation.title(f"Création de la Guilde du Joueur {numero_joueur}")
        creation.geometry("500x400")
        creation.configure(bg='#34495e')
        creation.transient(self.root)
        creation.grab_set()

        nb_vikings = tk.IntVar(value=0)
        nb_sorciers = tk.IntVar(value=0)
        nb_ases = tk.IntVar(value=0)

        tk.Label(creation, text=f"👥 Joueur {numero_joueur} - Composition",
                 font=('Arial', 16, 'bold'),
                 bg='#34495e', fg='#ecf0f1').pack(pady=20)

        tk.Label(creation, text="Choisissez vos personnages (max 5)",
                 font=('Arial', 11),
                 bg='#34495e', fg='#bdc3c7').pack()

        compteurs_frame = tk.Frame(creation, bg='#34495e')
        compteurs_frame.pack(pady=30)

        tk.Label(compteurs_frame, text="⚔️ Vikings :",
                 font=('Arial', 12),
                 bg='#34495e', fg='#e74c3c').grid(row=0, column=0, padx=10, pady=5)
        tk.Spinbox(compteurs_frame, from_=0, to=5, textvariable=nb_vikings,
                   width=10, font=('Arial', 12)).grid(row=0, column=1, padx=10)

        tk.Label(compteurs_frame, text="🔮 Sorciers :",
                 font=('Arial', 12),
                 bg='#34495e', fg='#3498db').grid(row=1, column=0, padx=10, pady=5)
        tk.Spinbox(compteurs_frame, from_=0, to=5, textvariable=nb_sorciers,
                   width=10, font=('Arial', 12)).grid(row=1, column=1, padx=10)

        tk.Label(compteurs_frame, text="✨ Ases :",
                 font=('Arial', 12),
                 bg='#34495e', fg='#f1c40f').grid(row=2, column=0, padx=10, pady=5)
        tk.Spinbox(compteurs_frame, from_=0, to=5, textvariable=nb_ases,
                   width=10, font=('Arial', 12)).grid(row=2, column=1, padx=10)

        self.total_label = tk.Label(compteurs_frame, text="Total: 0/5",
                                    font=('Arial', 12, 'bold'),
                                    bg='#34495e', fg='#2ecc71')
        self.total_label.grid(row=3, column=0, columnspan=2, pady=20)

        def mettre_a_jour_total(*args):
            total = nb_vikings.get() + nb_sorciers.get() + nb_ases.get()
            self.total_label.config(text=f"Total: {total}/5")
            if total == 5:
                self.total_label.config(fg='#2ecc71')
            elif total > 5:
                self.total_label.config(fg='#e74c3c')
            else:
                self.total_label.config(fg='#f39c12')

        nb_vikings.trace('w', mettre_a_jour_total)
        nb_sorciers.trace('w', mettre_a_jour_total)
        nb_ases.trace('w', mettre_a_jour_total)

        def valider():
            total = nb_vikings.get() + nb_sorciers.get() + nb_ases.get()
            if total > 5:
                messagebox.showerror(
                    "Erreur", "La guilde ne doit pas dépasser 5 personnages !")
                return
            if total == 0:
                messagebox.showerror(
                    "Erreur", "Vous devez avoir au moins 1 personnage !")
                return

            guilde = Guilde(f"Joueur {numero_joueur}")

            for _ in range(nb_vikings.get()):
                guilde.ajouter_personnage("vikings")
            for _ in range(nb_sorciers.get()):
                guilde.ajouter_personnage("sorcier")
            for _ in range(nb_ases.get()):
                guilde.ajouter_personnage("ases")

            if numero_joueur == 1:
                self.guilde1 = guilde
                creation.destroy()
                self.creation_guilde(2)
            else:
                self.guilde2 = guilde
                creation.destroy()
                self.choisir_premier_joueur()

        tk.Button(creation, text="✅ Valider", command=valider,
                  font=('Arial', 12, 'bold'),
                  bg='#27ae60', fg='white',
                  width=15, height=2).pack(pady=20)

    def choisir_premier_joueur(self):
        choix = tk.Toplevel(self.root)
        choix.title("Qui commence ?")
        choix.geometry("400x200")
        choix.configure(bg='#34495e')
        choix.transient(self.root)
        choix.grab_set()

        tk.Label(choix, text="🏆 Qui commence le combat ? 🏆",
                 font=('Arial', 14, 'bold'),
                 bg='#34495e', fg='#ecf0f1').pack(pady=30)

        def set_premier(joueur):
            self.premier_joueur = joueur
            choix.destroy()
            self.lancer_combat()

        btn_frame = tk.Frame(choix, bg='#34495e')
        btn_frame.pack(expand=True)

        tk.Button(btn_frame, text="Joueur 1",
                  command=lambda: set_premier('joueur1'),
                  font=('Arial', 12, 'bold'),
                  bg='#3498db', fg='white',
                  width=10, height=2).pack(side='left', padx=10)

        tk.Button(btn_frame, text="Joueur 2",
                  command=lambda: set_premier('joueur2'),
                  font=('Arial', 12, 'bold'),
                  bg='#e74c3c', fg='white',
                  width=10, height=2).pack(side='left', padx=10)

    def lancer_combat(self):
        combat_window = tk.Toplevel(self.root)
        combat_window.title("⚔️ Combat en cours ⚔️")
        combat_window.geometry("1200x700")
        combat_window.configure(bg='#2c3e50')

        self.combat = CombatGUI(
            combat_window, self.guilde1, self.guilde2, self.premier_joueur, self)

    def charger_partie(self):
        from tkinter import filedialog

        fichier = filedialog.askopenfilename(
            title="Choisir une sauvegarde",
            filetypes=[("Fichiers JSON", "*.json")],
            initialdir="saves"
        )

        if fichier:
            nom_fichier = os.path.basename(fichier)
            if nom_fichier.startswith("g1_"):
                guilde = Guilde("Joueur 1 (chargé)")
                if guilde.charger(nom_fichier):
                    self.guilde1 = guilde
                    messagebox.showinfo("Succès", "Guilde 1 chargée")
                    self.creation_guilde(2)
                else:
                    messagebox.showerror("Erreur", "Fichier invalide")
            elif nom_fichier.startswith("g2_"):
                guilde = Guilde("Joueur 2 (chargé)")
                if guilde.charger(nom_fichier):
                    self.guilde2 = guilde
                    messagebox.showinfo("Succès", "Guilde 2 chargée")
                    self.choisir_premier_joueur()
                else:
                    messagebox.showerror("Erreur", "Fichier invalide")


class CombatGUI:
    def __init__(self, parent, guilde1, guilde2, premier_joueur, interface_principale):
        self.parent = parent
        self.g1 = guilde1
        self.g2 = guilde2
        self.tour = premier_joueur
        self.interface_principale = interface_principale

        self.creer_interface()
        self.choisir_actif('joueur1')
        self.choisir_actif('joueur2')
        self.mettre_a_jour_affichage()

    def creer_interface(self):
        main_frame = tk.Frame(self.parent, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        header = tk.Frame(main_frame, bg='#34495e', height=60)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)

        self.header_label = tk.Label(header, text=f"⚔️ Tour du {self.tour} ⚔️",
                                     font=('Arial', 18, 'bold'),
                                     bg='#34495e', fg='#ecf0f1')
        self.header_label.pack(expand=True)

        guildes_frame = tk.Frame(main_frame, bg='#2c3e50')
        guildes_frame.pack(fill='both', expand=True)

        self.g1_frame = tk.Frame(
            guildes_frame, bg='#34495e', relief='raised', bd=2)
        self.g1_frame.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(self.g1_frame, text=f"👥 {self.g1.nom}",
                 font=('Arial', 14, 'bold'),
                 bg='#34495e', fg='#3498db').pack(pady=10)

        self.g1_actif_label = tk.Label(self.g1_frame, text="Personnage actif: Aucun",
                                       font=('Arial', 12),
                                       bg='#34495e', fg='#ecf0f1')
        self.g1_actif_label.pack()

        self.g1_composition = tk.Label(self.g1_frame, text="",
                                       font=('Arial', 10),
                                       bg='#34495e', fg='#bdc3c7')
        self.g1_composition.pack(pady=5)

        self.g1_listbox = tk.Listbox(self.g1_frame, bg='#2c3e50', fg='#ecf0f1',
                                     font=('Arial', 10), height=8)
        self.g1_listbox.pack(fill='both', expand=True, padx=10, pady=5)

        self.g2_frame = tk.Frame(
            guildes_frame, bg='#34495e', relief='raised', bd=2)
        self.g2_frame.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(self.g2_frame, text=f"👥 {self.g2.nom}",
                 font=('Arial', 14, 'bold'),
                 bg='#34495e', fg='#e74c3c').pack(pady=10)

        self.g2_actif_label = tk.Label(self.g2_frame, text="Personnage actif: Aucun",
                                       font=('Arial', 12),
                                       bg='#34495e', fg='#ecf0f1')
        self.g2_actif_label.pack()

        self.g2_composition = tk.Label(self.g2_frame, text="",
                                       font=('Arial', 10),
                                       bg='#34495e', fg='#bdc3c7')
        self.g2_composition.pack(pady=5)

        self.g2_listbox = tk.Listbox(self.g2_frame, bg='#2c3e50', fg='#ecf0f1',
                                     font=('Arial', 10), height=8)
        self.g2_listbox.pack(fill='both', expand=True, padx=10, pady=5)

        actions_frame = tk.Frame(main_frame, bg='#34495e', height=150)
        actions_frame.pack(fill='x', pady=10)
        actions_frame.pack_propagate(False)

        tk.Label(actions_frame, text="🎮 Actions disponibles",
                 font=('Arial', 12, 'bold'),
                 bg='#34495e', fg='#ecf0f1').pack(pady=5)

        boutons_frame = tk.Frame(actions_frame, bg='#34495e')
        boutons_frame.pack(expand=True)

        self.btn_attaque = tk.Button(boutons_frame, text="⚔️ Attaquer",
                                     command=self.action_attaque,
                                     bg='#e74c3c', fg='white',
                                     font=('Arial', 10, 'bold'),
                                     width=12, height=2,
                                     state='disabled')
        self.btn_attaque.pack(side='left', padx=5)

        self.btn_soin = tk.Button(boutons_frame, text="💚 Soigner",
                                  command=self.action_soin,
                                  bg='#27ae60', fg='white',
                                  font=('Arial', 10, 'bold'),
                                  width=12, height=2,
                                  state='disabled')
        self.btn_soin.pack(side='left', padx=5)

        self.btn_boost = tk.Button(boutons_frame, text="✨ Booster",
                                   command=self.action_boost,
                                   bg='#f39c12', fg='white',
                                   font=('Arial', 10, 'bold'),
                                   width=12, height=2,
                                   state='disabled')
        self.btn_boost.pack(side='left', padx=5)

        self.btn_changer = tk.Button(boutons_frame, text="🔄 Changer",
                                     command=self.action_changer,
                                     bg='#3498db', fg='white',
                                     font=('Arial', 10, 'bold'),
                                     width=12, height=2)
        self.btn_changer.pack(side='left', padx=5)

        self.btn_sauvegarder = tk.Button(boutons_frame, text="💾 Sauvegarder",
                                         command=self.sauvegarder_partie,
                                         bg='#9b59b6', fg='white',
                                         font=('Arial', 10, 'bold'),
                                         width=12, height=2)
        self.btn_sauvegarder.pack(side='left', padx=5)

        log_frame = tk.Frame(main_frame, bg='#34495e', height=100)
        log_frame.pack(fill='x', pady=5)
        log_frame.pack_propagate(False)

        tk.Label(log_frame, text="📜 Historique des actions",
                 font=('Arial', 10, 'bold'),
                 bg='#34495e', fg='#ecf0f1').pack(anchor='w', padx=10, pady=2)

        self.log_text = tk.Text(log_frame, bg='#2c3e50', fg='#ecf0f1',
                                font=('Arial', 9), height=4)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

    def choisir_actif(self, joueur):
        guilde = self.g1 if joueur == 'joueur1' else self.g2
        vivants = guilde.personnages_vivants()

        if not vivants:
            return

        choix = tk.Toplevel(self.parent)
        choix.title(f"Choix du personnage actif - {guilde.nom}")
        choix.geometry("400x300")
        choix.configure(bg='#34495e')
        choix.transient(self.parent)
        choix.grab_set()

        tk.Label(choix, text=f"Choisissez votre personnage actif :",
                 font=('Arial', 12, 'bold'),
                 bg='#34495e', fg='#ecf0f1').pack(pady=20)

        listbox = tk.Listbox(choix, bg='#2c3e50', fg='#ecf0f1',
                             font=('Arial', 11), height=8)
        listbox.pack(fill='both', expand=True, padx=20, pady=10)

        for i, perso in enumerate(vivants):
            listbox.insert(tk.END, f"{i+1}. {perso}")

        def selectionner():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                guilde.actif = vivants[index]
                self.ajouter_log(
                    f"{guilde.nom} a choisi {guilde.actif.type} comme personnage actif.")
                choix.destroy()
                self.mettre_a_jour_affichage()

        tk.Button(choix, text="✅ Sélectionner", command=selectionner,
                  font=('Arial', 11, 'bold'),
                  bg='#27ae60', fg='white',
                  width=15, height=2).pack(pady=10)

        choix.wait_window()

    def mettre_a_jour_affichage(self):
        self.g1_listbox.delete(0, tk.END)
        for perso in self.g1.equipe:
            self.g1_listbox.insert(tk.END, f"{perso}")

        self.g2_listbox.delete(0, tk.END)
        for perso in self.g2.equipe:
            self.g2_listbox.insert(tk.END, f"{perso}")

        if self.g1.actif:
            self.g1_actif_label.config(
                text=f"Personnage actif: {self.g1.actif}")
        if self.g2.actif:
            self.g2_actif_label.config(
                text=f"Personnage actif: {self.g2.actif}")

        self.g1_composition.config(
            text=f"Composition: {self.g1.composition_texte()}")
        self.g2_composition.config(
            text=f"Composition: {self.g2.composition_texte()}")

        self.header_label.config(text=f"⚔️ Tour du {self.tour} ⚔️")

        joueur_actuel = 'joueur1' if self.tour == 'joueur1' else 'joueur2'
        guilde = self.g1 if joueur_actuel == 'joueur1' else self.g2

        if guilde.actif:
            self.btn_attaque.config(
                state='normal' if guilde.actif.type == 'vikings' else 'disabled')
            self.btn_soin.config(
                state='normal' if guilde.actif.type == 'sorcier' else 'disabled')
            self.btn_boost.config(
                state='normal' if guilde.actif.type == 'ases' else 'disabled')

    def action_attaque(self):
        joueur_actuel = 'joueur1' if self.tour == 'joueur1' else 'joueur2'
        guilde = self.g1 if joueur_actuel == 'joueur1' else self.g2
        adversaire = self.g2 if joueur_actuel == 'joueur1' else self.g1

        if not adversaire.actif or not adversaire.actif.vivant:
            self.ajouter_log(
                "L'adversaire n'a pas de personnage actif valide !")
            return

        degats = guilde.actif.atq
        adversaire.actif.sante -= degats

        self.ajouter_log(
            f"⚔️ {guilde.nom} attaque et inflige {degats} dégâts !")

        if not adversaire.actif.vivant:
            self.ajouter_log(
                f"💀 {adversaire.actif.type} de {adversaire.nom} est mort !")

            vivants = adversaire.personnages_vivants()
            if not vivants:
                self.fin_combat(guilde.nom)
                return

            self.choisir_actif('joueur2' if joueur_actuel ==
                               'joueur1' else 'joueur1')

        self.tour = 'joueur2' if self.tour == 'joueur1' else 'joueur1'
        self.mettre_a_jour_affichage()

    def action_soin(self):
        joueur_actuel = 'joueur1' if self.tour == 'joueur1' else 'joueur2'
        guilde = self.g1 if joueur_actuel == 'joueur1' else self.g2

        vivants = [p for p in guilde.personnages_vivants(
        ) if p != guilde.actif and p.sante < p.max_sante]

        if not vivants:
            self.ajouter_log("❌ Aucun allié à soigner !")
            return

        choix = tk.Toplevel(self.parent)
        choix.title("Choisir la cible du soin")
        choix.geometry("400x300")
        choix.configure(bg='#34495e')
        choix.transient(self.parent)
        choix.grab_set()

        tk.Label(choix, text="Qui voulez-vous soigner ?",
                 font=('Arial', 12, 'bold'),
                 bg='#34495e', fg='#ecf0f1').pack(pady=20)

        listbox = tk.Listbox(choix, bg='#2c3e50', fg='#ecf0f1',
                             font=('Arial', 11), height=8)
        listbox.pack(fill='both', expand=True, padx=20, pady=10)

        for i, perso in enumerate(vivants):
            listbox.insert(tk.END, f"{i+1}. {perso}")

        def soigner():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                cible = vivants[index]
                soin = min(50, cible.max_sante - cible.sante)
                cible.sante += soin
                self.ajouter_log(
                    f"💚 {guilde.nom} soigne {cible.type} de {soin} PV !")
                choix.destroy()
                self.tour = 'joueur2' if self.tour == 'joueur1' else 'joueur1'
                self.mettre_a_jour_affichage()

        tk.Button(choix, text="✅ Soigner", command=soigner,
                  font=('Arial', 11, 'bold'),
                  bg='#27ae60', fg='white',
                  width=15, height=2).pack(pady=10)

    def action_boost(self):
        joueur_actuel = 'joueur1' if self.tour == 'joueur1' else 'joueur2'
        guilde = self.g1 if joueur_actuel == 'joueur1' else self.g2

        vivants = [p for p in guilde.personnages_vivants() if p !=
                   guilde.actif]

        if not vivants:
            self.ajouter_log("❌ Aucun allié à booster !")
            return

        choix = tk.Toplevel(self.parent)
        choix.title("Choisir la cible du boost")
        choix.geometry("400x300")
        choix.configure(bg='#34495e')
        choix.transient(self.parent)
        choix.grab_set()

        tk.Label(choix, text="Qui voulez-vous booster ?",
                 font=('Arial', 12, 'bold'),
                 bg='#34495e', fg='#ecf0f1').pack(pady=20)

        listbox = tk.Listbox(choix, bg='#2c3e50', fg='#ecf0f1',
                             font=('Arial', 11), height=8)
        listbox.pack(fill='both', expand=True, padx=20, pady=10)

        for i, perso in enumerate(vivants):
            listbox.insert(tk.END, f"{i+1}. {perso}")

        def booster():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                cible = vivants[index]
                cible.boost += 20
                self.ajouter_log(
                    f"✨ {guilde.nom} booste {cible.type} (+20 attaque) !")
                choix.destroy()
                self.tour = 'joueur2' if self.tour == 'joueur1' else 'joueur1'
                self.mettre_a_jour_affichage()

        tk.Button(choix, text="✅ Booster", command=booster,
                  font=('Arial', 11, 'bold'),
                  bg='#f39c12', fg='white',
                  width=15, height=2).pack(pady=10)

    def action_changer(self):
        joueur_actuel = 'joueur1' if self.tour == 'joueur1' else 'joueur2'
        self.choisir_actif(joueur_actuel)

    def sauvegarder_partie(self):
        nom_fichier = simpledialog.askstring("Sauvegarder", "Nom du fichier:")
        if nom_fichier:
            nom_fichier = nom_fichier.replace(" ", "_") + ".json"
            self.g1.sauvegarder(f"g1_{nom_fichier}")
            self.g2.sauvegarder(f"g2_{nom_fichier}")
            self.ajouter_log(f"💾 Partie sauvegardée")
            messagebox.showinfo(
                "Succès", "Partie sauvegardée dans le dossier 'saves'")

    def ajouter_log(self, message):
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)

    def fin_combat(self, gagnant):
        messagebox.showinfo("🏆 Victoire ! 🏆",
                            f"Félicitations ! {gagnant} remporte le combat !")

        reponse = messagebox.askyesno(
            "Rejouer ?", "Voulez-vous faire un autre combat ?")
        if reponse:
            self.parent.destroy()
            self.interface_principale.nouvelle_partie()
        else:
            self.parent.destroy()
            self.interface_principale.creer_menu_principal()


if __name__ == "__main__":
    app = InterfaceCombat()
