# main.py

import sys
import tkinter as tk
from structure import ClipboardManager

def main():
    root = tk.Tk()
    show_settings = "--show-settings" in sys.argv
    app = ClipboardManager(root, show_settings)
    # Aplicar las configuraciones iniciales
    root.geometry(f"{app.settings_manager.settings['width']}x{app.settings_manager.settings['height']}+0+0")
    
    root.mainloop()

if __name__ == "__main__":
    main()