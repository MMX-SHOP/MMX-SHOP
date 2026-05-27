import keyboard
import mouse
import customtkinter as ctk
import screeninfo
import configparser
import os
import time
import threading
import ctypes
import ast
import tkinter as tk  # Import tkinter for the Listbox
from tkinter import messagebox  # Import messagebox for confirmation dialogs
from tkinter import ttk

aimCheck = False
xValue = 0
yValue = 0
delayValue = 10
hotkey = 'p'  # Default hotkey

# Check if config file exists, if not create it
if not os.path.isfile('config.txt'):
    print('config.txt file not found. Creating new one...')
    with open('config.txt', 'w') as fp:
        pass
    config = configparser.ConfigParser()
    config['hotkey'] = {'hotkey': hotkey}
    config['loadouts'] = {}
    config.write(open('config.txt', 'w'))
    input('Press any key to exit...')
    exit()
else:
    config = configparser.ConfigParser()
    config.read('config.txt')

try:
    hotkey = config['hotkey']['hotkey']
except KeyError:
    print('Hotkey not found, adding hotkey line to config file...')
    config = configparser.ConfigParser()
    config['hotkey'] = {'hotkey': hotkey}
    config['loadouts'] = {}
    config.write(open('config.txt', 'w'))
    input('Press any key to exit...')
    exit()

print('Hotkey is:', hotkey)

# ─── Couleurs ───────────────────────────────────────────
BG_MAIN      = "#0d0d1a"
BG_FRAME     = "#13102b"
BG_CARD      = "#1a1535"
ACCENT       = "#7c3aed"
ACCENT_HOVER = "#6d28d9"
ACCENT_GLOW  = "#9d5cff"
TEXT_WHITE   = "#ffffff"
TEXT_MUTED   = "#a78bfa"

# ─── GUI Setup ──────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

gui = ctk.CTk()
gui.title("MMX-SHOP")

x, y = getResolution()
size = min(int(x / 5), int(y / 1.5))
gui.geometry(f'{size}x{size}')
gui.configure(fg_color=BG_MAIN)

# ─── Onglets ─────────────────────────────────────────────
style = ttk.Style()
style.theme_use('default')
style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
style.configure("TNotebook.Tab",
    background=BG_CARD, foreground=TEXT_MUTED,
    padding=[16, 7], font=('Segoe UI', 10, 'bold'), borderwidth=0)
style.map("TNotebook.Tab",
    background=[("selected", ACCENT)],
    foreground=[("selected", TEXT_WHITE)])

tab_view = ttk.Notebook(gui)
tab_view.pack(fill="both", expand=True, padx=10, pady=10)

main_tab = ctk.CTkFrame(tab_view, fg_color=BG_MAIN)
tab_view.add(main_tab, text="  Recoil  ")

settings_tab = ctk.CTkFrame(tab_view, fg_color=BG_MAIN)
tab_view.add(settings_tab, text="  Loadouts  ")

# ─── Header ──────────────────────────────────────────────
header = ctk.CTkFrame(main_tab, fg_color=BG_CARD, corner_radius=14)
header.pack(fill="x", padx=12, pady=(12, 6))

ctk.CTkLabel(header, text="MMX-SHOP",
    font=("Segoe UI", 17, "bold"),
    text_color=ACCENT_GLOW).pack(side="left", padx=14, pady=10)

ctk.CTkLabel(header, text="v1.0",
    font=("Segoe UI", 10),
    text_color=TEXT_MUTED).pack(side="left")

# ─── Aim Check ───────────────────────────────────────────
aimCheckButton = ctk.CTkButton(
    main_tab, text="○  Aim Check  OFF",
    command=toggleAimCheck,
    fg_color=BG_CARD, hover_color=ACCENT,
    font=("Segoe UI", 11, "bold"),
    text_color=TEXT_MUTED,
    corner_radius=10, height=38,
    border_width=1, border_color=ACCENT)
aimCheckButton.pack(pady=(6, 4), padx=12, fill="x")

# ─── Sliders ─────────────────────────────────────────────
def makeSlider(parent, label, from_, to, default, unit=""):
    frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12)
    frame.pack(pady=4, padx=12, fill="x")

    ctk.CTkLabel(frame, text=label,
        font=("Segoe UI", 10, "bold"),
        text_color=TEXT_MUTED, width=80, anchor="w").pack(side="left", padx=(14, 0), pady=12)

    val_label = ctk.CTkLabel(frame,
        text=f"{default}{unit}",
        font=("Segoe UI", 10, "bold"),
        text_color=ACCENT_GLOW, width=55, anchor="e")
    val_label.pack(side="right", padx=14)

    slider = ctk.CTkSlider(frame,
        from_=from_, to=to,
        button_color=ACCENT_GLOW,
        button_hover_color=ACCENT,
        progress_color=ACCENT,
        fg_color="#2a2250",
        command=lambda v: val_label.configure(text=f"{int(v)}{unit}"))
    slider.set(default)
    slider.pack(side="left", padx=(8, 8), fill="x", expand=True)

    return slider, val_label

xControl,  xValueLabel    = makeSlider(main_tab, "X Control", -5, 10, 0)
yControl,  yValueLabel    = makeSlider(main_tab, "Y Control",  0,  8, 0)
delay,     delayValueLabel = makeSlider(main_tab, "Delay",      1, 30, 10, " ms")

# ─── Apply Button ─────────────────────────────────────────
setButton = ctk.CTkButton(
    main_tab, text="APPLY",
    command=setValues,
    fg_color=ACCENT, hover_color=ACCENT_HOVER,
    font=("Segoe UI", 12, "bold"),
    text_color=TEXT_WHITE,
    corner_radius=10, height=40,
    border_width=1, border_color=ACCENT_GLOW)
setButton.pack(pady=10, padx=12, fill="x")

# ─── Loadouts Tab ─────────────────────────────────────────
ctk.CTkLabel(settings_tab, text="Loadouts",
    font=("Segoe UI", 15, "bold"),
    text_color=ACCENT_GLOW).pack(pady=(16, 6))

loadoutName = ctk.CTkEntry(settings_tab,
    placeholder_text="Loadout name...",
    fg_color=BG_CARD, border_color=ACCENT,
    text_color=TEXT_WHITE,
    placeholder_text_color=TEXT_MUTED,
    corner_radius=10, height=38)
loadoutName.pack(pady=4, padx=12, fill="x")

ctk.CTkButton(settings_tab, text="SAVE",
    command=saveLoadout,
    fg_color=ACCENT, hover_color=ACCENT_HOVER,
    font=("Segoe UI", 11, "bold"),
    corner_radius=10, height=36).pack(pady=4, padx=12, fill="x")

ctk.CTkButton(settings_tab, text="LOAD",
    command=showLoadoutSelection,
    fg_color=BG_CARD, hover_color=ACCENT,
    font=("Segoe UI", 11, "bold"),
    text_color=TEXT_WHITE,
    corner_radius=10, height=36,
    border_width=1, border_color=ACCENT).pack(pady=4, padx=12, fill="x")

# ─── Hotkey ───────────────────────────────────────────────
ctk.CTkLabel(settings_tab, text="Hotkey",
    font=("Segoe UI", 12, "bold"),
    text_color=ACCENT_GLOW).pack(pady=(14, 4))

hotkeyFrame = ctk.CTkFrame(settings_tab, fg_color=BG_CARD, corner_radius=12)
hotkeyFrame.pack(pady=4, padx=12, fill="x")

ctk.CTkLabel(hotkeyFrame, text="Key :",
    font=("Segoe UI", 10),
    text_color=TEXT_MUTED).pack(side="left", padx=12, pady=10)

hotkeyEntry = ctk.CTkEntry(hotkeyFrame,
    width=60, fg_color=BG_MAIN,
    border_color=ACCENT,
    text_color=TEXT_WHITE, corner_radius=8)
hotkeyEntry.insert(0, hotkey)
hotkeyEntry.pack(side="left", padx=6)

ctk.CTkButton(hotkeyFrame, text="UPDATE",
    command=updateHotkey,
    fg_color=ACCENT, hover_color=ACCENT_HOVER,
    font=("Segoe UI", 10, "bold"),
    corner_radius=8, height=30).pack(side="left", padx=8)
# Start of macro code
enabled = False

def moveRel(x, y):
    ctypes.windll.user32.mouse_event(0x0001, x, y, 0, 0)

def toggleMacro():
    global enabled
    enabled = not enabled
    if enabled:
        ctypes.windll.user32.MessageBeep(0xFFFFFFFF)  # Beep sound when enabling
    else:
        ctypes.windll.user32.MessageBeep(0x00000010)  # Beep sound when disabling
    print('Script Enabled!' if enabled else 'Script Disabled')

# Set the initial hotkey listener
keyboard.add_hotkey(hotkey, toggleMacro)

def leftClicked():
    return ctypes.windll.user32.GetAsyncKeyState(0x01) != 0

def rightClicked():
    return ctypes.windll.user32.GetAsyncKeyState(0x02) != 0

def macroTask():
    while True:
        if enabled:
            if not aimCheck and leftClicked():
                moveRel(xValue, yValue)
            elif aimCheck and leftClicked() and rightClicked():
                moveRel(xValue, yValue)
        time.sleep(delayValue / 1000)

thread = threading.Thread(target=macroTask)
thread.daemon = True
thread.start()

# Start main GUI loop
gui.mainloop()
