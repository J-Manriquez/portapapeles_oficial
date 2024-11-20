# group_manager.py

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import uuid
from settings_manager import SettingsManager
from group_content_manager import GroupContentManager
import logging

logging.getLogger('chardet').setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GroupManager:
    def __init__(self, master, clipboard_manager):
        self.master = master
        self.clipboard_manager = clipboard_manager
        self.data_manager = clipboard_manager.data_manager
        self.theme_manager = clipboard_manager.theme_manager
        self.settings = clipboard_manager.settings
        self.settings_manager = clipboard_manager.settings_manager
        self.groups, _, _ = self.data_manager.load_data()
        self.groups_window = None
        self.groups_frame = None
        self.group_content_manager = GroupContentManager(master, clipboard_manager, clipboard_manager.theme_manager, clipboard_manager.settings_manager)
        self.canvas = None
        self.scrollbar = None
        self.add_button = None
        self.close_button = None

    def show_group_content(self, group_id):
        if self.groups_window:
            self.groups_window.withdraw()  # Oculta la ventana de grupos
        self.group_content_manager.show_group_content(group_id)


    def show_groups_window(self):
        logger.debug("Intentando mostrar la ventana de grupos")
        if self.groups_window is None or not self.groups_window.winfo_exists():
            logger.debug("Creando nueva ventana de grupos")
            self.groups_window = tk.Toplevel(self.master)
            self.groups_window.title("Grupos")
            
            window_width = self.settings['width']
            window_height = self.settings['height']
            
            x = self.clipboard_manager.window_x 
            y = self.clipboard_manager.window_y 
            
            self.groups_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            self.groups_window.overrideredirect(True)
            self.groups_window.configure(bg=self.theme_manager.colors['dark']['bg'])
            self.groups_window.attributes('-topmost', True)
            self.master.bind("<Destroy>", self.on_main_window_close)

            # Barra de título personalizada
            title_frame = tk.Frame(self.groups_window, bg=self.theme_manager.colors['dark']['bg'])
            title_frame.pack(fill=tk.X, padx=2, pady=(0, 0))

            title_label = tk.Label(title_frame, text="Grupos", font=('Segoe UI', 10, 'bold'), 
                                   bg=self.theme_manager.colors['dark']['bg'], 
                                   fg=self.theme_manager.colors['dark']['fg'])
            title_label.pack(side=tk.LEFT, padx=5)

            # Botones en la barra de título
            buttons_frame = tk.Frame(title_frame, bg=self.theme_manager.colors['dark']['bg'])
            buttons_frame.pack(side=tk.RIGHT, padx=4)

            self.add_button = tk.Button(buttons_frame, text="➕", command=self.add_group, 
                                   font=('Segoe UI', 10), bd=0, padx=10, width=5, height=2,
                                   bg=self.theme_manager.colors['dark']['button_bg'],
                                   fg=self.theme_manager.colors['dark']['button_fg'])
            self.add_button.pack(side=tk.LEFT)

            self.close_button = tk.Button(buttons_frame, text="❌", command=self.close_groups_window, 
                                     font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2,
                                     bg=self.theme_manager.colors['dark']['button_bg'],
                                     fg=self.theme_manager.colors['dark']['button_fg'])
            self.close_button.pack(side=tk.LEFT)
            
            # Canvas para scroll y contenedor de grupos
            self.canvas = tk.Canvas(self.groups_window, bg=self.theme_manager.colors['dark']['bg'], bd=0, highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            # Scrollbar
            self.scrollbar = ttk.Scrollbar(self.groups_window, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            # Frame contenedor dentro del canvas para el scroll
            self.groups_frame = tk.Frame(self.canvas, bg=self.theme_manager.colors['dark']['bg'])
            canvas_window = self.canvas.create_window((0, 0), window=self.groups_frame, anchor='nw', width=295)

            # Ajustar el ancho del frame contenedor al canvas
            def on_canvas_resize(event):
                self.canvas.itemconfig(canvas_window, width=event.width)

            self.canvas.bind("<Configure>", on_canvas_resize)

            # Configuración de scroll
            def on_frame_configure(event):
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            self.groups_frame.bind("<Configure>", on_frame_configure)

            # Función para desplazamiento con la rueda del mouse
            def _on_mousewheel(event):
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

            # Hacer la ventana arrastrable
            title_label.bind('<Button-1>', self.start_move)
            title_label.bind('<B1-Motion>', self.on_move)

            self.refresh_groups()

            # Configurar eventos de teclado
            self.groups_window.bind('<Up>', lambda e: self.clipboard_manager.navigation.navigate_vertical(e))
            self.groups_window.bind('<Down>', lambda e: self.clipboard_manager.navigation.navigate_vertical(e))
            self.groups_window.bind('<Left>', lambda e: self.clipboard_manager.navigation.navigate_horizontal(e))
            self.groups_window.bind('<Right>', lambda e: self.clipboard_manager.navigation.navigate_horizontal(e))
            self.groups_window.bind('<Return>', lambda e: self.clipboard_manager.navigation.activate_selected(e))

            # Mostrar la ventana después de configurarla completamente
            self.groups_window.deiconify()
            self.groups_window.focus_force()
            
            # Inicializar el foco después de que la ventana esté visible
            self.groups_window.after(100, self.clipboard_manager.navigation.initialize_focus)
        else:
            logger.debug("Mostrando ventana de grupos existente")
            self.groups_window.deiconify()
            self.groups_window.focus_force()

        self.clipboard_manager.navigation.set_strategy('groups')
        logger.debug("Ventana de grupos mostrada y estrategia de navegación configurada")

        # Restaurar la posición del scroll
        # if hasattr(self, 'scroll_position'):
        #     self.canvas.yview_moveto(self.scroll_position)
         
    def close_groups_window(self):
        if self.canvas:
            # Guardar la posición actual del scroll
            self.scroll_position = self.canvas.yview()[0]
        self.groups_window.withdraw()
        self.clipboard_manager.show_main_screen()
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.groups_window.winfo_x() + deltax
        y = self.groups_window.winfo_y() + deltay
        self.groups_window.geometry(f"+{x}+{y}")

    def refresh_groups(self):
        logger.debug("Refrescando grupos")
        if self.groups_frame is None or not self.groups_frame.winfo_exists():
            return

        for widget in self.groups_frame.winfo_children():
            widget.destroy()

        for group_id, group_info in self.groups.items():
            group_card = tk.Frame(self.groups_frame, bg=self.theme_manager.colors['dark']['card_bg'], cursor="hand2")
            group_card.pack(fill=tk.X, padx=8, pady=2)
            
            group_card.bind("<Button-1>", lambda e, gid=group_id: self.show_group_content(gid))

            name_label = tk.Label(group_card, text=group_info['name'], font=("Segoe UI", 10, "bold"),
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'], 
                                width=int(17), justify=tk.LEFT, anchor='w',)
            name_label.pack(side=tk.LEFT, padx=5, pady=5)

            count_label = tk.Label(group_card, text=f"Items: {len(group_info['items'])}",
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'])
            count_label.pack(side=tk.LEFT, padx=5, pady=2)
            
            # Frame para los iconos
            icons_frame = tk.Frame(group_card, bg=self.theme_manager.colors['dark']['card_bg'])
            icons_frame.pack(side=tk.RIGHT, padx=3)

            edit_button = tk.Button(icons_frame, text="✏️", command=lambda gid=group_id: self.edit_group(gid),
                        font=('Segoe UI', 10), bd=0, highlightthickness=0,padx=4,
                        bg=self.clipboard_manager.theme_manager.colors['dark']['button_bg'],
                        fg=self.clipboard_manager.theme_manager.colors['dark']['button_fg'])
            edit_button.pack(side=tk.LEFT)

            delete_button = tk.Button(icons_frame, text="❌", command=lambda gid=group_id: self.delete_group(gid),
                          font=('Segoe UI', 10), bd=0, highlightthickness=0, padx=4,
                          bg=self.clipboard_manager.theme_manager.colors['dark']['button_bg'],
                          fg=self.clipboard_manager.theme_manager.colors['dark']['button_fg'])
            delete_button.pack(side=tk.LEFT)

        # logger.debug(f"Grupos refrescados: {len(self.groups)} grupos")

            
            
    def save_groups(self):
        pinned_items = {k: v for k, v in self.clipboard_manager.clipboard_items.items() if v['pinned']}
        # Asegúrate de que cada item pinned tenga la estructura correcta
        for item_id, item_data in pinned_items.items():
            if isinstance(item_data['text'], str):
                pinned_items[item_id]['text'] = {'text': item_data['text'], 'formatted': {}}
            elif not isinstance(item_data['text'], dict):
                pinned_items[item_id]['text'] = {'text': str(item_data['text']), 'formatted': {}}
        
        self.data_manager.save_data(self.groups, pinned_items, self.clipboard_manager.settings)
        print("Groups and pinned items saved")
        
    def edit_group(self, group_id):
        self.show_edit_group_dialog(group_id)

    def delete_group(self, group_id):
        # if tk.messagebox.askyesno("Eliminar Grupo", "¿Está seguro de que desea eliminar este grupo?"):
        del self.groups[group_id]
        self.refresh_groups()
        self.save_groups()

    def add_item_to_group(self, item_id, group_id):
        if group_id in self.groups:
            item_data = self.clipboard_manager.clipboard_items.get(item_id)
            if item_data and item_id not in [item['id'] for item in self.groups[group_id]['items']]:
                self.groups[group_id]['items'].append({
                    'id': item_id,
                    'text': item_data['text']
                })
                self.save_groups()
                if self.groups_window and self.groups_window.winfo_exists():
                    self.refresh_groups()
                print(f"Item {item_id} added to group {group_id}")
                
                # Actualizar la vista principal si es necesario
                if hasattr(self.clipboard_manager, 'refresh_cards'):
                    self.clipboard_manager.refresh_cards()
            else:
                print(f"Item {item_id} already in group {group_id} or not found")
        else:
            print(f"Group {group_id} not found")
            
    def on_main_window_close(self, event):
        if self.groups_window and self.groups_window.winfo_exists():
            self.groups_window.destroy()
            
    def close_groups_window(self):
        self.groups_window.destroy()
        self.clipboard_manager.show_main_screen()
            
    # ----------------------------------------------------------------------
    
    def show_group_dialog(self, group_id=None):
        is_edit = group_id is not None
        dialog = tk.Toplevel(self.master)
        dialog.title("Editar Grupo" if is_edit else "Nuevo Grupo")
        
        x = self.clipboard_manager.window_x + 40
        y = self.clipboard_manager.window_y + 40
        
        dialog.geometry(f"200x114+{x}+{y}")
        
        dialog.configure(bg=self.theme_manager.colors['dark']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)

        # Barra de título personalizada
        title_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        title_frame.pack(fill=tk.X, padx=4, pady=(4, 0))

        title_label = tk.Label(title_frame, text="Editar Grupo" if is_edit else "Nuevo Grupo", 
                            font=('Segoe UI', 10, 'bold'),
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        title_label.pack(side=tk.LEFT, padx=0)

        close_button = tk.Button(title_frame, text="❌", command=dialog.destroy,
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=0,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'])
        close_button.pack(side=tk.RIGHT)

        # Contenido
        content_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=0)

        name_label = tk.Label(content_frame, text="Nombre del grupo:",
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        name_label.pack(anchor='w', pady=(0, 5))

        name_entry = tk.Entry(content_frame, bg=self.theme_manager.colors['dark']['button_bg'],
                            fg=self.theme_manager.colors['dark']['fg'],
                            insertbackground=self.theme_manager.colors['dark']['fg'],
                            relief=tk.FLAT, bd=0, highlightthickness=1,
                            highlightcolor=self.theme_manager.colors['dark'].get('highlight', '#555555'),
                            highlightbackground=self.theme_manager.colors['dark'].get('border', '#333333'))
        name_entry.pack(fill=tk.X, pady=(0, 5))

        if is_edit:
            name_entry.insert(0, self.groups[group_id]['name'])

        def save_group():
            name = name_entry.get().strip()
            if name:
                if is_edit:
                    self.groups[group_id]['name'] = name
                else:
                    new_group_id = str(uuid.uuid4())
                    self.groups[new_group_id] = {'name': name, 'items': []}
                self.refresh_groups()
                self.save_groups()
                dialog.destroy()

        save_button = tk.Button(content_frame, text="Guardar", command=save_group,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'],
                                activebackground=self.theme_manager.colors['dark'].get('active_bg', '#4E4E4E'),
                                activeforeground=self.theme_manager.colors['dark'].get('active_fg', '#FFFFFF'),
                                relief=tk.FLAT, bd=0, padx=4, pady=6)
        save_button.pack(fill=tk.X, pady=(0, 0))

        # Hacer la ventana arrastrable
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

        dialog.focus_set()
        name_entry.focus()

    def add_group(self):
        self.show_group_dialog()

    def edit_group(self, group_id):
        self.show_group_dialog(group_id)    
    
    # def add_group(self):
    #     dialog = tk.Toplevel(self.master)
    #     dialog.title("Nuevo Grupo")
    #     dialog.geometry("200x115")
        
    #     # Calcula la posición relativa a la ventana principal
    #     x = self.clipboard_manager.window_x + 40
    #     y = self.clipboard_manager.window_y + 40
        
    #     dialog.geometry(f"+{x}+{y}")
        
    #     dialog.configure(bg=self.theme_manager.colors['dark']['bg'])
    #     dialog.overrideredirect(True)
    #     dialog.attributes('-topmost', True)

    #     # Barra de título personalizada
    #     title_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
    #     title_frame.pack(fill=tk.X, padx=4, pady=(4, 0))

    #     title_label = tk.Label(title_frame, text="Nuevo Grupo", font=('Segoe UI', 10, 'bold'),
    #                         bg=self.theme_manager.colors['dark']['bg'],
    #                         fg=self.theme_manager.colors['dark']['fg'])
    #     title_label.pack(side=tk.LEFT, padx=0)

    #     close_button = tk.Button(title_frame, text="❌", command=dialog.destroy,
    #                             font=('Segoe UI', 10, 'bold'), bd=0, padx=0,
    #                             bg=self.theme_manager.colors['dark']['button_bg'],
    #                             fg=self.theme_manager.colors['dark']['button_fg'])
    #     close_button.pack(side=tk.RIGHT)

    #     # Contenido
    #     content_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
    #     content_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=0)

    #     name_label = tk.Label(content_frame, text="Nombre del grupo:",
    #                         bg=self.theme_manager.colors['dark']['bg'],
    #                         fg=self.theme_manager.colors['dark']['fg'])
    #     name_label.pack(anchor='w', pady=(0, 5))

    #     name_entry = tk.Entry(content_frame, bg=self.theme_manager.colors['dark']['button_bg'],
    #                         fg=self.theme_manager.colors['dark']['fg'],
    #                         insertbackground=self.theme_manager.colors['dark']['fg'],
    #                         relief=tk.FLAT,  # Quita el efecto 3D
    #                         bd=0,  # Quita el borde
    #                         highlightthickness=1,  # Añade un borde fino
    #                         highlightcolor=self.theme_manager.colors['dark'].get('highlight', '#555555'),  # Color del borde cuando tiene foco
    #                         highlightbackground=self.theme_manager.colors['dark'].get('border', '#333333'))  # Color del borde cuando no tiene foco
    #     name_entry.pack(fill=tk.X, pady=(0, 0))

    #     def save_group():
    #         name = name_entry.get().strip()
    #         if name:
    #             group_id = str(uuid.uuid4())
    #             self.groups[group_id] = {'name': name, 'items': []}
    #             self.refresh_groups()
    #             self.save_groups()
    #             dialog.destroy()

    #     save_button = tk.Button(content_frame, text="Guardar", command=save_group,
    #                             bg=self.theme_manager.colors['dark']['button_bg'],
    #                             fg=self.theme_manager.colors['dark']['button_fg'],
    #                             activebackground=self.theme_manager.colors['dark'].get('active_bg', '#4E4E4E'),
    #                             activeforeground=self.theme_manager.colors['dark'].get('active_fg', '#FFFFFF'),
    #                             relief=tk.FLAT,  # Elimina el estilo 3D
    #                             bd=0,  # Elimina el borde
    #                             padx=4, pady=5)
    #     save_button.pack(fill=tk.X, expand=True, pady=(0, 0))

    #     # Hacer la ventana arrastrable
    #     def start_move(event):
    #         dialog.x = event.x
    #         dialog.y = event.y

    #     def on_move(event):
    #         deltax = event.x - dialog.x
    #         deltay = event.y - dialog.y
    #         x = dialog.winfo_x() + deltax
    #         y = dialog.winfo_y() + deltay
    #         dialog.geometry(f"+{x}+{y}")

    #     title_frame.bind('<Button-1>', start_move)
    #     title_frame.bind('<B1-Motion>', on_move)

    #     # Centrar el diálogo en la pantalla
    #     dialog.update_idletasks()
    #     width = dialog.winfo_width()
    #     height = dialog.winfo_height()
    #     x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    #     y = (dialog.winfo_screenheight() // 2) - (height // 2)
    #     dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    #     dialog.focus_set()
    #     name_entry.focus()
        
    # # ----------------------------------------------------------------------------------
    
    # def show_edit_group_dialog(self, group_id):
    #     dialog = tk.Toplevel(self.master)
    #     dialog.title("Editar Grupo")
    #     # dialog.geometry("200x115")
        
    #     # Calcula la posición relativa a la ventana principal
    #     x = self.clipboard_manager.window_x + 40
    #     y = self.clipboard_manager.window_y + 40
        
    #     dialog.geometry(f"200x115+{x}+{y}")
        
    #     dialog.configure(bg=self.theme_manager.colors['dark']['bg'])
    #     dialog.overrideredirect(True)
    #     dialog.attributes('-topmost', True)

    #     # Barra de título personalizada
    #     title_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
    #     title_frame.pack(fill=tk.X, padx=4, pady=(4, 0))

    #     title_label = tk.Label(title_frame, text="Editar Grupo", font=('Segoe UI', 10, 'bold'),
    #                         bg=self.theme_manager.colors['dark']['bg'],
    #                         fg=self.theme_manager.colors['dark']['fg'])
    #     title_label.pack(side=tk.LEFT, padx=0)

    #     close_button = tk.Button(title_frame, text="❌", command=dialog.destroy,
    #                             font=('Segoe UI', 10, 'bold'), bd=0, padx=0,
    #                             bg=self.theme_manager.colors['dark']['button_bg'],
    #                             fg=self.theme_manager.colors['dark']['button_fg'])
    #     close_button.pack(side=tk.RIGHT)

    #     # Contenido
    #     content_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
    #     content_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=0)

    #     name_label = tk.Label(content_frame, text="Nuevo nombre del grupo:",
    #                         bg=self.theme_manager.colors['dark']['bg'],
    #                         fg=self.theme_manager.colors['dark']['fg'])
    #     name_label.pack(anchor='w', pady=(0, 5))

    #     name_entry = tk.Entry(content_frame, bg=self.theme_manager.colors['dark']['button_bg'],
    #                         fg=self.theme_manager.colors['dark']['fg'],
    #                         insertbackground=self.theme_manager.colors['dark']['fg'],
    #                         relief=tk.FLAT,  # Quita el efecto 3D
    #                         bd=0,  # Quita el borde
    #                         highlightthickness=1,  # Añade un borde fino
    #                         highlightcolor=self.theme_manager.colors['dark'].get('highlight', '#555555'),  # Color del borde cuando tiene foco
    #                         highlightbackground=self.theme_manager.colors['dark'].get('border', '#333333'))  # Color del borde cuando no tiene foco
    #     name_entry.insert(0, self.groups[group_id]['name'])
    #     name_entry.pack(fill=tk.X, pady=(0, 0))

    #     def save_group():
    #         new_name = name_entry.get().strip()
    #         if new_name:
    #             self.groups[group_id]['name'] = new_name
    #             self.refresh_groups()
    #             self.save_groups()
    #             dialog.destroy()

    #     save_button = tk.Button(content_frame, text="Guardar", command=save_group,
    #                             bg=self.theme_manager.colors['dark']['button_bg'],
    #                             fg=self.theme_manager.colors['dark']['button_fg'],
    #                             activebackground=self.theme_manager.colors['dark'].get('active_bg', '#4E4E4E'),
    #                             activeforeground=self.theme_manager.colors['dark'].get('active_fg', '#FFFFFF'),
    #                             relief=tk.FLAT,  # Elimina el estilo 3D
    #                             bd=0,  # Elimina el borde
    #                             padx=4, pady=5)
    #     save_button.pack(fill=tk.X, expand=True, pady=(0, 0))  # Hace que el botón ocupe todo el ancho disponible

    #     # Hacer la ventana arrastrable
    #     def start_move(event):
    #         dialog.x = event.x
    #         dialog.y = event.y

    #     def on_move(event):
    #         deltax = event.x - dialog.x
    #         deltay = event.y - dialog.y
    #         x = dialog.winfo_x() + deltax
    #         y = dialog.winfo_y() + deltay
    #         dialog.geometry(f"+{x}+{y}")

    #     title_frame.bind('<Button-1>', start_move)
    #     title_frame.bind('<B1-Motion>', on_move)

    #     # Centrar el diálogo en la pantalla
    #     dialog.update_idletasks()
    #     width = dialog.winfo_width()
    #     height = dialog.winfo_height()
    #     x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    #     y = (dialog.winfo_screenheight() // 2) - (height // 2)
    #     dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    #     dialog.focus_set()
    #     name_entry.focus()