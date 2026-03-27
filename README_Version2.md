# Kali Control Hub

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Platform](https://img.shields.io/badge/platform-Kali%20%2F%20Debian-like-black.svg)
![Version](https://img.shields.io/badge/version-v1.0.0-green.svg)

Kali Control Hub est une application desktop légère en **Python + tkinter** pour centraliser la gestion d'outils Linux/Kali depuis une interface unique.

## Fonctionnalités
- Interface dark moderne sous tkinter.
- Outils classés par catégories (System, Dev, Cyber, Apps).
- Vérification d'installation par outil.
- Installation en un clic (avec logs).
- Lancement GUI/CLI.
- Console intégrée.

## Installation one-liner (recommandé)
```bash
curl -fsSL https://raw.githubusercontent.com/ELITEAYOTO/kali-control-hub/main/install.sh | bash
```

### Ce que fait l’installation
- Installe les dépendances système manquantes
- Copie l’app dans `/opt/kali-control-hub`
- Crée un venv Python
- Installe les dépendances Python
- Crée la commande globale `kali-control-hub`
- Crée un `.desktop` global + raccourci Desktop utilisateur (si détecté)

## Lancer
```bash
kali-control-hub
```

## Désinstaller
```bash
sudo /opt/kali-control-hub/uninstall.sh
```

## Installation manuelle (optionnel)
```bash
git clone https://github.com/ELITEAYOTO/kali-control-hub.git
cd kali-control-hub
chmod +x install.sh
./install.sh
```

## Proton VPN (CLI uniquement)
Le projet vise l’usage CLI pour Proton VPN (pas GNOME forcé).  
Si nécessaire, installe une version CLI selon disponibilité des dépôts.

## Licence
MIT — voir [LICENSE](LICENSE).