#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Kali Control Hub - installation des dépendances système"

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "[INFO] Mise à jour de l'index APT..."
$SUDO apt update

echo "[INFO] Installation des paquets de base..."
$SUDO apt install -y \
  python3 \
  python3-tk \
  git \
  curl \
  wget \
  flatpak

if [[ -f "requirements.txt" ]]; then
  if grep -qE '^[[:space:]]*[^#[:space:]]' requirements.txt; then
    echo "[INFO] Installation des dépendances Python depuis requirements.txt..."
    python3 -m pip install --user -r requirements.txt
  else
    echo "[INFO] Aucune dépendance Python externe à installer."
  fi
fi

echo "[OK] Installation terminée."
echo "[INFO] Lancez l'application avec : python3 app.py"
