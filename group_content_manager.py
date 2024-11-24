# group_content_manager.py

import tkinter as tk
from tkinter import ttk
from utils import process_text
import logging

logger = logging.getLogger(__name__)

class GroupContentManager:
    def __init__(self, master, manager, theme_manager, settings_manager):
        self.master = master
        self.manager = manager
        self.theme_manager = theme_manager
        self.settings_manager = settings_manager
        self.content_window = None
        self.canvas = None
        self.scrollbar = None
        self.items_frame = None

        self.min_card_height = 50  # Altura mínima en píxeles (2 líneas + 2*2 padding)
        self.max_card_height = 120  # Altura máxima en píxeles (4 líneas + 2*2 padding)
        self.line_height = 10      # Altura estimada de una línea de texto

    def calculate_card_height(self, text_data):
        if isinstance(text_data, dict):
            text = text_data.get('text', '')
        else:
            text = str(text_data)
        
        lines = len(text.split('\n'))
        if lines > 2:
            content_height = min(lines * (self.line_height*2), 7 * self.line_height)  # Máximo 4 líneas
        else:
            content_height = min(lines * self.line_height, 5 * self.line_height)  # Máximo 4 líneas
        return min(max(content_height + 5, self.min_card_height), self.max_card_height)

    def show_group_content(self, group_id):
        """Muestra el contenido de un grupo específico"""
        self.current_group_id = group_id  # Guardar el ID del grupo actual
        
        # Si existe una ventana anterior, destruirla para evitar problemas de estado
        if hasattr(self, 'content_window') and self.content_window:
            self.content_window.destroy()
            
        # Siempre crear una nueva ventana
        if self.content_window is not None:
            self.content_window.destroy()
        
        # Crear o mostrar la ventana de contenido
        if self.content_window is None or not self.content_window.winfo_exists():
            self.content_window = tk.Toplevel(self.master)
            self.content_window.title(f"Contenido del Grupo: {self.manager.group_manager.groups[group_id]['name']}")
            
            # Configurar dimensiones y posición
            window_width = self.settings_manager.settings['width']
            window_height = self.settings_manager.settings['height']
            x = self.manager.window_x 
            y = self.manager.window_y 
            
            self.content_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Configurar apariencia de la ventana
            self.content_window.overrideredirect(True)
            self.content_window.configure(bg=self.theme_manager.colors['dark']['bg'])
            self.content_window.attributes('-topmost', True)

            # Barra de título personalizada
            title_frame = tk.Frame(self.content_window, bg=self.theme_manager.colors['dark']['bg'])
            title_frame.pack(fill=tk.X, padx=6, pady=(0,0))

            title_label = tk.Label(title_frame, 
                                text=f"Grupo: {self.manager.group_manager.groups[group_id]['name']}", 
                                font=('Segoe UI', 10, 'bold'),
                                bg=self.theme_manager.colors['dark']['bg'],
                                fg=self.theme_manager.colors['dark']['fg'])
            title_label.pack(side=tk.LEFT, padx=5, pady=5)

            close_button = tk.Button(title_frame, 
                                text="❌", 
                                command=lambda: self.close_content_window(group_id),
                                font=('Segoe UI', 10, 'bold'),
                                bd=0, padx=10, width=5, height=2,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'])
            close_button.pack(side=tk.RIGHT)

            # Canvas y scroll para los items
            self.canvas = tk.Canvas(self.content_window, 
                                bg=self.theme_manager.colors['dark']['bg'], 
                                highlightthickness=0)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.scrollbar = ttk.Scrollbar(self.content_window, 
                                        orient="vertical", 
                                        command=self.canvas.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            # Frame para los items
            self.items_frame = tk.Frame(self.canvas, 
                                    bg=self.theme_manager.colors['dark']['bg'])
            self.canvas_window = self.canvas.create_window((0, 0), 
                                                        window=self.items_frame, 
                                                        anchor='nw', 
                                                        width=window_width)

            # Configurar el desplazamiento con la rueda del ratón
            def _on_mousewheel(event):
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

            # Asegurar que el ancho del frame interior se ajuste al canvas
            def _configure_inner_frame(event):
                if self.canvas.winfo_exists():
                    self.canvas.itemconfig(self.canvas_window, width=event.width)
            
            self.canvas.bind('<Configure>', _configure_inner_frame)

            # Hacer la ventana arrastrable
            title_frame.bind('<Button-1>', self.start_move)
            title_frame.bind('<B1-Motion>', self.on_move)
            
            # Vincular eventos de teclado
            self.content_window.bind('<Key>', self.manager.key_handler.handle_key_press)
            
            # Configurar la navegación y los atajos de teclado
            def after_dialog_shown():
                self.content_window.focus_force()
                self.content_window.grab_set()  # Asegurar que la ventana tenga el foco exclusivo
                self.manager.navigation.set_strategy('group_content')
                self.manager.group_content_screen_keys.activate()
                self.manager.navigation.initialize_focus()
                self.manager.navigation.update_highlights()
                
                # Desactivar otras configuraciones de teclas
                if hasattr(self.manager, 'main_screen_keys'):
                    self.manager.main_screen_keys.deactivate()
                if hasattr(self.manager, 'groups_screen_keys'):
                    self.manager.groups_screen_keys.deactivate()
                if hasattr(self.manager, 'select_group_screen_keys'):
                    self.manager.select_group_screen_keys.deactivate()
            
            # Dar tiempo a que la ventana se muestre completamente
            self.content_window.after(100, after_dialog_shown)
            
            # Dar tiempo a que la ventana se muestre completamente
            self.content_window.after(100, after_dialog_shown)

        else:
            # Si la ventana ya existe, mostrarla y actualizarla
            self.content_window.deiconify()
            self.content_window.lift()
            self.content_window.attributes('-topmost', True)
            self.content_window.after_idle(self.content_window.attributes, '-topmost', False)
            
            # Actualizar el título
            for widget in self.content_window.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.configure(text=f"Grupo: {self.manager.group_manager.groups[group_id]['name']}")
                            break
                    break

        # Mostrar items del grupo
        self.refresh_group_content(group_id)

        # Restaurar la posición del scroll si existe
        if hasattr(self, 'scroll_position'):
            self.canvas.yview_moveto(self.scroll_position)
            
        # Asegurarse de que el foco y la navegación estén correctamente configurados
        self.content_window.after(200, lambda: self.manager.navigation.current_strategy.initialize_focus())
        
        logger.debug(f"Grupo content window shown for group {group_id}")
    
    def _initialize_content_view(self):
        """Inicializa la vista de contenido después de mostrar la ventana"""
        self.content_window.focus_force()
        self.manager.navigation.initialize_focus()
        self.manager.navigation.update_highlights()

    def close_content_window(self, group_id):
        """Cierra la ventana de contenido y restaura la navegación de grupos"""
        if self.content_window:
            # Desactivar la configuración de teclas actual
            self.manager.group_content_screen_keys.deactivate()
            
            # Guardar la posición del scroll si es necesario
            if hasattr(self, 'canvas'):
                self.scroll_position = self.canvas.yview()[0]
                
            # self.content_window.withdraw()
            self.content_window.destroy()
            self.content_window = None
            
            # # Restaurar la navegación de grupos
            # self.manager.group_manager.show_groups_window()
            # self.manager.navigation.set_strategy('groups')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.content_window.winfo_x() + deltax
        y = self.content_window.winfo_y() + deltay
        self.content_window.geometry(f"+{x}+{y}")
        
    def refresh_group_content(self, group_id):
        # Limpiar el frame de items existente
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        window_width = self.settings_manager.settings['width']
        window_height = self.settings_manager.settings['height'] - 40  # Ajuste para la barra de título

        current_theme = 'dark'  # Puedes cambiar esto si soportas modo claro/oscuro
        theme = self.theme_manager.colors[current_theme]

        for item in self.manager.group_manager.groups[group_id]['items']:
            card_width = window_width - 4  # Ajuste mínimo para el padding
            card_height = max(self.min_card_height, self.calculate_card_height(item['text']))
    
            bg_color = theme['card_bg']
    
            card_container = tk.Frame(self.items_frame, width=card_width, height=card_height, bg=bg_color)
            card_container.pack(fill=tk.X, padx=6, pady=(4,0))
            card_container.pack_propagate(False)  # Evita que el contenido afecte el tamaño del contenedor

            text_frame = tk.Frame(card_container, bg=bg_color, pady=0)
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Procesamos el texto para mostrarlo de forma limpia
            processed_text = process_text(item['text'], 2)
            item_name = item.get('name', '')

            # Etiqueta para item_name en negrita y tamaño de fuente mayor
            if item_name:
                item_name_label = tk.Label(
                    text_frame,
                    text=f"{item_name}:",
                    font=("Segoe UI", 10, "bold"),
                    bg=bg_color,
                    fg=theme['fg'],
                    justify=tk.LEFT,
                    anchor='w',
                    width=int(24)
                )
                item_name_label.pack(padx=2, pady=0, fill=tk.X, side=tk.TOP, anchor='w')

            # Etiqueta para processed_text con fuente regular
            text_label = tk.Label(
                text_frame,
                text=processed_text,
                font=("Segoe UI", 10),
                justify=tk.LEFT,
                anchor='w',
                bg=bg_color,
                fg=theme['fg'],
                width=int(24)
            )
            text_label.pack(padx=6, pady=(0,4), fill=tk.X, expand=True, side=tk.TOP)
            
            icons_frame = tk.Frame(card_container, bg=bg_color)
            icons_frame.pack(side=tk.RIGHT, padx=3)

            edit_button = tk.Button(icons_frame, text="✏️", 
                                    command=lambda i=item['id']: self.edit_group_item(group_id, i),
                                    font=('Segoe UI', 10), bd=0, highlightthickness=0,padx=4,
                                    bg=bg_color, fg=theme['fg'])
            edit_button.pack(side=tk.LEFT)

            delete_button = tk.Button(icons_frame, text="❌", 
                                    command=lambda i=item['id']: self.remove_item_from_group(group_id, i, self.items_frame),
                                    font=('Segoe UI', 10), bd=0, highlightthickness=0,padx=4,
                                    bg=bg_color, fg=theme['fg'])
            delete_button.pack(side=tk.LEFT)

        # Actualizar el scrollregion después de añadir todos los widgets
        self.items_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Después de actualizar el contenido:
        if hasattr(self.manager.navigation, 'current_strategy'):
            self.manager.navigation.current_strategy.update_highlights()
        
    def remove_item_from_group(self, group_id, item_id, items_frame):
        self.manager.group_manager.groups[group_id]['items'] = [item for item in self.manager.group_manager.groups[group_id]['items'] if item['id'] != item_id]
        self.manager.group_manager.save_groups()
        self.refresh_group_content(group_id)
        self.manager.group_manager._initialize_content_view()

    def edit_group_item(self, group_id, item_id):
        """Muestra el diálogo para editar un item del grupo"""
        # Primero, cerrar la ventana de contenido del grupo
        self.close_content_window(group_id)
        
        item = next((item for item in self.manager.group_manager.groups[group_id]['items'] if item['id'] == item_id), None)
        if not item:
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("Editar Item")
        
        x = self.manager.window_x
        y = self.manager.window_y 
        
        if isinstance(item['text'], dict):
            text = item['text'].get('text', '')
            original_format = item['text'].get('formatted', {})
        else:
            text = str(item['text'])
            original_format = {}
        
        text_lines = text.count('\n') + 1
        initial_height = min(150 + (text_lines * 20), 600)
        
        dialog.geometry(f"300x{initial_height}+{x}+{y}")
        
        dialog.configure(bg=self.theme_manager.colors['dark']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)

        title_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        title_frame.pack(fill=tk.X, padx=4, pady=(4, 0))

        title_label = tk.Label(title_frame, text="Editar Item", font=('Segoe UI', 10, 'bold'),
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        title_label.pack(side=tk.LEFT, padx=0)

        def close_edit_dialog():
            dialog.destroy()
            # Volver a mostrar la ventana de grupos después de cerrar el diálogo
            self.manager.group_manager.show_groups_window()

        close_button = tk.Button(title_frame, text="❌", command=close_edit_dialog,
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=0,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'])
        close_button.pack(side=tk.RIGHT)
        
        content_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=0)

        name_label = tk.Label(content_frame, text="Nombre del item:",
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        name_label.pack(anchor='w', pady=(0, 5))

        name_entry = tk.Entry(content_frame, bg=self.theme_manager.colors['dark']['button_bg'],
                            fg=self.theme_manager.colors['dark']['fg'],
                            insertbackground=self.theme_manager.colors['dark']['fg'],
                            font=('Segoe UI', 10))
        name_entry.insert(0, item.get('name', ''))
        name_entry.pack(fill=tk.X, pady=(0, 5))

        text_label = tk.Label(content_frame, text="Texto del item:",
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        text_label.pack(anchor='w', pady=(0, 5))

        text_entry = tk.Text(content_frame, height=3, bg=self.theme_manager.colors['dark']['button_bg'],
                            fg=self.theme_manager.colors['dark']['fg'],
                            insertbackground=self.theme_manager.colors['dark']['fg'],
                            font=('Segoe UI', 10))
        text_entry.insert(tk.END, text)
        text_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        def save_item():
            new_name = name_entry.get().strip()
            new_text = text_entry.get("1.0", tk.END).strip()
            if new_text:
                item['name'] = new_name
                if new_text != text:
                    # Si el texto ha cambiado, eliminamos el formato
                    item['text'] = {'text': new_text, 'formatted': {}}
                else:
                    # Si el texto no ha cambiado, mantenemos el formato original
                    item['text'] = {'text': new_text, 'formatted': original_format}
                self.manager.group_manager.save_groups()
                dialog.destroy()
                # Volver a mostrar la ventana de grupos después de guardar
                self.manager.group_manager.show_groups_window()

        save_button = tk.Button(content_frame, text="Guardar", command=save_item,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'],
                                relief=tk.FLAT, bd=0, padx=4, pady=8)
        save_button.pack(fill=tk.X, pady=(0, 5))

        # Código para hacer la ventana arrastrable
        def start_move(event):
            dialog.x = event.x
            dialog.y = event.y

        def on_move(event):
            deltax = event.x - dialog.x
            deltay = event.y - dialog.y
            x = dialog.winfo_x() + deltax
            y = dialog.winfo_y() + deltay
            dialog.geometry(f"+{x}+{y}")

        title_frame.bind('<Button-1>', start_move)
        title_frame.bind('<B1-Motion>', on_move)

        # Función para ajustar dinámicamente la altura de la ventana
        def adjust_dialog_height(event=None):
            content = text_entry.get("1.0", tk.END)
            lines = content.count('\n') + 1
            new_height = min(150 + (lines * 20), 600)
            dialog.geometry(f"300x{new_height}")

        text_entry.bind("<KeyRelease>", adjust_dialog_height)

        dialog.focus_set()
        name_entry.focus()

        adjust_dialog_height()