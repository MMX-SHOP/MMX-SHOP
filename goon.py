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
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

aimCheck = False
xValue = 0
yValue = 0
delayValue = 10
hotkey = 'p'

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
    config = configparser.ConfigParser()
    config['hotkey'] = {'hotkey': hotkey}
    config['loadouts'] = {}
    config.write(open('config.txt', 'w'))
    input('Press any key to exit...')
    exit()

# ─── Couleurs ───────────────────────────────────────────
BG_MAIN      = "#1a0a2e"   # Violet très foncé
BG_FRAME     = "#2d1b4e"   # Violet foncé
ACCENT       = "#7c3aed"   # Violet vif
ACCENT_HOVER = "#6d28d9"   # Violet hover
TEXT_WHITE   = "#ffffff"
TEXT_MUTED   = "#c4b5fd"   # Violet clair
SLIDER_BG    = "#4c1d95"

def setValues():
    global xValue, yValue, delayValue
    xValue = int(xControl.get())
    yValue = int(yControl.get())
    delayValue = int(delay.get())
    xValueLabel.configure(text=f"X: {xValue}")
    yValueLabel.configure(text=f"Y: {yValue}")
    delayValueLabel.configure(text=f"Delay: {delayValue} ms")

def toggleAimCheck():
    global aimCheck
    aimCheck = not aimCheck
    if aimCheck:
        aimCheckButton.configure(text='● Aim Check ON', fg_color=ACCENT, hover_color=ACCENT_HOVER)
    else:
        aimCheckButton.configure(text='○ Aim Check OFF', fg_color=BG_FRAME, hover_color=ACCENT)

def getResolution():
    screens = screeninfo.get_monitors()
    primary_monitor = screens[0]
    return primary_monitor.width, primary_monitor.height

def saveLoadout():
    setValues()
    name = str(loadoutName.get()).strip()
    loadoutName.delete(0, ctk.END)
    config = configparser.ConfigParser()
    config.read('config.txt')
    if not config.has_section('loadouts'):
        config.add_section('loadouts')
    config.set('loadouts', name, f'[{xValue},{yValue},{delayValue}]')
    config.write(open('config.txt', 'w'))

def showLoadoutSelection():
    loadout_names = config.options('loadouts')
    if not loadout_names:
        return

    loadout_window = ctk.CTkToplevel(gui)
    loadout_window.title("Loadouts")
    loadout_window.geometry("280x420")
    loadout_window.configure(fg_color=BG_MAIN)

    ctk.CTkLabel(loadout_window, text="Sélectionner un loadout",
                 font=("Segoe UI", 13, "bold"),
                 text_color=TEXT_WHITE).pack(pady=(15, 5))

    listbox_frame = ctk.CTkFrame(loadout_window, fg_color=BG_FRAME, corner_radius=10)
    listbox_frame.pack(pady=5, padx=15, fill="both", expand=True)

    loadout_listbox = tk.Listbox(
        listbox_frame,
        font=('Segoe UI', 11),
        bg=BG_FRAME,
        fg=TEXT_WHITE,
        selectbackground=ACCENT,
        selectforeground=TEXT_WHITE,
        borderwidth=0,
        highlightthickness=0,
        relief="flat"
    )
    loadout_listbox.pack(pady=8, padx=8, fill="both", expand=True)

    for name in loadout_names:
        loadout_listbox.insert(tk.END, name)

    def confirmLoadout():
        selected_index = loadout_listbox.curselection()
        if selected_index:
            name = loadout_names[selected_index[0]]
            if messagebox.askyesno("Confirmer", f"Charger '{name}' ?"):
                loadLoadout(name)
                loadout_window.destroy()

    ctk.CTkButton(
        loadout_window, text="Charger",
        command=confirmLoadout,
        fg_color=ACCENT, hover_color=ACCENT_HOVER,
        font=("Segoe UI", 12, "bold"),
        corner_radius=8
    ).pack(pady=10, padx=15, fill="x")

def loadLoadout(name=None):
    global xValue, yValue, delayValue
    if name is None:
        setValues()
        name = str(loadoutName.get()).strip()
        loadoutName.delete(0, ctk.END)

    config = configparser.ConfigParser()
    config.read('config.txt')

    try:
        loadout = config['loadouts'][name]
    except KeyError:
        return None

    loadoutList = ast.literal_eval(loadout)
    xValue = loadoutList[0]
    yValue = loadoutList[1]
    delayValue = loadoutList[2]

    xControl.set(loadoutList[0])
    yControl.set(loadoutList[1])
    delay.set(loadoutList[2])
    setValues()

# ─── GUI ────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

gui = ctk.CTk()
gui.title("MMX-SHOP")
gui.configure(fg_color=BG_MAIN)

x, y = getResolution()
size = min(int(x / 5), int(y / 1.5))
gui.geometry(f'{size}x{size}')

# ─── Style des onglets ──────────────────────────────────
style = ttk.Style()
style.theme_use('default')
style.configure("TNotebook",
    background=BG_MAIN,
    borderwidth=0
)
style.configure("TNotebook.Tab",
    background=BG_FRAME,
    foreground=TEXT_MUTED,
    padding=[14, 6],
    font=('Segoe UI', 10, 'bold'),
    borderwidth=0
)
style.map("TNotebook.Tab",
    background=[("selected", ACCENT)],
    foreground=[("selected", TEXT_WHITE)]
)

tab_view = ttk.Notebook(gui)
tab_view.pack(fill="both", expand=True, padx=10, pady=10)

# ─── Onglets ─────────────────────────────────────────────
main_tab = ctk.CTkFrame(tab_view, fg_color=BG_MAIN)
tab_view.add(main_tab, text="  Recoil  ")

settings_tab = ctk.CTkFrame(tab_view, fg_color=BG_MAIN)
tab_view.add(settings_tab, text="  Loadouts  ")

# ─── Header ──────────────────────────────────────────────
header = ctk.CTkFrame(main_tab, fg_color=BG_FRAME, corner_radius=12)
header.pack(fill="x", padx=12, pady=(12, 6))

ctk.CTkLabel(header, text="MMX-SHOP",
             font=("Segoe UI", 16, "bold"),
             text_color=TEXT_WHITE).pack(side="left", padx=14, pady=8)

ctk.CTkLabel(header, text="Recoil Control",
             font=("Segoe UI", 10),
             text_color=TEXT_MUTED).pack(side="left")

# ─── Aim Check ───────────────────────────────────────────
aimCheckButton = ctk.CTkButton(
    main_tab, text="○ Aim Check OFF",
    command=toggleAimCheck,
    fg_color=BG_FRAME, hover_color=ACCENT,
    font=("Segoe UI", 11, "bold"),
    text_color=TEXT_WHITE,
    corner_radius=8, height=36
)
aimCheckButton.pack(pady=(6, 4), padx=12, fill="x")

# ─── Fonction slider ─────────────────────────────────────
def makeSliderRow(parent, label, from_, to, default, unit="", update_label_ref=None):
    frame = ctk.CTkFrame(parent, fg_color=BG_FRAME, corner_radius=10)
    frame.pack(pady=4, padx=12, fill="x")

    ctk.CTkLabel(frame, text=label,
                 font=("Segoe UI", 10, "bold"),
                 text_color=TEXT_MUTED, width=80, anchor="w").pack(side="left", padx=(12, 0), pady=10)

    val_label = ctk.CTkLabel(frame, text=f"{default}{unit}",
                              font=("Segoe UI", 10, "bold"),
                              text_color=TEXT_WHITE, width=55, anchor="e")
    val_label.pack(side="right", padx=12)

    slider = ctk.CTkSlider(frame, from_=from_, to=to,
                            button_color=ACCENT,
                            button_hover_color=ACCENT_HOVER,
                            progress_color=ACCENT,
                            fg_color=SLIDER_BG,
                            command=lambda v: val_label.configure(text=f"{int(v)}{unit}"))
    slider.set(default)
    slider.pack(side="left", padx=(8, 8), fill="x", expand=True)

    return slider, val_label

xControl, xValueLabel     = makeSliderRow(main_tab, "X Control", -5, 10, xValue)
yControl, yValueLabel     = makeSliderRow(main_tab, "Y Control",  0,  8, yValue)
delay,    delayValueLabel  = makeSliderRow(main_tab, "Delay",      1, 30, delayValue, " ms")

setButton = ctk.CTkButton(
    main_tab, text="Appliquer",
    command=setValues,
    fg_color=ACCENT, hover_color=ACCENT_HOVER,
    font=("Segoe UI", 12, "bold"),
    text_color=TEXT_WHITE,
    corner_radius=8, height=38
)
setButton.pack(pady=10, padx=12, fill="x")

# ─── Loadouts Tab ────────────────────────────────────────
ctk.CTkLabel(settings_tab, text="Loadouts",
             font=("Segoe UI", 14, "bold"),
             text_color=TEXT_WHITE).pack(pady=(14, 6))

loadoutName = ctk.CTkEntry(
    settings_tab, placeholder_text="Nom du loadout...",
    fg_color=BG_FRAME, border_color=ACCENT,
    text_color=TEXT_WHITE, placeholder_text_color=TEXT_MUTED,
    corner_radius=8, height=36
)
loadoutName.pack(pady=4, padx=12, fill="x")

ctk.CTkButton(settings_tab, text="💾  Sauvegarder",
              command=saveLoadout,
              fg_color=ACCENT, hover_color=ACCENT_HOVER,
              font=("Segoe UI", 11, "bold"),
              corner_radius=8, height=36).pack(pady=4, padx=12, fill="x")

ctk.CTkButton(settings_tab, text="📂  Charger un loadout",
              command=showLoadoutSelection,
              fg_color=BG_FRAME, hover_color=ACCENT,
              font=("Segoe UI", 11, "bold"),
              text_color=TEXT_WHITE,
              corner_radius=8, height=36).pack(pady=4, padx=12, fill="x")

# ─── Hotkey ──────────────────────────────────────────────
ctk.CTkLabel(settings_tab, text="Hotkey",
             font=("Segoe UI", 12, "bold"),
             text_color=TEXT_WHITE).pack(pady=(12, 4))

hotkeyFrame = ctk.CTkFrame(settings_tab, fg_color=BG_FRAME, corner_radius=10)
hotkeyFrame.pack(pady=4, padx=12, fill="x")

ctk.CTkLabel(hotkeyFrame, text="Touche :",
             font=("Segoe UI", 10),
             text_color=TEXT_MUTED).pack(side="left", padx=12, pady=10)

hotkeyEntry = ctk.CTkEntry(hotkeyFrame, width=60,
                            fg_color=BG_MAIN, border_color=ACCENT,
                            text_color=TEXT_WHITE, corner_radius=6)
hotkeyEntry.insert(0, hotkey)
hotkeyEntry.pack(side="left", padx=6)

def updateHotkey():
    global hotkey
    new_hotkey = hotkeyEntry.get().strip()
    if new_hotkey and new_hotkey != hotkey:
        keyboard.remove_hotkey(hotkey)
        hotkey = new_hotkey
        config['hotkey']['hotkey'] = hotkey
        keyboard.add_hotkey(hotkey, toggleMacro)
        with open('config.txt', 'w') as configfile:
            config.write(configfile)

ctk.CTkButton(hotkeyFrame, text="Mettre à jour",
              command=updateHotkey,
              fg_color=ACCENT, hover_color=ACCENT_HOVER,
              font=("Segoe UI", 10, "bold"),
              corner_radius=6, height=30).pack(side="left", padx=8)

# ─── Macro ───────────────────────────────────────────────
enabled = False

def moveRel(x, y):
    ctypes.windll.user32.mouse_event(0x0001, x, y, 0, 0)

def toggleMacro():
    global enabled
    enabled = not enabled
    if enabled:
        ctypes.windll.user32.MessageBeep(0xFFFFFFFF)
    else:
        ctypes.windll.user32.MessageBeep(0x00000010)

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

gui.mainloop()
