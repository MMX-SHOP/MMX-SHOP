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

def setValues():
    global xValue, yValue, delayValue
    xValue = int(xControl.get())
    yValue = int(yControl.get())
    delayValue = int(delay.get())
    xValueLabel.configure(text=f"X: {xValue}")
    yValueLabel.configure(text=f"Y: {yValue}")
    delayValueLabel.configure(text=f"Delay: {delayValue} ms")
    print(f"Values set - X:{xValue} Y:{yValue} D:{delayValue}")

def toggleAimCheck():
    global aimCheck
    aimCheck = not aimCheck
    aimCheckButton.configure(text='Aim Check On' if aimCheck else 'Aim Check Off')

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
    loadout_names = config.options('loadouts')  # Get all loadout names
    if not loadout_names:
        ctk.CTkMessageBox.showinfo("Loadout List", "No loadouts found.")
        return

    loadout_window = ctk.CTkToplevel(gui)  # Create a new top-level window
    loadout_window.title("Loadout changer")
    loadout_window.geometry("300x500")

    loadout_listbox = tk.Listbox(loadout_window, font=('Arial', 10))  # Set font size for Listbox
    loadout_listbox.pack(pady=10, padx=10, fill="both", expand=True)

    for name in loadout_names:
        loadout_listbox.insert(tk.END, name)  # Insert loadout names into the listbox

    def confirmLoadout():
        selected_index = loadout_listbox.curselection()
        if selected_index:
            name = loadout_names[selected_index[0]]  # Get the selected loadout name
            confirmation = messagebox.askyesno("Confirm Loadout", f"Are you sure you want to load the loadout '{name}'?")
            if confirmation:
                loadLoadout(name)

    loadButton = ctk.CTkButton(loadout_window, text="Load Selected Loadout", command=confirmLoadout)
    loadButton.pack(pady=5)

    # Set smaller font for the button
    loadButton.configure(font=('Arial', 9))

def loadLoadout(name=None):
    global xValue, yValue, delayValue
    if name is None:  # If no name is provided, get it from the entry
        setValues()
        name = str(loadoutName.get()).strip()
        loadoutName.delete(0, ctk.END)

    config = configparser.ConfigParser()
    config.read('config.txt')

    try:
        loadout = config['loadouts'][name]
    except KeyError:
        ctk.CTkMessageBox.showwarning("Error", f"No loadout called {name}")
        return None

    loadoutList = ast.literal_eval(loadout)
    xValue = loadoutList[0]
    yValue = loadoutList[1]
    delayValue = loadoutList[2]

    xControl.set(loadoutList[0])
    yControl.set(loadoutList[1])
    delay.set(loadoutList[2])
    setValues()  # Update labels with loaded values

# Create GUI
ctk.set_appearance_mode("dark")

gui = ctk.CTk()
gui.title("MMX-SHOP")
gui.configure(fg_color="#050505")

# Set window size
x, y = getResolution()
size = min(int(x / 5), int(y / 1.5))
gui.geometry(f'{size}x{size}')
# MMX-SHOP Branding

brandFrame = ctk.CTkFrame(gui, fg_color="transparent")
brandFrame.pack(pady=(10, 5))

mmxLabel = ctk.CTkLabel(
    brandFrame,
    text="MMX",
    font=("Arial", 28, "bold"),
    text_color="white"
)
mmxLabel.pack(side="left")

shopLabel = ctk.CTkLabel(
    brandFrame,
    text="-SHOP",
    font=("Arial", 28, "bold"),
    text_color="#A020F0"
)
shopLabel.pack(side="left")

# Create Notebook (Tabs)
tab_view = ttk.Notebook(gui)
tab_view.pack(fill="both", expand=True)

# Create Main Tab
main_tab = ctk.CTkFrame(tab_view)
tab_view.add(main_tab, text="Recoil")

# Create Settings Tab
settings_tab = ctk.CTkFrame(tab_view)
tab_view.add(settings_tab, text="Loadouts")

# Main Tab Contents
aimCheckButton = ctk.CTkButton(
    main_tab,
    text="Aim Check Off",
    command=toggleAimCheck,
    fg_color="#7C3AED",
    hover_color="#8B5CF6",
    corner_radius=18,
    height=40
)
aimCheckButton.pack(pady=5)

# X Control
xFrame = ctk.CTkFrame(main_tab)
xFrame.pack(pady=5)

ctk.CTkLabel(xFrame, text='X Control').pack(side=ctk.LEFT)
xControl = ctk.CTkSlider(xFrame, from_=-5, to=10, orientation='horizontal', width=150, command=lambda value: xValueLabel.configure(text=f"X: {int(value)}"))
xControl.pack(side=ctk.LEFT, padx=(5, 10))
xValueLabel = ctk.CTkLabel(xFrame, text=f"X: {xValue}")
xValueLabel.pack(side=ctk.LEFT)

# Y Control
yFrame = ctk.CTkFrame(main_tab)
yFrame.pack(pady=5)

ctk.CTkLabel(yFrame, text='Y Control').pack(side=ctk.LEFT)
yControl = ctk.CTkSlider(yFrame, from_=0, to=8, orientation='horizontal', width=150, command=lambda value: yValueLabel.configure(text=f"Y: {int(value)}"))
yControl.pack(side=ctk.LEFT, padx=(5, 10))
yValueLabel = ctk.CTkLabel(yFrame, text=f"Y: {yValue}")
yValueLabel.pack(side=ctk.LEFT)

# Delay Control
delayFrame = ctk.CTkFrame(main_tab)
delayFrame.pack(pady=5)

ctk.CTkLabel(delayFrame, text='Delay (ms)').pack(side=ctk.LEFT)

delay = ctk.CTkSlider(
    delayFrame,
    from_=1,
    to=30,
    orientation='horizontal',
    width=150,
    command=lambda value: delayValueLabel.configure(
        text=f"Delay: {int(value)} ms"
    )
)

delay.set(10)
delay.pack(side=ctk.LEFT, padx=(5,10))

delayValueLabel = ctk.CTkLabel(
    delayFrame,
    text=f"Delay: {delayValue} ms"
)

delayValueLabel.pack(side=ctk.LEFT)

setButton = ctk.CTkButton(
    main_tab,
    text="Set",
    command=setValues,
    fg_color="#7C3AED",
    hover_color="#8B5CF6",
    corner_radius=15,
    height=42
)

setButton.pack(pady=5)

# Settings Tab Contents



# Settings Tab Contents
loadoutName = ctk.CTkEntry(settings_tab)
loadoutName.pack(pady=5)
saveButton = ctk.CTkButton(
    settings_tab,
    text='Save cfg',
    command=saveLoadout,
    fg_color="#7C3AED",
    hover_color="#8B5CF6",
    corner_radius=15,
    height=40
)

saveButton.pack(pady=5)


loadButton = ctk.CTkButton(     settings_tab,     text='Load cfg',     command=showLoadoutSelection,     fg_color="#7C3AED",     hover_color="#8B5CF6",     corner_radius=15,     height=40 )
loadButton.pack(pady=5)

# Hotkey Entry
hotkeyFrame = ctk.CTkFrame(settings_tab)
hotkeyFrame.pack(pady=5)

ctk.CTkLabel(hotkeyFrame, text='Hotkey:').pack(side=ctk.LEFT)
hotkeyEntry = ctk.CTkEntry(hotkeyFrame, width=10)
hotkeyEntry.insert(0, hotkey)
hotkeyEntry.pack(side=ctk.LEFT, padx=(5, 10))

def updateHotkey():
    global hotkey
    new_hotkey = hotkeyEntry.get().strip()
    
    if new_hotkey and new_hotkey != hotkey:
        # Remove the old hotkey listener
        keyboard.remove_hotkey(hotkey)
        
        # Set the new hotkey
        hotkey = new_hotkey
        config['hotkey']['hotkey'] = hotkey
        
        # Add the new hotkey listener
        keyboard.add_hotkey(hotkey, toggleMacro)

        # Save the updated hotkey to config
        with open('config.txt', 'w') as configfile:
            config.write(configfile)

        print(f"Hotkey updated to: {hotkey}")

updateHotkeyButton = ctk.CTkButton(     hotkeyFrame,     text='Update Hotkey',     command=updateHotkey,     fg_color="#7C3AED",     hover_color="#8B5CF6",     corner_radius=15,     height=35 )
updateHotkeyButton.pack(side=ctk.LEFT)

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
