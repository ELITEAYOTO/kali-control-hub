#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="kali-control-hub"
REPO_OWNER="ELITEAYOTO"
REPO_NAME="kali-control-hub"
REPO_BRANCH="main"
APP_VERSION="v1.0.0"

INSTALL_DIR="/opt/${REPO_NAME}"
BIN_PATH="/usr/local/bin/${APP_NAME}"
GLOBAL_DESKTOP_PATH="/usr/local/share/applications/${APP_NAME}.desktop"

COLOR_RED=$'\033[0;31m'
COLOR_GRN=$'\033[0;32m'
COLOR_YLW=$'\033[0;33m'
COLOR_BLU=$'\033[0;34m'
COLOR_RST=$'\033[0m'

log_info() { echo "${COLOR_BLU}[INFO]${COLOR_RST} $*"; }
log_ok()   { echo "${COLOR_GRN}[OK]${COLOR_RST} $*"; }
log_warn() { echo "${COLOR_YLW}[WARN]${COLOR_RST} $*"; }
log_err()  { echo "${COLOR_RED}[ERROR]${COLOR_RST} $*" >&2; }

die() { log_err "$*"; exit 1; }

have_cmd() { command -v "$1" >/dev/null 2>&1; }

SUDO=""
if [[ "${EUID}" -ne 0 ]]; then
  if have_cmd sudo; then
    SUDO="sudo"
  else
    die "sudo est requis (lance ce script en root ou installe sudo)."
  fi
fi

require_apt() {
  have_cmd apt-get || have_cmd apt || die "Ce script nécessite apt (Kali/Debian)."
}

apt_install_if_missing() {
  local pkgs=("$@")
  log_info "Installation des dépendances via apt: ${pkgs[*]}"
  $SUDO apt-get update -y || log_warn "apt-get update a échoué (réseau ?). On continue et on tente l'installation."
  if ! $SUDO apt-get install -y --no-install-recommends "${pkgs[@]}"; then
    die "Impossible d'installer: ${pkgs[*]}. Vérifie ta connexion puis relance."
  fi
}

ensure_cmd_or_install_pkg() {
  local cmd="$1"
  shift
  local pkgs=("$@")
  if have_cmd "$cmd"; then
    return 0
  fi
  apt_install_if_missing "${pkgs[@]}"
  have_cmd "$cmd" || die "Commande absente après installation: ${cmd}"
}

download_repo_tarball() {
  local tmpdir
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' EXIT

  local url="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/tar.gz/${REPO_BRANCH}"
  local tarball="${tmpdir}/${REPO_NAME}.tar.gz"

  log_info "Téléchargement du code source (${url})"
  if have_cmd curl; then
    curl -fL --retry 3 --retry-delay 2 -o "$tarball" "$url" || die "Téléchargement échoué via curl."
  elif have_cmd wget; then
    wget -O "$tarball" "$url" || die "Téléchargement échoué via wget."
  else
    die "Ni curl ni wget n'est disponible."
  fi

  log_info "Extraction vers ${INSTALL_DIR}"
  $SUDO mkdir -p "$INSTALL_DIR"
  tar -xzf "$tarball" -C "$tmpdir"

  local extracted
  extracted="$(find "$tmpdir" -maxdepth 1 -type d -name "${REPO_NAME}-*" | head -n 1)"
  [[ -n "$extracted" ]] || die "Extraction échouée: dossier extrait introuvable."

  $SUDO rm -rf "${INSTALL_DIR:?}/"*
  $SUDO cp -a "${extracted}/." "$INSTALL_DIR/"
}

validate_project_files() {
  [[ -f "${INSTALL_DIR}/app.py" ]] || die "app.py introuvable dans ${INSTALL_DIR}."
  [[ -f "${INSTALL_DIR}/requirements.txt" ]] || log_warn "requirements.txt introuvable (OK si aucune dépendance Python externe)."
}

create_venv_and_install_python_deps() {
  log_info "Création du venv: ${INSTALL_DIR}/.venv"
  $SUDO python3 -m venv "${INSTALL_DIR}/.venv" || die "Échec création venv (python3-venv ?)."

  $SUDO "${INSTALL_DIR}/.venv/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true
  $SUDO "${INSTALL_DIR}/.venv/bin/python" -m pip install --upgrade pip wheel >/dev/null

  if [[ -f "${INSTALL_DIR}/requirements.txt" ]] && grep -qE '^[[:space:]]*[^#[:space:]]' "${INSTALL_DIR}/requirements.txt"; then
    log_info "Installation des dépendances Python (requirements.txt)"
    if ! $SUDO "${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"; then
      die "Échec pip install -r requirements.txt"
    fi
  else
    log_info "Aucune dépendance Python externe à installer."
  fi
}

install_launcher() {
  log_info "Installation du launcher: ${BIN_PATH}"
  $SUDO tee "$BIN_PATH" >/dev/null <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail

INSTALL_DIR="/opt/kali-control-hub"
VENV_PY="${INSTALL_DIR}/.venv/bin/python"

if [[ ! -x "${VENV_PY}" ]]; then
  echo "[ERROR] Venv introuvable: ${VENV_PY}"
  echo "[INFO] Réinstalle avec: curl -fsSL https://raw.githubusercontent.com/ELITEAYOTO/kali-control-hub/main/install.sh | bash"
  exit 1
fi

exec "${VENV_PY}" "${INSTALL_DIR}/app.py" "$@"
EOF
  $SUDO chmod +x "$BIN_PATH"
}

install_global_desktop_entry() {
  log_info "Création du .desktop global: ${GLOBAL_DESKTOP_PATH}"
  $SUDO tee "$GLOBAL_DESKTOP_PATH" >/dev/null <<EOF
[Desktop Entry]
Type=Application
Name=Kali Control Hub
Comment=Centralise la gestion d'outils Kali/Linux
Exec=${BIN_PATH}
Icon=utilities-terminal
Terminal=false
Categories=Utility;System;
EOF
  $SUDO chmod 644 "$GLOBAL_DESKTOP_PATH" || true
}

install_user_desktop_shortcut() {
  local target_user="${SUDO_USER:-${USER:-}}"
  if [[ -z "$target_user" || "$target_user" == "root" ]]; then
    log_warn "Utilisateur non-root non détecté: raccourci Desktop utilisateur ignoré."
    log_warn "Le .desktop global reste disponible."
    return 0
  fi

  local user_home
  user_home="$(getent passwd "$target_user" | cut -d: -f6)"
  if [[ -z "$user_home" || ! -d "$user_home" ]]; then
    log_warn "Home introuvable pour $target_user: raccourci Desktop utilisateur ignoré."
    return 0
  fi

  local desktop_dir="$user_home/Desktop"
  if [[ ! -d "$desktop_dir" ]]; then
    desktop_dir="$user_home/Bureau"
  fi
  if [[ ! -d "$desktop_dir" ]]; then
    log_warn "Aucun dossier Desktop/Bureau trouvé pour $target_user."
    return 0
  fi

  local user_desktop_path="$desktop_dir/${APP_NAME}.desktop"
  log_info "Création du raccourci Desktop utilisateur: ${user_desktop_path}"

  cat > "/tmp/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Kali Control Hub
Comment=Centralise la gestion d'outils Kali/Linux
Exec=${BIN_PATH}
Icon=utilities-terminal
Terminal=false
Categories=Utility;System;
EOF

  $SUDO cp "/tmp/${APP_NAME}.desktop" "$user_desktop_path"
  $SUDO chown "$target_user:$target_user" "$user_desktop_path" || true
  $SUDO chmod +x "$user_desktop_path" || true
  rm -f "/tmp/${APP_NAME}.desktop"
}

check_tkinter_import() {
  log_info "Vérification tkinter dans le venv..."
  if $SUDO "${INSTALL_DIR}/.venv/bin/python" -c "import tkinter" >/dev/null 2>&1; then
    log_ok "Import tkinter OK."
  else
    log_warn "Import tkinter KO. L'app peut ne pas se lancer."
    log_warn "Vérifie python3-tk / version Python."
  fi
}

check_gui_environment() {
  log_info "Vérification environnement graphique..."
  if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    log_ok "GUI détectée (DISPLAY/WAYLAND)."
  else
    log_warn "Aucune GUI détectée actuellement."
    log_warn "Installation OK, mais l'app GUI nécessite une session desktop pour se lancer."
  fi
}

print_protonvpn_cli_hint() {
  cat <<'EOF'

[INFO] Proton VPN (CLI only):
- Installer de préférence la version CLI uniquement (pas GNOME).
- Exemple si disponible:
    sudo apt-get install -y --no-install-recommends protonvpn-cli
- Sinon, suivre la doc officielle Proton VPN Debian/Kali.

EOF
}

main() {
  require_apt

  log_info "${APP_NAME} installer (${APP_VERSION})"
  log_info "Cible: ${INSTALL_DIR}"
  log_info "Commande globale: ${BIN_PATH}"

  ensure_cmd_or_install_pkg tar tar
  ensure_cmd_or_install_pkg python3 python3
  ensure_cmd_or_install_pkg git git
  ensure_cmd_or_install_pkg curl curl || true
  ensure_cmd_or_install_pkg wget wget || true

  apt_install_if_missing python3-venv python3-tk python3-pip ca-certificates

  if ! have_cmd curl && ! have_cmd wget; then
    die "Impossible: ni curl ni wget n'est disponible."
  fi

  if [[ -f "./app.py" && -f "./install.sh" ]]; then
    log_info "Repo détecté dans le dossier courant -> copie vers ${INSTALL_DIR}"
    $SUDO mkdir -p "$INSTALL_DIR"
    $SUDO rm -rf "${INSTALL_DIR:?}/"*
    $SUDO cp -a "./." "$INSTALL_DIR/"
  else
    download_repo_tarball
  fi

  validate_project_files
  create_venv_and_install_python_deps
  install_launcher
  install_global_desktop_entry
  install_user_desktop_shortcut
  check_tkinter_import
  check_gui_environment
  print_protonvpn_cli_hint

  log_ok "Installation terminée."
  log_info "Lancer: ${APP_NAME}"
  log_info "Désinstaller: sudo ${INSTALL_DIR}/uninstall.sh"
}

main "$@"