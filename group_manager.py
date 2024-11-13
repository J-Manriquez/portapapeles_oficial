import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import uuid

class GroupManager:
    def __init__(self, master, clipboard_manager):
        self.master = master
        self.clipboard_manager = clipboard_manager
        self.data_manager = clipboard_manager.data_manager
        self.theme_manager = clipboard_manager.theme_manager
        self.groups, _ = self.data_manager.load_data()
        self.groups_window = None
        self.groups_frame = None


    def show_groups_window(self):
        if self.groups_window is None or not self.groups_window.winfo_exists():
            self.groups_window = tk.Toplevel(self.master)
            self.groups_window.title("Grupos")
            self.groups_window.geometry("295x400+0+0")
            self.groups_window.overrideredirect(True)  # Oculta la barra de título
            self.groups_window.configure(bg=self.theme_manager.colors['dark']['bg'])
            self.groups_window.attributes('-topmost', True) # Hacer que la ventana esté siempre en primer plano
            self.master.bind("<Destroy>", self.on_main_window_close) # Vincular el cierre de la ventana principal al cierre de la ventana de grupos

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

            add_button = tk.Button(buttons_frame, text="➕", command=self.add_group, 
                                   font=('Segoe UI', 10), bd=0, padx=10, width=5, height=2,
                                   bg=self.theme_manager.colors['dark']['button_bg'],
                                   fg=self.theme_manager.colors['dark']['button_fg'])
            add_button.pack(side=tk.LEFT)

            close_button = tk.Button(buttons_frame, text="❌", command=self.groups_window.destroy, 
                                     font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2,
                                     bg=self.theme_manager.colors['dark']['button_bg'],
                                     fg=self.theme_manager.colors['dark']['button_fg'])
            close_button.pack(side=tk.LEFT)

            # # Marco para la lista de grupos
            # self.groups_frame = tk.Frame(self.groups_window, bg=self.theme_manager.colors['dark']['bg'])
            # self.groups_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            # # Hacer la ventana arrastrable
            # title_label.bind('<Button-1>', self.start_move)
            # title_label.bind('<B1-Motion>', self.on_move)
            
            # Canvas para scroll y contenedor de grupos
            canvas = tk.Canvas(self.groups_window, bg=self.theme_manager.colors['dark']['bg'], bd=0, highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            # Scrollbar oculto
            scrollbar = ttk.Scrollbar(self.groups_window, orient=tk.VERTICAL, command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Frame contenedor dentro del canvas para el scroll
            self.groups_frame = tk.Frame(canvas, bg=self.theme_manager.colors['dark']['bg'])
            canvas_window = canvas.create_window((0, 0), window=self.groups_frame, anchor='nw', width=295)

            # Ajustar el ancho del frame contenedor al canvas
            def on_canvas_resize(event):
                canvas.itemconfig(canvas_window, width=event.width)

            canvas.bind("<Configure>", on_canvas_resize)

            # Configuración de scroll
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))

            self.groups_frame.bind("<Configure>", on_frame_configure)

            # Función para desplazamiento con la rueda del mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            # Hacer la ventana arrastrable
            title_label.bind('<Button-1>', self.start_move)
            title_label.bind('<B1-Motion>', self.on_move)

            self.refresh_groups()

        # Si la ventana de grupos ya estaba abierta, llevarla al frente
        else:
            self.groups_window.lift()
            self.groups_window.attributes('-topmost', True)
            self.groups_window.after_idle(self.groups_window.attributes, '-topmost', False)
        
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
        if self.groups_frame is None or not self.groups_frame.winfo_exists():
            return

        for widget in self.groups_frame.winfo_children():
            widget.destroy()

        for group_id, group_info in self.groups.items():
            group_card = tk.Frame(self.groups_frame, bg=self.theme_manager.colors['dark']['card_bg'], cursor="hand2")
            group_card.pack(fill=tk.X, padx=4, pady=2)
            
            group_card.bind("<Button-1>", lambda e, gid=group_id: self.show_group_content(gid))

            name_label = tk.Label(group_card, text=group_info['name'], font=("Segoe UI", 10, "bold"),
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'])
            name_label.pack(side=tk.LEFT, padx=5, pady=5)

            count_label = tk.Label(group_card, text=f"Items: {len(group_info['items'])}",
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'])
            count_label.pack(side=tk.LEFT, padx=5, pady=5)
            
            delete_button = tk.Button(group_card, text="    🗑️", command=lambda gid=group_id: self.delete_group(gid),
                                    font=('Segoe UI', 10), bd=0, bg=self.theme_manager.colors['dark']['button_bg'],
                                    fg=self.theme_manager.colors['dark']['button_fg'])
            delete_button.pack(side=tk.RIGHT, padx=2, pady=5)

            edit_button = tk.Button(group_card, text="✏️", command=lambda gid=group_id: self.edit_group(gid),
                                    font=('Segoe UI', 10), bd=0, bg=self.theme_manager.colors['dark']['button_bg'],
                                    fg=self.theme_manager.colors['dark']['button_fg'])
            edit_button.pack(side=tk.RIGHT, padx=2, pady=5)

            
            
    def save_groups(self):
        pinned_items = {k: v for k, v in self.clipboard_manager.clipboard_items.items() if v['pinned']}
        self.data_manager.save_data(self.groups, pinned_items)
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
            
    # ----------------------------------------------------------------------
    
    def show_group_content(self, group_id):
        group_window = tk.Toplevel(self.master)
        group_window.title(f"Contenido del Grupo: {self.groups[group_id]['name']}")
        group_window.geometry("295x400+0+0")
        group_window.overrideredirect(True)
        group_window.configure(bg=self.theme_manager.colors['dark']['bg'])
        group_window.attributes('-topmost', True)

        # Barra de título personalizada
        title_frame = tk.Frame(group_window, bg=self.theme_manager.colors['dark']['bg'])
        title_frame.pack(fill=tk.X, padx=6, pady=(0,0))

        title_label = tk.Label(title_frame, text=f"Grupo: {self.groups[group_id]['name']}", 
                            font=('Segoe UI', 10, 'bold'),
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        title_label.pack(side=tk.LEFT, padx=5, pady=0)

        close_button = tk.Button(title_frame, text="❌", command=group_window.destroy,
                                font=('Segoe UI', 10, 'bold'),bd=0, padx=10, width=5, height=2,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'])
        close_button.pack(side=tk.RIGHT)

        # Marco para la lista de items
        items_frame = tk.Frame(group_window, bg=self.theme_manager.colors['dark']['bg'])
        items_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=2)

        # Mostrar items del grupo
        for item in self.groups[group_id]['items']:
            item_frame = tk.Frame(items_frame, bg=self.theme_manager.colors['dark']['card_bg'])
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            text = item['text'][:50] + '...' if len(item['text']) > 50 else item['text']
            item_label = tk.Label(item_frame, text=text, 
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'],
                                anchor='w', padx=5, pady=5)
            item_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            delete_button = tk.Button(item_frame, text="🗑️", 
                                    command=lambda i=item['id']: self.remove_item_from_group(group_id, i, items_frame),
                                    font=('Segoe UI', 10), bd=0,
                                    bg=self.theme_manager.colors['dark']['button_bg'],
                                    fg=self.theme_manager.colors['dark']['button_fg'])
            delete_button.pack(side=tk.RIGHT, padx=2, pady=2)

        # Hacer la ventana arrastrable
        def start_move(event):
            group_window.x = event.x
            group_window.y = event.y

        def on_move(event):
            deltax = event.x - group_window.x
            deltay = event.y - group_window.y
            x = group_window.winfo_x() + deltax
            y = group_window.winfo_y() + deltay
            group_window.geometry(f"+{x}+{y}")

        title_frame.bind('<Button-1>', start_move)
        title_frame.bind('<B1-Motion>', on_move)

    def remove_item_from_group(self, group_id, item_id, items_frame):
        self.groups[group_id]['items'] = [item for item in self.groups[group_id]['items'] if item['id'] != item_id]
        self.save_groups()
        self.refresh_group_content(group_id, items_frame)

    def refresh_group_content(self, group_id, items_frame):
        for widget in items_frame.winfo_children():
            widget.destroy()
        
        for item in self.groups[group_id]['items']:
            item_frame = tk.Frame(items_frame, bg=self.theme_manager.colors['dark']['card_bg'])
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            text = item['text'][:50] + '...' if len(item['text']) > 50 else item['text']
            item_label = tk.Label(item_frame, text=text, 
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'],
                                anchor='w', padx=5, pady=5)
            item_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            delete_button = tk.Button(item_frame, text="🗑️", 
                                    command=lambda i=item['id']: self.remove_item_from_group(group_id, i, items_frame),
                                    font=('Segoe UI', 10), bd=0,
                                    bg=self.theme_manager.colors['dark']['button_bg'],
                                    fg=self.theme_manager.colors['dark']['button_fg'])
            delete_button.pack(side=tk.RIGHT, padx=2, pady=2)

    # -----------------------------------------------------------------------
    
    
    def add_group(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Nuevo Grupo")
        dialog.geometry("200x115")
        dialog.configure(bg=self.theme_manager.colors['dark']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)

        # Barra de título personalizada
        title_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        title_frame.pack(fill=tk.X, padx=4, pady=(4, 0))

        title_label = tk.Label(title_frame, text="Nuevo Grupo", font=('Segoe UI', 10, 'bold'),
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
                            relief=tk.FLAT,  # Quita el efecto 3D
                            bd=0,  # Quita el borde
                            highlightthickness=1,  # Añade un borde fino
                            highlightcolor=self.theme_manager.colors['dark'].get('highlight', '#555555'),  # Color del borde cuando tiene foco
                            highlightbackground=self.theme_manager.colors['dark'].get('border', '#333333'))  # Color del borde cuando no tiene foco
        name_entry.pack(fill=tk.X, pady=(0, 0))

        def save_group():
            name = name_entry.get().strip()
            if name:
                group_id = str(uuid.uuid4())
                self.groups[group_id] = {'name': name, 'items': []}
                self.refresh_groups()
                self.save_groups()
                dialog.destroy()

        save_button = tk.Button(content_frame, text="Guardar", command=save_group,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'],
                                activebackground=self.theme_manager.colors['dark'].get('active_bg', '#4E4E4E'),
                                activeforeground=self.theme_manager.colors['dark'].get('active_fg', '#FFFFFF'),
                                relief=tk.FLAT,  # Elimina el estilo 3D
                                bd=0,  # Elimina el borde
                                padx=4, pady=5)
        save_button.pack(fill=tk.X, expand=True, pady=(0, 0))

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

        # Centrar el diálogo en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        dialog.focus_set()
        name_entry.focus()
        
    # ----------------------------------------------------------------------------------
    
    def show_edit_group_dialog(self, group_id):
        dialog = tk.Toplevel(self.master)
        dialog.title("Editar Grupo")
        dialog.geometry("200x115")
        dialog.configure(bg=self.theme_manager.colors['dark']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)

        # Barra de título personalizada
        title_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        title_frame.pack(fill=tk.X, padx=4, pady=(4, 0))

        title_label = tk.Label(title_frame, text="Editar Grupo", font=('Segoe UI', 10, 'bold'),
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

        name_label = tk.Label(content_frame, text="Nuevo nombre del grupo:",
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        name_label.pack(anchor='w', pady=(0, 5))

        name_entry = tk.Entry(content_frame, bg=self.theme_manager.colors['dark']['button_bg'],
                            fg=self.theme_manager.colors['dark']['fg'],
                            insertbackground=self.theme_manager.colors['dark']['fg'],
                            relief=tk.FLAT,  # Quita el efecto 3D
                            bd=0,  # Quita el borde
                            highlightthickness=1,  # Añade un borde fino
                            highlightcolor=self.theme_manager.colors['dark'].get('highlight', '#555555'),  # Color del borde cuando tiene foco
                            highlightbackground=self.theme_manager.colors['dark'].get('border', '#333333'))  # Color del borde cuando no tiene foco
        name_entry.insert(0, self.groups[group_id]['name'])
        name_entry.pack(fill=tk.X, pady=(0, 0))

        def save_group():
            new_name = name_entry.get().strip()
            if new_name:
                self.groups[group_id]['name'] = new_name
                self.refresh_groups()
                self.save_groups()
                dialog.destroy()

        save_button = tk.Button(content_frame, text="Guardar", command=save_group,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'],
                                activebackground=self.theme_manager.colors['dark'].get('active_bg', '#4E4E4E'),
                                activeforeground=self.theme_manager.colors['dark'].get('active_fg', '#FFFFFF'),
                                relief=tk.FLAT,  # Elimina el estilo 3D
                                bd=0,  # Elimina el borde
                                padx=4, pady=5)
        save_button.pack(fill=tk.X, expand=True, pady=(0, 0))  # Hace que el botón ocupe todo el ancho disponible

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

        # Centrar el diálogo en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        dialog.focus_set()
        name_entry.focus()