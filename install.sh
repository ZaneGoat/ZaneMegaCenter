#!/usr/bin/env bash
# Install script for Zane Mega Center

INSTALL_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "Installing Zane Mega Center..."

# Ensure directories exist
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"

# Copy Python script
cp ZaneMegaCenter.py "$INSTALL_DIR/ZaneMegaCenter.py"
chmod +x "$INSTALL_DIR/ZaneMegaCenter.py"

# Copy and modify desktop file
cp Zane_Mega_Center.desktop "$DESKTOP_DIR/Zane_Mega_Center.desktop"
sed -i "s|Exec=.*|Exec=$INSTALL_DIR/ZaneMegaCenter.py|g" "$DESKTOP_DIR/Zane_Mega_Center.desktop"

echo "Installation complete! You can now launch Zane Mega Center from your application menu."
