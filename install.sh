#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  Zane Mega Center — One-Click Installer
#  Sets up venv, dependencies, and desktop shortcut
# ═══════════════════════════════════════════════════════════
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_SCRIPT="$SCRIPT_DIR/ZaneMegaCenter.py"
REQ_FILE="$SCRIPT_DIR/requirements.txt"
VENV_DIR="$HOME/.local/share/zanemegacenter/venv"
DESKTOP_FILE="$HOME/Desktop/Zane_Mega_Center.desktop"

echo -e "${RED}${BOLD}═══════════════════════════════════════════════${RESET}"
echo -e "${RED}${BOLD}  ⚡ ZANE MEGA CENTER — INSTALLER${RESET}"
echo -e "${RED}${BOLD}═══════════════════════════════════════════════${RESET}"
echo

# ── 1. Check that the main script exists ──
if [ ! -f "$APP_SCRIPT" ]; then
    echo -e "${RED}[✗] ZaneMegaCenter.py not found in $SCRIPT_DIR${RESET}"
    exit 1
fi
echo -e "${GREEN}[✓]${RESET} Found ZaneMegaCenter.py"

# ── 2. Install system packages if missing ──
echo -e "${BOLD}[*] Checking system dependencies...${RESET}"
PKGS_NEEDED=()
dpkg -s python3-venv &>/dev/null || PKGS_NEEDED+=(python3-venv)
dpkg -s python3-tk   &>/dev/null || PKGS_NEEDED+=(python3-tk)

if [ ${#PKGS_NEEDED[@]} -gt 0 ]; then
    echo -e "[*] Installing missing system packages: ${PKGS_NEEDED[*]}"
    sudo apt-get update -qq
    sudo apt-get install -y "${PKGS_NEEDED[@]}"
    echo -e "${GREEN}[✓]${RESET} System packages installed"
else
    echo -e "${GREEN}[✓]${RESET} All system packages present"
fi

# ── 3. Create / rebuild virtual environment ──
echo -e "${BOLD}[*] Setting up Python virtual environment...${RESET}"
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo "[*] Broken venv detected — removing..."
    rm -rf "$VENV_DIR"
fi

if [ ! -d "$VENV_DIR" ]; then
    mkdir -p "$(dirname "$VENV_DIR")"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}[✓]${RESET} Virtual environment created at $VENV_DIR"
else
    echo -e "${GREEN}[✓]${RESET} Virtual environment already exists"
fi

# ── 4. Install Python dependencies ──
echo -e "${BOLD}[*] Installing Python dependencies...${RESET}"
"$VENV_DIR/bin/pip" install --upgrade pip -q
if [ -f "$REQ_FILE" ]; then
    "$VENV_DIR/bin/pip" install -r "$REQ_FILE" -q
else
    "$VENV_DIR/bin/pip" install customtkinter psutil matplotlib -q
fi
echo -e "${GREEN}[✓]${RESET} All Python dependencies installed"

# ── 5. Make the main script executable ──
chmod +x "$APP_SCRIPT"

# ── 6. Create / update desktop shortcut ──
echo -e "${BOLD}[*] Creating desktop shortcut...${RESET}"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Zane Mega Center
Comment=Ultimate Cleaner and Hardware Controller
Exec=$VENV_DIR/bin/python3 $APP_SCRIPT
Icon=preferences-system
Terminal=false
Type=Application
Categories=System;Utility;
EOF

# Trust the desktop file (KDE/GNOME)
chmod +x "$DESKTOP_FILE"
if command -v gio &>/dev/null; then
    gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
fi

echo -e "${GREEN}[✓]${RESET} Desktop shortcut created at $DESKTOP_FILE"

# ── 7. Verify everything ──
echo
echo -e "${BOLD}[*] Verifying installation...${RESET}"
"$VENV_DIR/bin/python3" -c "
import customtkinter, psutil, matplotlib
print('  customtkinter', customtkinter.__version__)
print('  psutil        ', psutil.__version__)
print('  matplotlib    ', matplotlib.__version__)
print('  All imports OK ✓')
"

echo
echo -e "${RED}${BOLD}═══════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ INSTALLATION COMPLETE${RESET}"
echo -e "${RED}${BOLD}═══════════════════════════════════════════════${RESET}"
echo
echo -e "  Launch from desktop: ${BOLD}Zane Mega Center${RESET} icon"
echo -e "  Launch from terminal: ${BOLD}$VENV_DIR/bin/python3 $APP_SCRIPT${RESET}"
echo
