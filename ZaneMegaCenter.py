#!/usr/bin/env python3
"""
Zane Mega Center — Ultimate System Control & Cleaner
Black & Red Gaming Edition | MSI GF65 Thin 10UE
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import threading
import time
import re
import collections
import tkinter as tk

import socket

# --- Single Instance Lock ---
def enforce_single_instance():
    try:
        global _single_instance_socket
        _single_instance_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        _single_instance_socket.bind('\0zanemegacenter_lock')
    except socket.error:
        print("Zane Mega Center is already running. Exiting.")
        sys.exit(0)

enforce_single_instance()

# --- Virtual Environment Bootstrap ---
VENV_DIR = Path.home() / ".local" / "share" / "zanemegacenter" / "venv"
VENV_PYTHON = VENV_DIR / "bin" / "python3"

def setup_venv_and_relaunch():
    if not VENV_PYTHON.exists():
        print("First run detected. Setting up virtual environment...")
        VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print("Installing dependencies (customtkinter, psutil, matplotlib)...")
        subprocess.run([str(VENV_DIR / "bin" / "pip"), "install", "customtkinter", "psutil", "matplotlib"], check=True)
        print("Setup complete. Relaunching...")
    
    if sys.executable != str(VENV_PYTHON):
        os.execl(str(VENV_PYTHON), str(VENV_PYTHON), *sys.argv)

setup_venv_and_relaunch()

# --- Application Logic ---
import customtkinter as ctk
import psutil
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- Theme Constants (Pure Black & Red Gaming Palette) ---
BG_DARK      = "#0a0a0a"   # Main background
BG_PANEL     = "#121212"   # Container panels
BG_CARD      = "#181818"   # Inner cards & controls
BG_ELEVATED  = "#222222"   # Elevated elements
BORDER_DARK  = "#2a1515"   # Subtle red-tinted border
RED_CRIMSON  = "#8B0000"   # Deep blood red
RED_PRIMARY  = "#cc0000"   # MSI racing red
RED_BRIGHT   = "#ff1a1a"   # Glowing red alert
RED_GLOW     = "#ff4444"   # Highlight red
RED_SUBTLE   = "#3d0a0a"   # Subtle red background
TEXT_MAIN    = "#f0f0f0"   # Crisp white
TEXT_MUTED   = "#888888"   # Slate gray
TEXT_RED     = "#ff5555"   # Accent text
GREEN_OK     = "#44bb44"   # Secondary success

# --- Hardware Constants ---
ISW_BIN      = "/usr/local/bin/isw"
ISW_SECTION  = "16W1EMS1"
MODEL_NAME   = "MSI GF65 Thin 10UE"

def run_isw(*args):
    cmd = ["sudo", ISW_BIN] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return r.stdout, r.stderr, r.returncode
    except Exception as e:
        return "", str(e), 1

def parse_isw_r(text):
    result = dict(cpu_t="--", cpu_fs="--", cpu_fr="--", gpu_t="--", gpu_fs="--", gpu_fr="--")
    for line in text.splitlines():
        if "│" not in line: 
            continue
        clean = re.sub(r'\x1b\[[0-9;]*m', '', line)
        cells = [c.strip() for c in clean.split("│") if c.strip()]
        if len(cells) < 4: 
            continue
        try:
            result["cpu_t"]  = cells[0].replace("°C", "").strip()
            parts1 = cells[1].split()
            result["cpu_fs"] = parts1[0].replace("%", "").strip() if len(parts1) > 0 else "--"
            result["cpu_fr"] = parts1[1].replace("RPM", "").strip() if len(parts1) > 1 else "--"
            result["gpu_t"]  = cells[2].replace("°C", "").strip()
            parts3 = cells[3].split()
            result["gpu_fs"] = parts3[0].replace("%", "").strip() if len(parts3) > 0 else "--"
            result["gpu_fr"] = parts3[1].replace("RPM", "").strip() if len(parts3) > 1 else "--"
            if result["cpu_t"].lstrip("-").isdigit(): 
                return result
        except: 
            continue
    return result

class SudoDialog(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Authentication Required")
        self.geometry("420x220")
        self.configure(fg_color=BG_DARK)
        self.password = None
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()

        card = ctk.CTkFrame(self, fg_color=BG_PANEL, border_color=RED_CRIMSON, border_width=1, corner_radius=10)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        self.label = ctk.CTkLabel(card, text="AUTHENTICATION REQUIRED", font=("Helvetica", 14, "bold"), text_color=RED_PRIMARY)
        self.label.pack(pady=(15, 5))

        self.sublabel = ctk.CTkLabel(card, text="Root privileges required for system actions:", font=("Helvetica", 11), text_color=TEXT_MUTED)
        self.sublabel.pack(pady=(0, 10))

        self.entry = ctk.CTkEntry(card, show="*", width=280, fg_color=BG_CARD, border_color=BORDER_DARK, text_color=TEXT_MAIN)
        self.entry.pack(pady=5)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.submit)

        self.btn = ctk.CTkButton(card, text="CONFIRM", font=("Helvetica", 12, "bold"),
                                 fg_color=RED_PRIMARY, hover_color=RED_BRIGHT, text_color=TEXT_MAIN, command=self.submit)
        self.btn.pack(pady=(12, 10))

    def submit(self, event=None):
        self.password = self.entry.get()
        self.destroy()

class ZaneMegaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"ZANE MEGA CENTER // {MODEL_NAME}")
        self.geometry("1020x800")
        self.minsize(980, 750)
        self.configure(fg_color=BG_DARK)

        # Matplotlib history
        self.history_len = 60
        self.cpu_history = collections.deque([0]*self.history_len, maxlen=self.history_len)
        self.gpu_history = collections.deque([0]*self.history_len, maxlen=self.history_len)

        self.boost_on = False
        self.active_mode = None
        self.current_battery_limit = None
        self.monitoring = True

        self._build_header()
        self._build_tabview()
        self._build_statusbar()

        self.update_stats()
        self._detect_initial_battery_limit()
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    # ── Header ───────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=60)
        hdr.pack(fill="x", padx=0, pady=0)

        left_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=10)

        logo = ctk.CTkLabel(left_frame, text="⚡ ZANE MEGA CENTER", font=("Helvetica", 18, "bold"), text_color=RED_PRIMARY)
        logo.pack(side="left")

        tag = ctk.CTkLabel(left_frame, text=" | LINUX EDITION", font=("Helvetica", 11, "bold"), text_color=TEXT_MUTED)
        tag.pack(side="left", padx=5)

        right_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=10)

        model_lbl = ctk.CTkLabel(right_frame, text=f"DEVICE: {MODEL_NAME}", font=("Helvetica", 11, "bold"), text_color=TEXT_MUTED)
        model_lbl.pack(side="right")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    def _build_tabview(self):
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=BG_DARK,
            segmented_button_fg_color=BG_PANEL,
            segmented_button_selected_color=RED_CRIMSON,
            segmented_button_selected_hover_color=RED_PRIMARY,
            segmented_button_unselected_color=BG_CARD,
            segmented_button_unselected_hover_color=BG_ELEVATED,
            text_color=TEXT_MAIN
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 0))

        self.tab_hw = self.tabview.add("  HARDWARE & POWER  ")
        self.tab_clean = self.tabview.add("  SYSTEM CLEANER  ")

        self.setup_hw_tab()
        self.setup_cleaner_tab()

    # ── Status Bar ───────────────────────────────────────────────────────────
    def _build_statusbar(self):
        sb = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=35)
        sb.pack(fill="x", side="bottom")

        self.status_dot = ctk.CTkLabel(sb, text="●", font=("Helvetica", 14), text_color=RED_PRIMARY)
        self.status_dot.pack(side="left", padx=(15, 6), pady=4)

        self.status_lbl = ctk.CTkLabel(sb, text="System Ready", font=("Helvetica", 11), text_color=TEXT_MUTED, anchor="w")
        self.status_lbl.pack(side="left", fill="x", expand=True, pady=4)

    def set_status(self, msg, color=RED_PRIMARY):
        self.status_lbl.configure(text=msg)
        self.status_dot.configure(text_color=color)

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 1: HARDWARE & POWER
    # ═════════════════════════════════════════════════════════════════════════
    def setup_hw_tab(self):
        self.tab_hw.grid_columnconfigure(0, weight=1)
        self.tab_hw.grid_rowconfigure(0, weight=0) # Chart
        self.tab_hw.grid_rowconfigure(1, weight=0) # Power modes
        self.tab_hw.grid_rowconfigure(2, weight=1) # Fan & Battery controls

        # 1. Live Matplotlib Temperature Chart Frame
        chart_card = ctk.CTkFrame(self.tab_hw, fg_color=BG_PANEL, border_color=BORDER_DARK, border_width=1, corner_radius=8)
        chart_card.grid(row=0, column=0, padx=10, pady=(5, 8), sticky="nsew")

        # Top row of chart card: Live readout badges
        badge_row = ctk.CTkFrame(chart_card, fg_color="transparent")
        badge_row.pack(fill="x", padx=15, pady=(8, 0))

        title_lbl = ctk.CTkLabel(badge_row, text="REALTIME THERMAL TELEMETRY", font=("Helvetica", 12, "bold"), text_color=TEXT_MAIN)
        title_lbl.pack(side="left")

        self.gpu_badge = ctk.CTkLabel(badge_row, text="GPU: --°C | --%", font=("Helvetica", 12, "bold"),
                                      text_color="#ff7777", fg_color=BG_CARD, corner_radius=6, padx=10, pady=4)
        self.gpu_badge.pack(side="right", padx=(6, 0))

        self.cpu_badge = ctk.CTkLabel(badge_row, text="CPU: --°C | --%", font=("Helvetica", 12, "bold"),
                                      text_color=RED_BRIGHT, fg_color=BG_CARD, corner_radius=6, padx=10, pady=4)
        self.cpu_badge.pack(side="right")

        # Matplotlib Figure
        self.fig = Figure(figsize=(9, 2.2), dpi=100, facecolor=BG_PANEL)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#0e0e0e")
        self.ax.tick_params(colors=TEXT_MUTED, labelsize=9)
        self.ax.grid(True, linestyle="--", alpha=0.18, color="#ffffff")

        for spine in self.ax.spines.values():
            spine.set_color(BORDER_DARK)
            spine.set_linewidth(0.8)

        self.line_cpu, = self.ax.plot([], [], color=RED_BRIGHT, label="CPU Temp (°C)", linewidth=2.0)
        self.line_gpu, = self.ax.plot([], [], color="#ff8888", label="GPU Temp (°C)", linewidth=1.8, linestyle="--")

        legend = self.ax.legend(facecolor="#161616", edgecolor=BORDER_DARK, labelcolor=TEXT_MAIN, loc="upper left", fontsize=8)
        legend.get_frame().set_alpha(0.8)

        self.ax.set_xlim(0, self.history_len - 1)
        self.ax.set_ylim(20, 100)
        self.fig.tight_layout(pad=1.2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        # 2. Power Profiles Section
        power_card = ctk.CTkFrame(self.tab_hw, fg_color=BG_PANEL, border_color=BORDER_DARK, border_width=1, corner_radius=8)
        power_card.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")

        p_title = ctk.CTkLabel(power_card, text="POWER PROFILES", font=("Helvetica", 12, "bold"), text_color=TEXT_MAIN)
        p_title.pack(anchor="w", padx=15, pady=(8, 4))

        p_buttons = ctk.CTkFrame(power_card, fg_color="transparent")
        p_buttons.pack(fill="x", padx=10, pady=(0, 10))
        p_buttons.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_extreme = ctk.CTkButton(
            p_buttons, text="🔥 EXTREME\n144Hz | Max Fans | Full Power",
            font=("Helvetica", 12, "bold"),
            fg_color=BG_CARD, hover_color=RED_SUBTLE, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1,
            height=54, corner_radius=8,
            command=lambda: self.set_power("extreme")
        )
        self.btn_extreme.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_balance = ctk.CTkButton(
            p_buttons, text="⚖️ BALANCE\n48Hz | Smart Fans | Daily Use",
            font=("Helvetica", 12, "bold"),
            fg_color=BG_CARD, hover_color=RED_SUBTLE, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1,
            height=54, corner_radius=8,
            command=lambda: self.set_power("balance")
        )
        self.btn_balance.grid(row=0, column=1, padx=5, sticky="ew")

        self.btn_battery = ctk.CTkButton(
            p_buttons, text="🔋 SUPER BATTERY\n48Hz | Silent | Bluetooth Off",
            font=("Helvetica", 12, "bold"),
            fg_color=BG_CARD, hover_color=RED_SUBTLE, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1,
            height=54, corner_radius=8,
            command=lambda: self.set_power("battery")
        )
        self.btn_battery.grid(row=0, column=2, padx=5, sticky="ew")

        # 3. Bottom Controls (Fan Controls & Battery Limits)
        bottom_row = ctk.CTkFrame(self.tab_hw, fg_color="transparent")
        bottom_row.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="nsew")
        bottom_row.grid_columnconfigure(0, weight=3)
        bottom_row.grid_columnconfigure(1, weight=2)

        # Fan Control Card
        fan_card = ctk.CTkFrame(bottom_row, fg_color=BG_PANEL, border_color=BORDER_DARK, border_width=1, corner_radius=8)
        fan_card.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        f_title = ctk.CTkLabel(fan_card, text="FAN CONTROLS & THERMAL MANAGEMENT", font=("Helvetica", 12, "bold"), text_color=TEXT_MAIN)
        f_title.pack(anchor="w", padx=15, pady=(8, 6))

        # Cooler Boost & Smart Boost Row
        cb_row = ctk.CTkFrame(fan_card, fg_color="transparent")
        cb_row.pack(fill="x", padx=12, pady=(0, 8))
        cb_row.grid_columnconfigure(0, weight=1)
        cb_row.grid_columnconfigure(1, weight=1)

        self.boost_btn = ctk.CTkButton(
            cb_row, text="❄️ COOLER BOOST [OFF]",
            font=("Helvetica", 12, "bold"),
            fg_color=BG_CARD, hover_color=RED_CRIMSON, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1,
            height=40, corner_radius=6,
            command=self.toggle_boost
        )
        self.boost_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        smart_box = ctk.CTkFrame(cb_row, fg_color=BG_CARD, border_color=BORDER_DARK, border_width=1, corner_radius=6, height=40)
        smart_box.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        smart_box.pack_propagate(False)

        self.smart_boost_var = ctk.BooleanVar(value=False)
        self.smart_boost_switch = ctk.CTkSwitch(
            smart_box, text="🤖 Smart Boost (>80°C)",
            font=("Helvetica", 11, "bold"),
            variable=self.smart_boost_var,
            progress_color=RED_PRIMARY,
            button_color=TEXT_MAIN,
            button_hover_color=RED_BRIGHT
        )
        self.smart_boost_switch.pack(side="left", padx=12, pady=8)

        # Secondary Fan Curves Row
        sec_fan = ctk.CTkFrame(fan_card, fg_color="transparent")
        sec_fan.pack(fill="x", padx=12, pady=(0, 10))
        sec_fan.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            sec_fan, text="Apply GF65 Custom Curve",
            font=("Helvetica", 11),
            fg_color=BG_CARD, hover_color=BG_ELEVATED, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1,
            height=32, corner_radius=6,
            command=lambda: self.run_isw_cmd("-w", ISW_SECTION)
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        ctk.CTkButton(
            sec_fan, text="Reset to BIOS Auto",
            font=("Helvetica", 11),
            fg_color=BG_CARD, hover_color=BG_ELEVATED, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1,
            height=32, corner_radius=6,
            command=lambda: self.run_isw_cmd("-b", "off")
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Battery Charge Limit Card
        bat_card = ctk.CTkFrame(bottom_row, fg_color=BG_PANEL, border_color=BORDER_DARK, border_width=1, corner_radius=8)
        bat_card.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        b_hdr = ctk.CTkFrame(bat_card, fg_color="transparent")
        b_hdr.pack(fill="x", padx=15, pady=(8, 2))

        b_title = ctk.CTkLabel(b_hdr, text="BATTERY HEALTH LIMIT", font=("Helvetica", 12, "bold"), text_color=TEXT_MAIN)
        b_title.pack(side="left")

        self.bat_status_badge = ctk.CTkLabel(
            b_hdr, text="DETECTING...", font=("Helvetica", 11, "bold"),
            text_color=RED_BRIGHT, fg_color=BG_CARD, corner_radius=6, padx=8, pady=2
        )
        self.bat_status_badge.pack(side="right")

        b_desc = ctk.CTkLabel(bat_card, text="Caps AC charging to preserve Li-ion cells:", font=("Helvetica", 10), text_color=TEXT_MUTED)
        b_desc.pack(anchor="w", padx=15, pady=(0, 6))

        bat_btns = ctk.CTkFrame(bat_card, fg_color="transparent")
        bat_btns.pack(fill="x", padx=12, pady=(0, 10))
        bat_btns.grid_columnconfigure((0, 1, 2), weight=1)

        self.bat_btn_60 = ctk.CTkButton(
            bat_btns, text="60%\nMax Life", font=("Helvetica", 11, "bold"),
            fg_color=BG_CARD, hover_color=RED_SUBTLE, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1, height=45, corner_radius=6,
            command=lambda: self.set_battery_limit(60)
        )
        self.bat_btn_60.grid(row=0, column=0, padx=2, sticky="ew")

        self.bat_btn_80 = ctk.CTkButton(
            bat_btns, text="80%\nBalanced", font=("Helvetica", 11, "bold"),
            fg_color=BG_CARD, hover_color=RED_SUBTLE, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1, height=45, corner_radius=6,
            command=lambda: self.set_battery_limit(80)
        )
        self.bat_btn_80.grid(row=0, column=1, padx=2, sticky="ew")

        self.bat_btn_100 = ctk.CTkButton(
            bat_btns, text="100%\nFull Trip", font=("Helvetica", 11, "bold"),
            fg_color=BG_CARD, hover_color=RED_SUBTLE, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1, height=45, corner_radius=6,
            command=lambda: self.set_battery_limit(100)
        )
        self.bat_btn_100.grid(row=0, column=2, padx=2, sticky="ew")

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 2: SYSTEM CLEANER
    # ═════════════════════════════════════════════════════════════════════════
    def setup_cleaner_tab(self):
        self.tab_clean.grid_columnconfigure(0, weight=0) # Sidebar
        self.tab_clean.grid_columnconfigure(1, weight=1) # Main View
        self.tab_clean.grid_rowconfigure(0, weight=1)

        # Sidebar with modules
        self.sidebar = ctk.CTkFrame(self.tab_clean, fg_color=BG_PANEL, border_color=BORDER_DARK, border_width=1, width=280, corner_radius=8)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(5, 10), pady=5)
        self.sidebar.grid_propagate(False)

        side_title = ctk.CTkLabel(self.sidebar, text="CLEANUP MODULES", font=("Helvetica", 13, "bold"), text_color=RED_PRIMARY)
        side_title.pack(anchor="w", padx=15, pady=(12, 6))

        scroll_modules = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        scroll_modules.pack(fill="both", expand=True, padx=5, pady=0)

        self.modules = {
            "RAM Cache & Compaction (Sudo)": {"cmd": "sync && sysctl -w vm.drop_caches=3 && sysctl -w vm.compact_memory=1", "sudo": True},
            "Swap Memory Reset (Sudo)": {"cmd": "swapoff -a && swapon -a", "sudo": True},
            "APT Package Cache (Sudo)": {"cmd": "apt-get clean && apt-get autoclean && apt-get autoremove -y", "sudo": True},
            "Python Pip Cache": {"cmd": "pip cache purge", "sudo": False},
            "Systemd Journal Logs (Sudo)": {"cmd": "journalctl --vacuum-size=100M", "sudo": True},
            "User Trash Bin": {"cmd": "rm -rf ~/.local/share/Trash/files/* ~/.local/share/Trash/info/*", "sudo": False},
            "Thumbnail Cache": {"cmd": "rm -rf ~/.cache/thumbnails/* ~/.thumbnails/*", "sudo": False},
            "Flatpak Unused (Sudo)": {"cmd": "flatpak uninstall --unused -y", "sudo": True},
            "Snap Cache (Sudo)": {"cmd": "rm -rf /var/lib/snapd/cache/*", "sudo": True},
            "Docker Prune (Sudo)": {"cmd": "docker container prune -f && docker image prune -f", "sudo": True},
            "/tmp Old Files": {"cmd": "find /tmp -type f -atime +1 -delete", "sudo": False},
            "General ~/.cache Clean": {"cmd": "find ~/.cache -mindepth 1 -maxdepth 1 ! -name 'pip' ! -name 'BraveSoftware' ! -name 'thumbnails' ! -name 'mozilla' ! -name 'google-chrome' -exec rm -rf {} +", "sudo": False}
        }

        self.prefs_file = Path.home() / ".config" / "zaneclearpro" / "prefs.json"
        self.prefs = self.load_prefs()
        self.switches = {}

        for name in self.modules.keys():
            switch = ctk.CTkSwitch(
                scroll_modules, text=name,
                font=("Helvetica", 11),
                command=self.save_prefs,
                progress_color=RED_PRIMARY,
                button_color=TEXT_MAIN,
                button_hover_color=RED_BRIGHT
            )
            switch.pack(anchor="w", padx=10, pady=5)
            if self.prefs.get(name, True):
                switch.select()
            else:
                switch.deselect()
            self.switches[name] = switch

        # Select all / Deselect buttons
        sel_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sel_frame.pack(fill="x", padx=10, pady=(8, 4))
        sel_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            sel_frame, text="Select All", font=("Helvetica", 11),
            fg_color=BG_CARD, hover_color=BG_ELEVATED, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1, height=28,
            command=self.select_all
        ).grid(row=0, column=0, padx=2, sticky="ew")

        ctk.CTkButton(
            sel_frame, text="Deselect All", font=("Helvetica", 11),
            fg_color=BG_CARD, hover_color=BG_ELEVATED, text_color=TEXT_MAIN,
            border_color=BORDER_DARK, border_width=1, height=28,
            command=self.deselect_all
        ).grid(row=0, column=1, padx=2, sticky="ew")

        # RUN CLEANUP Button
        self.run_btn = ctk.CTkButton(
            self.sidebar, text="⚡ RUN SYSTEM CLEANUP",
            font=("Helvetica", 13, "bold"),
            fg_color=RED_CRIMSON, hover_color=RED_PRIMARY, text_color=TEXT_MAIN,
            height=46, corner_radius=6,
            command=self.start_cleanup
        )
        self.run_btn.pack(fill="x", padx=10, pady=(8, 12))

        # Main View (Stats & Live Console)
        main_view = ctk.CTkFrame(self.tab_clean, fg_color="transparent")
        main_view.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        main_view.grid_rowconfigure(0, weight=0)
        main_view.grid_rowconfigure(1, weight=1)
        main_view.grid_columnconfigure(0, weight=1)

        # Resource Progress Bars Card
        stats_card = ctk.CTkFrame(main_view, fg_color=BG_PANEL, border_color=BORDER_DARK, border_width=1, corner_radius=8)
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        stats_card.grid_columnconfigure((0, 1), weight=1)

        # RAM Gauge
        ram_box = ctk.CTkFrame(stats_card, fg_color="transparent")
        ram_box.grid(row=0, column=0, padx=15, pady=12, sticky="ew")

        self.ram_title = ctk.CTkLabel(ram_box, text="MEMORY USAGE (RAM)", font=("Helvetica", 11, "bold"), text_color=TEXT_MAIN)
        self.ram_title.pack(anchor="w")

        self.ram_bar = ctk.CTkProgressBar(ram_box, progress_color=RED_PRIMARY, fg_color=BG_CARD, height=14, corner_radius=4)
        self.ram_bar.pack(fill="x", pady=6)

        self.ram_text = ctk.CTkLabel(ram_box, text="RAM: Loading...", font=("Helvetica", 10), text_color=TEXT_MUTED)
        self.ram_text.pack(anchor="w")

        # Disk Gauge
        disk_box = ctk.CTkFrame(stats_card, fg_color="transparent")
        disk_box.grid(row=0, column=1, padx=15, pady=12, sticky="ew")

        self.disk_title = ctk.CTkLabel(disk_box, text="ROOT STORAGE (/)", font=("Helvetica", 11, "bold"), text_color=TEXT_MAIN)
        self.disk_title.pack(anchor="w")

        self.disk_bar = ctk.CTkProgressBar(disk_box, progress_color="#aa2222", fg_color=BG_CARD, height=14, corner_radius=4)
        self.disk_bar.pack(fill="x", pady=6)

        self.disk_text = ctk.CTkLabel(disk_box, text="Disk: Loading...", font=("Helvetica", 10), text_color=TEXT_MUTED)
        self.disk_text.pack(anchor="w")

        # Terminal Output Box Card
        log_card = ctk.CTkFrame(main_view, fg_color=BG_PANEL, border_color=BORDER_DARK, border_width=1, corner_radius=8)
        log_card.grid(row=1, column=0, sticky="nsew")

        log_hdr = ctk.CTkFrame(log_card, fg_color="transparent")
        log_hdr.pack(fill="x", padx=15, pady=(8, 4))

        ctk.CTkLabel(log_hdr, text="TERMINAL OUTPUT // EXECUTION LOG", font=("Helvetica", 11, "bold"), text_color=TEXT_MAIN).pack(side="left")

        self.log_box = ctk.CTkTextbox(
            log_card,
            font=("Monospace", 11),
            fg_color="#080808",
            text_color="#e0e0e0",
            border_color=BORDER_DARK,
            border_width=1,
            corner_radius=6
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_box.configure(state="disabled")

    # ── Helpers: Cleaner ──────────────────────────────────────────────────────
    def load_prefs(self):
        try:
            if self.prefs_file.exists():
                with open(self.prefs_file, "r") as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_prefs(self):
        try:
            self.prefs_file.parent.mkdir(parents=True, exist_ok=True)
            prefs = {name: (switch.get() == 1) for name, switch in self.switches.items()}
            with open(self.prefs_file, "w") as f:
                json.dump(prefs, f)
        except:
            pass

    def select_all(self):
        for switch in self.switches.values():
            switch.select()
        self.save_prefs()

    def deselect_all(self):
        for switch in self.switches.values():
            switch.deselect()
        self.save_prefs()

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_stats(self):
        try:
            ram = psutil.virtual_memory()
            self.ram_bar.set(ram.percent / 100.0)
            self.ram_text.configure(text=f"{ram.used / (1024**3):.2f} GB / {ram.total / (1024**3):.2f} GB ({ram.percent}%)")

            disk = psutil.disk_usage('/')
            self.disk_bar.set(disk.percent / 100.0)
            self.disk_text.configure(text=f"{disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB ({disk.percent}%)")
        except:
            pass
        self.after(2000, self.update_stats)

    def start_cleanup(self):
        self.run_btn.configure(state="disabled", text="⚡ CLEANING IN PROGRESS...")
        needs_sudo = any(self.switches[name].get() == 1 and info["sudo"] for name, info in self.modules.items())
        sudo_password = None
        if needs_sudo:
            try:
                subprocess.run(["sudo", "-n", "true"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                dialog = SudoDialog(self)
                self.wait_window(dialog)
                sudo_password = dialog.password
                if not sudo_password:
                    self.log("[WARN] Operation cancelled: Root authentication not provided.")
                    self.run_btn.configure(state="normal", text="⚡ RUN SYSTEM CLEANUP")
                    return
        threading.Thread(target=self._run_cleanup_thread, args=(sudo_password,), daemon=True).start()

    def _run_cleanup_thread(self, sudo_password):
        self.log("="*60)
        self.log("STARTING SYSTEM CLEANUP PROTOCOL")
        self.log("="*60)

        for name, info in self.modules.items():
            if self.switches[name].get() == 1:
                self.log(f"[*] Executing: {name}...")
                cmd = f"sudo -S bash -c \"{info['cmd']}\"" if info["sudo"] else f"bash -c \"{info['cmd']}\""
                try:
                    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    out, _ = p.communicate(input=sudo_password + '\n' if info["sudo"] and sudo_password else None)
                    if p.returncode == 0:
                        self.log(f"[✓] {name} completed successfully.")
                    else:
                        cleaned = out.replace('[sudo] password for zane: ', '').strip()
                        self.log(f"[!] {name} output: {cleaned}")
                except Exception as e:
                    self.log(f"[ERR] Failed: {str(e)}")

        self.log("="*60)
        self.log("CLEANUP PROTOCOL FINISHED")
        self.log("="*60)
        self.after(0, lambda: self.run_btn.configure(state="normal", text="⚡ RUN SYSTEM CLEANUP"))
        self.after(0, lambda: self.set_status("Cleanup Protocol Completed", GREEN_OK))

    # ── Hardware & Telemetry Loop ─────────────────────────────────────────────
    def monitor_loop(self):
        while self.monitoring:
            out, err, rc = run_isw("-r", "1")
            if out.strip():
                d = parse_isw_r(out)
                self.after(0, self._apply_telemetry, d)
            time.sleep(3)

    def _apply_telemetry(self, d):
        cpu_t_str = d.get("cpu_t", "--")
        gpu_t_str = d.get("gpu_t", "--")
        cpu_fs = d.get("cpu_fs", "--")
        gpu_fs = d.get("gpu_fs", "--")

        self.cpu_badge.configure(text=f"CPU: {cpu_t_str}°C | Fan: {cpu_fs}%")
        self.gpu_badge.configure(text=f"GPU: {gpu_t_str}°C | Fan: {gpu_fs}%")

        # Parse numeric values for plot
        try:
            cpu_val = int(cpu_t_str)
        except:
            cpu_val = 0

        try:
            gpu_val = int(gpu_t_str)
        except:
            gpu_val = 0

        self.cpu_history.append(cpu_val)
        self.gpu_history.append(gpu_val)

        # Smart Boost thermostat logic
        if getattr(self, "smart_boost_var", None) and self.smart_boost_var.get():
            if cpu_val >= 80 and not self.boost_on:
                self.toggle_boost(force="on")
                self.set_status("🔥 Thermal limit reached (>=80°C)! Cooler Boost engaged.", RED_BRIGHT)
            elif cpu_val <= 70 and self.boost_on and self.active_mode != "extreme":
                self.toggle_boost(force="off")
                self.set_status("❄️ Cooled down (<=70°C). Restored Auto fan curve.", GREEN_OK)

        # Update Matplotlib Chart
        try:
            x_vals = range(self.history_len)
            self.line_cpu.set_data(x_vals, self.cpu_history)
            self.line_gpu.set_data(x_vals, self.gpu_history)

            max_val = max(max(self.cpu_history), max(self.gpu_history), 80)
            self.ax.set_ylim(20, max(100, max_val + 5))
            self.canvas.draw_idle()
        except:
            pass

    # ── Power & Hardware Controls ─────────────────────────────────────────────
    def set_power(self, mode):
        self.active_mode = mode
        self.set_status(f"Applying {mode.upper()} mode...", RED_PRIMARY)

        # Highlight active button visually
        self.btn_extreme.configure(
            fg_color=RED_CRIMSON if mode == "extreme" else BG_CARD,
            border_color=RED_PRIMARY if mode == "extreme" else BORDER_DARK
        )
        self.btn_balance.configure(
            fg_color=RED_CRIMSON if mode == "balance" else BG_CARD,
            border_color=RED_PRIMARY if mode == "balance" else BORDER_DARK
        )
        self.btn_battery.configure(
            fg_color=RED_CRIMSON if mode == "battery" else BG_CARD,
            border_color=RED_PRIMARY if mode == "battery" else BORDER_DARK
        )

        if mode == "extreme":
            self.toggle_boost(force="on")
        else:
            self.toggle_boost(force="off")

        def task():
            if mode == "extreme":
                subprocess.run(["kscreen-doctor", "output.1.mode.1"])
                subprocess.run(["rfkill", "unblock", "bluetooth"])
                subprocess.run(["sudo", "tlp", "ac"])
                msg = "🔥 Extreme Mode Active (144Hz + Max Fans)"
            elif mode == "balance":
                subprocess.run(["kscreen-doctor", "output.1.mode.2"])
                subprocess.run(["rfkill", "unblock", "bluetooth"])
                subprocess.run(["sudo", "tlp", "start"])
                msg = "⚖️ Balance Mode Active (48Hz + Auto Fans)"
            elif mode == "battery":
                subprocess.run(["kscreen-doctor", "output.1.mode.2"])
                subprocess.run(["rfkill", "block", "bluetooth"])
                subprocess.run(["sudo", "tlp", "bat"])
                msg = "🔋 Super Battery Active (48Hz + BT Off)"

            subprocess.run(["notify-send", "Zane Mega Center", msg])
            self.after(0, lambda: self.set_status(msg, GREEN_OK))

        threading.Thread(target=task, daemon=True).start()

    def run_isw_cmd(self, flag, val):
        def task():
            self.after(0, lambda: self.set_status(f"Executing ISW {flag} {val}...", RED_PRIMARY))
            out, err, rc = run_isw(flag, val)
            self.after(0, lambda: self.set_status(f"ISW command executed.", GREEN_OK))
        threading.Thread(target=task, daemon=True).start()

    def toggle_boost(self, force=None):
        if force == "on":
            self.boost_on = True
        elif force == "off":
            self.boost_on = False
        else:
            self.boost_on = not self.boost_on

        val = "on" if self.boost_on else "off"
        btn_text = "❄️ COOLER BOOST [ON]" if self.boost_on else "❄️ COOLER BOOST [OFF]"
        btn_color = RED_PRIMARY if self.boost_on else BG_CARD

        self.boost_btn.configure(text=btn_text, fg_color=btn_color)
        self.run_isw_cmd("-b", val)

    def set_battery_limit(self, pct, update_hardware=True):
        self.current_battery_limit = pct
        self.bat_status_badge.configure(text=f"ACTIVE: {pct}%", text_color=RED_BRIGHT if pct != 100 else TEXT_MUTED)

        # Highlight active button visually
        self.bat_btn_60.configure(
            fg_color=RED_CRIMSON if pct == 60 else BG_CARD,
            border_color=RED_PRIMARY if pct == 60 else BORDER_DARK,
            border_width=2 if pct == 60 else 1
        )
        self.bat_btn_80.configure(
            fg_color=RED_CRIMSON if pct == 80 else BG_CARD,
            border_color=RED_PRIMARY if pct == 80 else BORDER_DARK,
            border_width=2 if pct == 80 else 1
        )
        self.bat_btn_100.configure(
            fg_color=RED_CRIMSON if pct == 100 else BG_CARD,
            border_color=RED_PRIMARY if pct == 100 else BORDER_DARK,
            border_width=2 if pct == 100 else 1
        )

        if update_hardware:
            def task():
                self.after(0, lambda: self.set_status(f"Setting battery charge limit to {pct}%...", RED_PRIMARY))
                run_isw("-t", str(pct))
                self.after(0, lambda: self.set_status(f"Battery limit set to {pct}% [OK]", GREEN_OK))
            threading.Thread(target=task, daemon=True).start()

    def _detect_initial_battery_limit(self):
        def task():
            out, err, rc = run_isw("-p", ISW_SECTION)
            m = re.search(r"0x[0-9a-fA-F]+\((\d+)\)\s+0xef", out)
            if m:
                val = int(m.group(1))
                thresh = val - 128 if val > 128 else (100 if val == 128 else val)
                if thresh in (60, 80, 100):
                    self.after(0, lambda: self.set_battery_limit(thresh, update_hardware=False))
                else:
                    self.after(0, lambda: self.set_battery_limit(100, update_hardware=False))
            else:
                self.after(0, lambda: self.set_battery_limit(100, update_hardware=False))
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    app = ZaneMegaApp()
    app.mainloop()
