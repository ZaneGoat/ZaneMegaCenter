# Zane Mega Center

**Ultimate System Control & Cleaner | Black & Red Gaming Edition**

Zane Mega Center is a powerful system tuning utility designed primarily for the MSI GF65 Thin 10UE (and compatible Linux devices). It provides a sleek, dark-themed dashboard built with `customtkinter` to manage hardware power profiles, monitor temperatures in real-time, and run system cleanups.

## Features

- **Real-Time Thermal Telemetry**: Live updating temperature charts for CPU and GPU using Matplotlib.
- **Power Profiles**: Quickly switch between Extreme, Balance, and Super Battery modes.
- **Fan Control & Smart Boost**: Toggle Cooler Boost or enable Smart Boost to automatically ramp up fans when CPU temperature exceeds 80°C.
- **Battery Health Limit**: Cap battery charging at 60%, 80%, or 100% to preserve Li-ion cells.
- **System Cleaner**: Clear RAM caches, APT caches, pip caches, Systemd journals, unused Flatpaks, Snap caches, and Docker images with a single click.

## Requirements
- Python 3.x
- `isw` (MSI laptop fan control and system monitoring tool) installed and accessible at `/usr/local/bin/isw`
- `customtkinter`, `psutil`, `matplotlib` (automatically installed into an isolated virtual environment upon first launch)

## Installation

You can install Zane Mega Center for your user by running the provided install script:

```bash
chmod +x install.sh
./install.sh
```

This will copy the script to `~/.local/bin/` and add the application to your desktop environment's launcher menu.

## Usage
Simply launch **Zane Mega Center** from your application menu, or run:
```bash
~/.local/bin/ZaneMegaCenter.py
```

*Note: Some cleanup and hardware modules require root privileges. A secure GUI prompt will ask for your password when required.*
