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
    
    # Configurar el atajo de teclado global
    app.key_handler.register_global_hotkey(app.hotkey, app.key_handler.toggle_window)
    
    # Configurar manejo de teclas para la ventana principal
    root.bind('<Key>', app.key_handler.handle_key_press)
    
    root.mainloop()

if __name__ == "__main__":
    main()