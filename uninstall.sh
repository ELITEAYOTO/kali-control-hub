#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="kali-control-hub"
INSTALL_DIR="/opt/kali-control-hub"
BIN_PATH="/usr/local/bin/${APP_NAME}"
GLOBAL_DESKTOP_PATH="/usr/local/share/applications/${APP_NAME}.desktop"

have_cmd() { command -v "$1" >/dev/null 2>&1; }

SUDO=""
if [[ "${EUID}" -ne 0 ]]; then
  if have_cmd sudo; then
    SUDO="sudo"
  else
    echo "[ERROR] sudo requis (ou lancer en root)." >&2
    exit 1
  fi
fi

echo "[INFO] Désinstallation de ${APP_NAME}"
echo "[INFO] Suppression: ${BIN_PATH}"
$SUDO rm -f "$BIN_PATH" || true

echo "[INFO] Suppression: ${GLOBAL_DESKTOP_PATH}"
$SUDO rm -f "$GLOBAL_DESKTOP_PATH" || true

echo "[INFO] Suppression: ${INSTALL_DIR}"
$SUDO rm -rf "$INSTALL_DIR" || true

echo "[OK] Désinstallation terminée."