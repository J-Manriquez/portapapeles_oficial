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
        self.file_path_var = tk.StringVar()  # Para almacenar la ruta del archivo

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
            self.settings_window.configure(bg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['bg'])
            self.settings_window.attributes('-topmost', True)

            # Barra de título personalizada
            title_frame = tk.Frame(self.settings_window, bg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['bg'])
            title_frame.pack(fill=tk.X, padx=6, pady=(0, 0))

            title_label = tk.Label(title_frame, text="Configuraciones", font=('Segoe UI', 10, 'bold'),
                                   bg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['bg'],
                            fg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['fg'])
            title_label.pack(side=tk.LEFT, padx=5)

            close_button = tk.Button(title_frame, text="❌", command=self.close_settings_window,
                                     font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2,
                                     bg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['button_bg'],
                        fg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['button_fg'])
            close_button.pack(side=tk.RIGHT)

            # Canvas para scroll y contenedor de configuraciones
            canvas = tk.Canvas(self.settings_window, bg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['bg'], bd=0, highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            # Scrollbar oculto
            scrollbar = ttk.Scrollbar(self.settings_window, orient=tk.VERTICAL, command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Frame contenedor dentro del canvas para el scroll
            self.settings_frame = tk.Frame(canvas, bg=self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']['bg'])
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
            exit_frame = tk.Frame(self.settings_frame,
                                bg=self.clipboard_manager.theme_manager.colors['dark']['bg'])
            exit_frame.pack(fill=tk.X, padx=0, pady=(4, 4))

            current_theme = self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']
            exit_button = tk.Button(
                exit_frame,
                text="⚡ Cerrar aplicación",
                command=self.clipboard_manager.functions.exit_app,
                font=('Segoe UI', 10, 'bold'),
                bg=current_theme['exit_button_bg'],
                fg=current_theme['exit_button_fg'],
                bd=0,
                relief=tk.FLAT,
                padx=10,
                pady=8
            )
            exit_button.pack(fill=tk.X, padx=4)

            # Agregar sección para la ubicación del archivo
            subtitle = tk.Label(
                self.settings_frame,
                text="Ubicación del archivo de datos",
                font=('Segoe UI', 10, 'bold'),
                bg=current_theme['bg'],
                fg=current_theme['fg'],
                anchor='w'
            )
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')

            file_location_frame = tk.Frame(
                self.settings_frame,
                bg=current_theme['card_bg']
            )
            file_location_frame.pack(fill=tk.X, padx=4, pady=2)

            # Mostrar ruta actual
            self.file_path_var.set(self.clipboard_manager.data_manager.file_path)
            path_label = tk.Label(
                file_location_frame,
                textvariable=self.file_path_var,
                bg=current_theme['card_bg'],
                fg=current_theme['fg'],
                anchor='w',
                padx=5,
                pady=5,
                wraplength=250  # Para que el texto largo se ajuste
            )
            path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            change_path_button = tk.Button(
                file_location_frame,
                text="📂",
                command=self.change_file_location,
                font=('Segoe UI', 10),
                bd=0,
                bg=current_theme['button_bg'],
                fg=current_theme['button_fg']
            )
            change_path_button.pack(side=tk.RIGHT, padx=2, pady=2)

            subtitle = tk.Label(self.settings_frame, text="Límite de elementos",
                            font=('Segoe UI', 10, 'bold'),
                            bg=current_theme['bg'],
                            fg=current_theme['fg'],
                            anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Máximo de elementos: ", str(self.settings.get('max_items', 20)))

            subtitle = tk.Label(self.settings_frame, text="Tecla de activación",
                            font=('Segoe UI', 10, 'bold'),
                            bg=current_theme['bg'],
                            fg=current_theme['fg'],
                            anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Teclas Alt + Activacion: ", self.settings['hotkey'])

            subtitle = tk.Label(self.settings_frame, text="Tecla de retroceso",
                            font=('Segoe UI', 10, 'bold'),
                            bg=current_theme['bg'],
                            fg=current_theme['fg'],
                            anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Tecla Retroceso: ", self.settings['back_key'])

            # Tecla para mostrar grupos
            subtitle = tk.Label(self.settings_frame, text="Tecla para mostrar grupos",
                            font=('Segoe UI', 10, 'bold'),
                            bg=current_theme['bg'],
                            fg=current_theme['fg'],
                            anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Teclas Alt + Grupos: ", self.settings.get('groups_key', 'g'))

            # Tecla para nuevo grupo
            subtitle = tk.Label(self.settings_frame, text="Tecla para nuevo grupo",
                            font=('Segoe UI', 10, 'bold'),
                            bg=current_theme['bg'],
                            fg=current_theme['fg'],
                            anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Teclas Alt + Nuevo Grupo: ", self.settings.get('new_group_key', 'n'))

            # Configuración del icono de formato
            subtitle = tk.Label(self.settings_frame, text="Contenido con Formato",
                            font=('Segoe UI', 10, 'bold'),
                            bg=current_theme['bg'],
                            fg=current_theme['fg'],
                            anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_toggle_setting("Mostra 🎨 en copiado formato", 'show_format_icon')

            subtitle = tk.Label(self.settings_frame, text="Dimensiones de la app",
                        font=('Segoe UI', 10, 'bold'),
                        bg=current_theme['bg'],
                        fg=current_theme['fg'],
                        anchor='w')
            subtitle.pack(fill=tk.X, padx=4, pady=(10, 5), anchor='w')
            self.create_setting_card("Alto", str(self.settings['height']))
            self.create_setting_card("Ancho", str(self.settings['width']))

            # Hacer la ventana arrastrable
            title_label.bind('<Button-1>', self.start_move)
            title_label.bind('<B1-Motion>', self.on_move)

            # Agregar vinculación de tecla para toda la ventana
            self.settings_window.bind('<Key>', self.clipboard_manager.key_handler.handle_key_press)

        else:
            self.settings_window.lift()
            self.settings_window.attributes('-topmost', True)
            self.settings_window.after_idle(self.settings_window.attributes, '-topmost', False)

    def change_file_location(self):
        """Permite al usuario seleccionar una nueva ubicación para el archivo de datos"""
        from tkinter import filedialog
        import os

        # Obtener el directorio inicial (el actual del archivo)
        initial_dir = os.path.dirname(self.clipboard_manager.data_manager.file_path)

        # Abrir diálogo para seleccionar directorio
        new_directory = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Seleccionar ubicación para el archivo de datos"
        )

        if new_directory:
            # Construir la nueva ruta completa
            new_file_path = os.path.join(new_directory, 'clipboard_data.json')

            # Actualizar la ruta en el DataManager
            self.clipboard_manager.data_manager.file_path = new_file_path

            # Actualizar la etiqueta en la interfaz
            self.file_path_var.set(new_file_path)

            # Guardar los datos en la nueva ubicación
            groups, pinned_items, settings = self.clipboard_manager.data_manager.load_data()
            self.clipboard_manager.data_manager.save_data(groups, pinned_items, settings)

            # Actualizar la configuración para que use la nueva ruta la próxima vez
            self.settings['data_file_path'] = new_file_path
            self.save_settings()

    def create_toggle_setting(self, setting_name, setting_key):
        current_theme = self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']
        card = tk.Frame(self.settings_frame, bg=current_theme['card_bg'])
        card.pack(fill=tk.X, padx=4, pady=2)

        label = tk.Label(card, text=setting_name,
                        bg=current_theme['card_bg'],
                        fg=current_theme['fg'],
                        anchor='w', padx=5, pady=5)
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Variable para el estado del toggle
        toggle_var = tk.BooleanVar(value=self.settings.get(setting_key, True))
        
        # Crear el switch/toggle button con colores apropiados
        is_active = toggle_var.get()
        button_text = "✓" if is_active else "✗"
        button_bg = current_theme['success_bg'] if is_active else current_theme['error_bg']
        button_fg = current_theme['success_fg'] if is_active else current_theme['error_fg']
        
        toggle_button = tk.Button(card, 
                                text=button_text,
                                command=lambda: self.toggle_setting(toggle_button, toggle_var, setting_key),
                                font=('Segoe UI', 12, 'bold'), bd=0,
                                bg=button_bg,
                                fg=button_fg,
                                activebackground=button_bg,
                                activeforeground=button_fg)
        toggle_button.pack(side=tk.RIGHT, padx=5, pady=2)

    def toggle_setting(self, button, var, setting_key):
        # Cambiar el estado
        new_value = not var.get()
        var.set(new_value)
        
        # Obtener colores del tema actual
        current_theme = self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']
        
        # Actualizar el botón con colores apropiados
        button_text = "✓" if new_value else "✗"
        button_bg = current_theme['success_bg'] if new_value else current_theme['error_bg']
        button_fg = current_theme['success_fg'] if new_value else current_theme['error_fg']
        
        button.configure(text=button_text, 
                        bg=button_bg, 
                        fg=button_fg,
                        activebackground=button_bg,
                        activeforeground=button_fg)
        
        # Guardar la configuración
        self.settings[setting_key] = new_value
        self.save_settings()
        
        # Actualizar la visualización en tiempo real si es necesario
        if setting_key == 'show_format_icon':
            self.clipboard_manager.refresh_current_screen()

    def create_setting_card(self, setting_name, default_value):
        current_theme = self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']
        card = tk.Frame(self.settings_frame, bg=current_theme['card_bg'])
        card.pack(fill=tk.X, padx=4, pady=2)

        # Modificar para mostrar el texto correcto según el tipo de configuración
        display_text = f"{setting_name} {default_value}"

        label = tk.Label(card, text=display_text,
                        bg=current_theme['card_bg'],
                        fg=current_theme['fg'],
                        anchor='w', padx=5, pady=5)
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        edit_button = tk.Button(card, text="✏️",
                                command=lambda: self.toggle_edit_mode(card, label, edit_button, setting_name, default_value),
                                font=('Segoe UI', 10), bd=0,
                                bg=current_theme['button_bg'],
                                fg=current_theme['button_fg'])
        edit_button.pack(side=tk.RIGHT, padx=2, pady=2)

    def toggle_edit_mode(self, card, label, button, setting_name, current_value):
        if button['text'] == "✏️":
            # Cambiar a modo edición
            current_theme = self.clipboard_manager.theme_manager.colors['dark' if self.clipboard_manager.is_dark_mode else 'light']
            entry = tk.Entry(card, bg=current_theme['button_bg'],
                            fg=current_theme['fg'],
                            insertbackground=current_theme['fg'])
            entry.insert(0, current_value)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
            label.pack_forget()
            button.configure(text="💾")
        else:
            # Guardar cambios
            entry = [child for child in card.winfo_children() if isinstance(child, tk.Entry)][0]
            new_value = entry.get()
            label.configure(text=f"{setting_name} {new_value}")
            entry.destroy()
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            button.configure(text="✏️")

            # Actualizar configuraciones
            if setting_name == "Alto":
                new_height = int(new_value)
                if new_height > 0:
                    self.settings['height'] = new_height
                    self.clipboard_manager.window_height = new_height

            elif setting_name == "Ancho":
                new_width = int(new_value)
                if new_width > 0:
                    self.settings['width'] = new_width
                    self.clipboard_manager.window_width = new_width

            elif setting_name == "Máximo de elementos: ":
                try:
                    new_max = int(new_value)
                    if new_max > 0:
                        self.settings['max_items'] = new_max
                        self.clipboard_manager.settings['max_items'] = new_max
                except ValueError:
                    # Si no es un número válido, mantener el valor anterior
                    new_value = current_value

            elif setting_name == "Tecla Retroceso: ":
                self.settings['back_key'] = new_value
                # Actualizar el atajo de retroceso
                self.clipboard_manager.key_handler.global_hotkeys.register_hotkey(
                    new_value,
                    lambda: self.clipboard_manager.key_handler.handle_back()
                    )

            elif setting_name == "Teclas Alt + Activacion: ":
                old_hotkey = self.settings['hotkey']
                self.settings['hotkey'] = new_value
                # Actualizar el atajo principal
                self.clipboard_manager.key_handler.global_hotkeys.update_hotkey(
                    f"alt+{old_hotkey}",
                    f"alt+{new_value}",
                    self.clipboard_manager.key_handler.toggle_window
                )

            elif setting_name == "Teclas Alt + Grupos: ":
                old_key = self.settings.get('groups_key', 'g')
                self.settings['groups_key'] = new_value
                # Actualizar el atajo de grupos
                self.clipboard_manager.key_handler.global_hotkeys.update_hotkey(
                    f"alt+{old_key}",
                    f"alt+{new_value}",
                    self.clipboard_manager.key_handler.show_groups_screen
                )

            elif setting_name == "Teclas Alt + NuevoGrupo: ":
                old_key = self.settings.get('new_group_key', 'n')
                self.settings['new_group_key'] = new_value
                # Actualizar el atajo de nuevo grupo
                self.clipboard_manager.key_handler.global_hotkeys.update_hotkey(
                    f"alt+{old_key}",
                    f"alt+{new_value}",
                    self.clipboard_manager.key_handler.show_new_group_dialog
                )

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
