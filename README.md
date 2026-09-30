<div align="center">

```
  ███████╗ █████╗ ███╗   ██╗███████╗    ███╗   ███╗███████╗ ██████╗  █████╗ 
  ╚══███╔╝██╔══██╗████╗  ██║██╔════╝    ████╗ ████║██╔════╝██╔════╝ ██╔══██╗
    ███╔╝ ███████║██╔██╗ ██║█████╗      ██╔████╔██║█████╗  ██║  ███╗███████║
   ███╔╝  ██╔══██║██║╚██╗██║██╔══╝      ██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║
  ███████╗██║  ██║██║ ╚████║███████╗    ██║ ╚═╝ ██║███████╗╚██████╔╝██║  ╚═╝
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝    ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
              — U L T I M A T E   S Y S T E M   M A T R I X —
```

# ⚡ ZANE MEGA CENTER ⚡
### *Ultimate Hardware Tuning, Thermal Telemetry & Controller Space Command Deck*

[![Python](https://img.shields.io/badge/Python-3.13%2B-red?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-black?style=for-the-badge&logo=tkinter&logoColor=red)](https://github.com/TomSchimansky/CustomTkinter)
[![Kernel Driver](https://img.shields.io/badge/EC_Driver-ISW%20%2F%2016W1EMS1-darkred?style=for-the-badge&logo=linux&logoColor=white)](#hardware-controls)
[![Device](https://img.shields.io/badge/Hardware-MSI%20GF65%20Thin%2010UE-crimson?style=for-the-badge&logo=msi&logoColor=white)](#overview)
[![Platform](https://img.shields.io/badge/OS-Linux%20%2F%20KDE%20Plasma-222?style=for-the-badge&logo=kde&logoColor=red)](#quick-start)
[![Theme](https://img.shields.io/badge/Aesthetic-MSI%20Racing%20Red-black?style=for-the-badge&logo=databricks&logoColor=red)](#theme--styling)

<br/>

<img src="assets/zane_mega_center_preview.png" alt="Zane Mega Center Live Dashboard" width="940" style="border-radius: 8px; border: 2px solid #991515; box-shadow: 0 0 25px rgba(255, 30, 40, 0.4);"/>

*Live System Telemetry — Real-time Thermals, Power Matrix, Fan Curves & Direct Controller Space Command Link*

---

</div>

## 🌌 Overview

**Zane Mega Center** is a high-performance system tuning suite and hardware telemetry cockpit built for Linux on the **MSI GF65 Thin 10UE** (and compatible hardware). Designed with an aggressive, pure **Black & Red Cyberpunk / MSI Racing** aesthetic, it unites real-time hardware telemetry, active EC fan curve management, battery longevity protection, a deep one-click system cleaner, and native command integration with [**Controller Space**](https://github.com/ZaneGoat/Controler-space).

Whether you are pushing your system to the edge in **Extreme Mode**, monitoring thermal headroom with live 60-second telemetry graphs, maintaining Li-ion cell health, or launching your controller flight deck, Zane Mega Center provides instantaneous, centralized command.

---

## ⚡ Key Modules & Flight Deck Capabilities

### 📊 1. Realtime Thermal Telemetry
- **Live 60-Sample Waveform Plotter**: Integrated Matplotlib canvas rendering CPU and GPU temperature curves dynamically updated via asynchronous telemetry threads.
- **Instant Thermal Badges**: Real-time readouts showing CPU temperature, fan percentage/RPM, and GPU temperature.
- **Embedded ISW Integration**: Direct interface with the Embedded Controller (EC section `16W1EMS1`) for zero-overhead, hardware-level sensor readings.

### 🔥 2. Power Profiles & Display Switching
- **🔥 Extreme Mode**: Engages 144Hz high-refresh display output (`kscreen-doctor`), unblocks Bluetooth, switches TLP to high-performance AC mode, and turns on Cooler Boost.
- **⚖️ Balance Mode**: Switches display to power-efficient 48Hz, activates smart automatic fan curves, and restores balanced TLP defaults.
- **🔋 Super Battery Mode**: Forces 48Hz display refresh, blocks Bluetooth radios via `rfkill`, sets TLP to aggressive battery savings, and silences fans.

### ❄️ 3. Fan Controls & Thermal Management
- **❄️ Cooler Boost [ON/OFF]**: Instant hardware trigger overriding the EC to drive dual cooling fans to 100% maximum RPM.
- **🤖 Smart Boost Thermostat**: Intelligent background watcher that automatically engages Cooler Boost if the CPU reaches or exceeds **80°C**, and gracefully restores automatic fan curves once temperatures cool below **70°C**.
- **Secondary Fan Curves**: Single-click toggles to apply the custom GF65 curve or restore factory BIOS auto curves.

### 🔋 4. Battery Health Preserver
- **Direct EC Charge Capping**: Extends Li-ion battery lifecycle by capping maximum AC charge levels directly in the laptop's Embedded Controller:
  - **60% (Max Life)**: Recommended for permanent AC desktop use to prevent cell swelling and oxidation.
  - **80% (Balanced)**: Ideal balance of mobility and battery preservation.
  - **100% (Full Trip)**: Full charge capacity for travel.
- **Hardware Detection**: Automatically queries EC register `0xef` on boot to display the active charge threshold.

### 🎮 5. Controller Space Command Deck Integration
- **Header Launcher**: Instant `🎮 CONTROLLER SPACE` quick-access button always available in the top title bar.
- **Hardware Tab Quick Card**: Direct `🚀 START` launcher right inside the Hardware & Power tab.
- **Dedicated Flight Deck Tab**:
  - **Start / Stop / Restart**: Asynchronously executes `start.sh` with live PID monitoring (`● RUNNING` / `● OFFLINE`).
  - **Live Console Streaming**: Embedded terminal log displaying real-time output from `start.sh` and DearPyGui.
  - **Project Links**: One-click shortcuts to open the local Controller Space folder in file manager (`xdg-open`) and view the [GitHub repository](https://github.com/ZaneGoat/Controler-space).
  - **Subsystem Launcher**: Direct launcher for the standalone Warp Core LED & Rumble matrix (`led.py`).

### 🧹 6. System Cleaner & Memory Purge Matrix
- **12 Automated Maintenance Modules**:
  - 🧠 *RAM Cache & Memory Compaction* (`vm.drop_caches=3` + `vm.compact_memory=1`)
  - 🔄 *Swap Memory Reset* (`swapoff -a && swapon -a`)
  - 📦 *APT Package Cache Clean & Autoremove*
  - 🐍 *Python Pip Cache Purge*
  - 📜 *Systemd Journal Vacuum* (capped to 100M)
  - 🗑️ *User Trash Bin Purge*
  - 🖼️ *Thumbnail Cache Cleanup*
  - 📦 *Flatpak Unused Runtimes Removal*
  - ⚡ *Snap Package Cache Vacuum*
  - 🐳 *Docker Container & Image Pruning*
  - 🗄️ *Old /tmp File Cleanup*
  - 🧹 *General User ~/.cache Maintenance*
- **Live Resource Gauges**: Progress bars and live statistics for memory (RAM) and root storage (`/`).
- **Interactive Console Log**: Terminal output window with color-coded success markers (`[✓]`) and execution timing.

---

## 📸 Flight Deck Screenshots

<div align="center">

### 🎮 Controller Space Flight Deck Tab
<img src="assets/zane_mega_center_controller.png" alt="Controller Space Tab" width="900" style="border-radius: 8px; border: 2px solid #991515; box-shadow: 0 0 20px rgba(255, 30, 40, 0.3); margin-bottom: 25px;"/>

*Dedicated Controller Space command hub with live PID tracking, process controls, links, and terminal stream*

### 🧹 System Cleaner & Memory Purge Tab
<img src="assets/zane_mega_center_cleaner.png" alt="System Cleaner Tab" width="900" style="border-radius: 8px; border: 2px solid #991515; box-shadow: 0 0 20px rgba(255, 30, 40, 0.3);"/>

*One-click system optimization matrix with individual module switches and live resource gauges*

</div>

---

## 🛠️ System Architecture

```mermaid
flowchart TD
    subgraph UI ["🖥️ Zane Mega Center GUI (CustomTkinter)"]
        HDR["⚡ Title Bar & Quick Controller Launcher"]
        TAB_HW["📊 Tab 1: Hardware & Power Profiles"]
        TAB_CTRL["🎮 Tab 2: Controller Space Hub"]
        TAB_CLN["🧹 Tab 3: System Cleaner & Terminal Log"]
    end

    subgraph Core ["⚡ Background Management Engines"]
        MON["📡 Realtime Thermal Monitor Loop (isw -r 1)"]
        SMART["🤖 Smart Boost Watcher (80°C Threshold)"]
        CTRL_PROC["🛸 Controller Space Subprocess (start.sh)"]
        CLN_EXEC["⚙️ Sudo Clean Runner (sync / apt / docker / cache)"]
    end

    subgraph Hardware ["💻 Hardware & Kernel Layer"]
        EC["🎛️ MSI EC (16W1EMS1 via /usr/local/bin/isw)"]
        KSCREEN["🖥️ Display Server (kscreen-doctor 144Hz/48Hz)"]
        TLP["🔋 Power Architecture (sudo tlp)"]
        DS4["🎮 Controller Space (DearPyGui / SDL Gamepad)"]
    end

    HDR --> TAB_CTRL
    TAB_HW --> MON
    TAB_HW --> SMART
    TAB_HW --> EC
    TAB_HW --> KSCREEN
    TAB_HW --> TLP
    TAB_CTRL --> CTRL_PROC
    CTRL_PROC --> DS4
    TAB_CLN --> CLN_EXEC
    MON --> EC
```

---

## 🚀 Quick Start

### 1. Fast Setup
Run the automated installer to set up desktop entries and permissions:

```bash
cd ~/ZaneMegaCenter
bash install.sh
```

### 2. Launching Zane Mega Center
Launch directly from your desktop applications menu, run the desktop shortcut, or launch via terminal:

```bash
# Launch installed script
~/.local/bin/ZaneMegaCenter.py

# Or launch local repository
python3 ZaneMegaCenter.py
```

> [!NOTE]
> On first launch, Zane Mega Center automatically bootstraps its isolated virtual environment (`~/.local/share/zanemegacenter/venv`) and installs `customtkinter`, `psutil`, and `matplotlib`.

### 3. Requirements
- **Python 3.10+**
- **ISW (Ice-Sealed Wyvern)** installed at `/usr/local/bin/isw`
- **Linux** (Tested on Debian / Ubuntu / Kali / KDE Plasma)
- **Controller Space** located at `~/Desktop/Controler space` or `~/controller-dashboard`

---

## 🎨 Theme & Palette

| Element | Color Hex | Preview |
| :--- | :--- | :--- |
| **Main Background** | `#0a0a0a` | `Dark Onyx` |
| **Panel Background** | `#121212` | `Jet Carbon` |
| **Card / Element BG** | `#181818` | `Deep Obsidian` |
| **MSI Racing Red** | `#cc0000` | `Primary Red` |
| **Alert Bright Red** | `#ff1a1a` | `Glowing Crimson` |
| **Blood Red Accent** | `#8B0000` | `Dark Crimson` |
| **Status Ready Green** | `#44bb44` | `Cyber Green` |

---

## 🔗 Connected Ecosystem

- [**Controller Space (Starship Flight Deck)**](https://github.com/ZaneGoat/Controler-space): 1000Hz low-latency DualShock 4 & gamepad telemetry matrix.
- [**ISW Fan Control**](https://github.com/YoyPa/isw): EC fan control for MSI laptops.

---

<div align="center">
  <b>ZANE MEGA CENTER</b> // <i>Engineered for Maximum Hardware Performance</i> ⚡
</div>
