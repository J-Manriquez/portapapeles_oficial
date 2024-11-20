# settings_manager.py

import json
import os
import sys
import tkinter as tk
from tkinter import ttk

class SettingsManager:
    def __init__(self, master, clipboard_manager):
        self.master = master
        self.clipboard_manager = clipboard_manager
        self.settings_window = None
        self.settings = None      
          
    def initialize_settings(self):
        # Llama a este método después de que ClipboardManager haya inicializado completamente
        self.settings = self.clipboard_manager.settings
        
    def save_settings(self):
        groups, pinned_items, _ = self.clipboard_manager.data_manager.load_data()
        self.clipboard_manager.data_manager.save_data(groups, pinned_items, self.settings)
        
    def show_settings_window(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = tk.Toplevel(self.master)
            self.settings_window.title("Configuraciones")
            
            window_width = self.settings['width']
            window_height = self.settings['height']

            # Usa las coordenadas de la ventana principal o una posición predeterminada
            x = getattr(self.clipboard_manager, 'window_x', 0) 
            y = getattr(self.clipboard_manager, 'window_y', 0)
            
            self.settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            self.settings_window.overrideredirect(True)
            self.settings_window.configure(bg=self.clipboard_manager.theme_manager.colors['dark']['bg'])
            self.settings_window.attributes('-topmost', True)

            # Barra de título personalizada
            title_frame = tk.Frame(self.settings_window, bg=self.clipboard_manager.theme_manager.colors['dark']['bg'])
            title_frame.pack(fill=tk.X, padx=6, pady=(0, 0))

            title_label = tk.Label(title_frame, text="Configuraciones", font=('Segoe UI', 10, 'bold'), 
                                   bg=self.clipboard_manager.theme_manager.colors['dark']['bg'], 
                                   fg=self.clipboard_manager.theme_manager.colors['dark']['fg'])
            title_label.pack(side=tk.LEFT, padx=5)

            close_button = tk.Button(title_frame, text="❌", command=self.close_settings_window, 
                                     font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2,
                                     bg=self.clipboard_manager.theme_manager.colors['dark']['button_bg'],
                                     fg=self.clipboard_manager.theme_manager.colors['dark']['button_fg'])
            close_button.pack(side=tk.RIGHT)

            # Canvas para scroll y contenedor de configuraciones
            canvas = tk.Canvas(self.settings_window, bg=self.clipboard_manager.theme_manager.colors['dark']['bg'], bd=0, highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            # Scrollbar oculto
            scrollbar = ttk.Scrollbar(self.settings_window, orient=tk.VERTICAL, command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Frame contenedor dentro del canvas para el scroll
            self.settings_frame = tk.Frame(canvas, bg=self.clipboard_manager.theme_manager.colors['dark']['bg'])
            canvas_window = canvas.create_window((0, 0), window=self.settings_frame, anchor='nw', width=295)

            # Ajustar el ancho del frame contenedor al canvas
            def on_canvas_resize(event):
                canvas.itemconfig(canvas_window, width=event.width)

            canvas.bind("<Configure>", on_canvas_resize)

            # Configuración de scroll
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))

            self.settings_frame.bind("<Configure>", on_frame_configure)

            # Función para desplazamiento con la rueda del mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            # Crear cards de configuración
            subtitle = tk.Label(self.settings_frame, text="Tecla de activación", 
                        font=('Segoe UI', 10, 'bold'),
                        bg=self.clipboard_manager.theme_manager.colors['dark']['bg'],
                        fg=self.clipboard_manager.theme_manager.colors['dark']['fg'],
                        anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Alt+", self.settings['hotkey'])
            
            subtitle = tk.Label(self.settings_frame, text="Dimensiones de la app", 
                        font=('Segoe UI', 10, 'bold'),
                        bg=self.clipboard_manager.theme_manager.colors['dark']['bg'],
                        fg=self.clipboard_manager.theme_manager.colors['dark']['fg'],
                        anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Alto", str(self.settings['height']))
            self.create_setting_card("Ancho", str(self.settings['width']))

            # Hacer la ventana arrastrable
            title_label.bind('<Button-1>', self.start_move)
            title_label.bind('<B1-Motion>', self.on_move)

        else:
            self.settings_window.lift()
            self.settings_window.attributes('-topmost', True)
            self.settings_window.after_idle(self.settings_window.attributes, '-topmost', False)

    def create_setting_card(self, setting_name, default_value):
        card = tk.Frame(self.settings_frame, bg=self.clipboard_manager.theme_manager.colors['dark']['card_bg'])
        card.pack(fill=tk.X, padx=4, pady=2)

        label = tk.Label(card, text=f"{setting_name}: {default_value}", 
                         bg=self.clipboard_manager.theme_manager.colors['dark']['card_bg'],
                         fg=self.clipboard_manager.theme_manager.colors['dark']['fg'],
                         anchor='w', padx=5, pady=5)
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        edit_button = tk.Button(card, text="✏️", 
                                command=lambda: self.toggle_edit_mode(card, label, edit_button, setting_name, default_value),
                                font=('Segoe UI', 10), bd=0,
                                bg=self.clipboard_manager.theme_manager.colors['dark']['button_bg'],
                                fg=self.clipboard_manager.theme_manager.colors['dark']['button_fg'])
        edit_button.pack(side=tk.RIGHT, padx=2, pady=2)

    def toggle_edit_mode(self, card, label, button, setting_name, current_value):
        if button['text'] == "✏️":
            # Cambiar a modo edición
            entry = tk.Entry(card, bg=self.clipboard_manager.theme_manager.colors['dark']['button_bg'],
                             fg=self.clipboard_manager.theme_manager.colors['dark']['fg'],
                             insertbackground=self.clipboard_manager.theme_manager.colors['dark']['fg'])
            entry.insert(0, current_value)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
            label.pack_forget()
            button.configure(text="💾")
        else:
            # Guardar cambios
            entry = [child for child in card.winfo_children() if isinstance(child, tk.Entry)][0]
            new_value = entry.get()
            label.configure(text=f"{setting_name}: {new_value}")
            entry.destroy()
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            button.configure(text="✏️")
            
            # Actualizar configuraciones
            if setting_name == "Alto":
                self.settings['height'] = int(new_value)
            elif setting_name == "Ancho":
                self.settings['width'] = int(new_value)
            elif setting_name == "Alt+":
                old_hotkey = self.settings['hotkey']
                new_hotkey = 'alt+' + new_value
                self.settings['hotkey'] = new_value  # Guarda solo la letra
                self.clipboard_manager.key_handler.update_hotkey(f"alt+{old_hotkey}", new_hotkey)
                
            self.save_settings()
            self.restart_app()
            
    def restart_app(self):
        python = sys.executable
        os.execl(python, python, *sys.argv, "--show-settings")
            
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.settings_window.winfo_x() + deltax
        y = self.settings_window.winfo_y() + deltay
        self.settings_window.geometry(f"+{x}+{y}")
        
    def close_settings_window(self):
        self.settings_window.destroy()
        self.clipboard_manager.show_main_screen()