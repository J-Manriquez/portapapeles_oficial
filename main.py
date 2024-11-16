# main.py
import keyboard
import sys
import tkinter as tk
from structure import ClipboardManager

def main():
    root = tk.Tk()
    show_settings = "--show-settings" in sys.argv
    app = ClipboardManager(root, show_settings)
    # Aplicar las configuraciones iniciales
    root.geometry(f"{app.settings_manager.settings['width']}x{app.settings_manager.settings['height']}+0+0")
    
    # if show_settings:
    #     root.after(100, app.settings_manager.show_settings_window)
    
    # Configurar el atajo de teclado global
    keyboard.add_hotkey(app.hotkey, app.key_manager.toggle_window)
    
    root.mainloop()

if __name__ == "__main__":
    main()