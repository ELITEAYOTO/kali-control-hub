# Kali Control Hub

Kali Control Hub est une application desktop légère en **Python + tkinter** pour centraliser la gestion d'outils Linux/Kali depuis une interface unique.

Le hub permet de :
- vérifier si un outil est installé,
- l'installer si absent,
- le lancer (GUI ou CLI),
- afficher les logs dans une console intégrée.

## Fonctionnalités

- Interface dark moderne sous tkinter.
- Outils classés par catégories (System, Dev, Cyber, Apps).
- Vérification d'installation par outil.
- Installation en un clic (avec logs).
- Lancement GUI direct.
- Lancement CLI dans terminal avec fallback robuste.
- Aide CLI contextuelle quand aucun argument n'est fourni (pour certains outils).
- Console intégrée colorée (`INFO`, `OK`, `ERREUR`, `CMD`).
- Boutons globaux : refresh, effacer console, ouvrir terminal.

## Captures d'écran

<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/86f1ae87-5109-4552-bf05-7c815149aafa" />


### Vue principale
`docs/screenshots/main.png`

### Console intégrée
`docs/screenshots/console.png`

### Onglets outils
`docs/screenshots/tabs.png`

## Installation (Kali / Debian-like)

### 1) Cloner le projet

```bash
git clone https://github.com/<your-username>/kali-control-hub.git
cd kali-control-hub
```

### 2) Lancer le script d'installation système

```bash
chmod +x install.sh
./install.sh
```

### 3) (Optionnel) Créer un environnement virtuel Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
python3 app.py
```

## Structure du projet

```text
kali-control-hub/
├── app.py
├── install.sh
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Licence

Ce projet est distribué sous licence **MIT**.  
Voir le fichier [LICENSE](LICENSE).
