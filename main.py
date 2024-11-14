# main.py

import tkinter as tk
from structure import ClipboardManager

def main():
    root = tk.Tk()
    app = ClipboardManager(root)
    # Aplicar las configuraciones iniciales
    root.geometry(f"{app.settings_manager.settings['width']}x{app.settings_manager.settings['height']}+0+0")
    
    root.mainloop()

if __name__ == "__main__":
    main()