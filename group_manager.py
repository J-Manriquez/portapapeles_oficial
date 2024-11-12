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
            title_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

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

            # Marco para la lista de grupos
            self.groups_frame = tk.Frame(self.groups_window, bg=self.theme_manager.colors['dark']['bg'])
            self.groups_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Hacer la ventana arrastrable
            title_label.bind('<Button-1>', self.start_move)
            title_label.bind('<B1-Motion>', self.on_move)

            self.refresh_groups()
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
            group_card = tk.Frame(self.groups_frame, bg=self.theme_manager.colors['dark']['card_bg'])
            group_card.pack(fill=tk.X, padx=5, pady=5)

            name_label = tk.Label(group_card, text=group_info['name'], font=("Segoe UI", 10, "bold"),
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'])
            name_label.pack(side=tk.LEFT, padx=5, pady=5)

            count_label = tk.Label(group_card, text=f"Items: {len(group_info['items'])}",
                                bg=self.theme_manager.colors['dark']['card_bg'],
                                fg=self.theme_manager.colors['dark']['fg'])
            count_label.pack(side=tk.LEFT, padx=5, pady=5)

            view_button = tk.Button(group_card, text="👁️", command=lambda gid=group_id: self.show_group_content(gid),
                                    font=('Segoe UI', 10), bd=0, bg=self.theme_manager.colors['dark']['button_bg'],
                                    fg=self.theme_manager.colors['dark']['button_fg'])
            view_button.pack(side=tk.RIGHT, padx=2, pady=5)

            edit_button = tk.Button(group_card, text="✏️", command=lambda gid=group_id: self.edit_group(gid),
                                    font=('Segoe UI', 10), bd=0, bg=self.theme_manager.colors['dark']['button_bg'],
                                    fg=self.theme_manager.colors['dark']['button_fg'])
            edit_button.pack(side=tk.RIGHT, padx=2, pady=5)

            delete_button = tk.Button(group_card, text="🗑️", command=lambda gid=group_id: self.delete_group(gid),
                                    font=('Segoe UI', 10), bd=0, bg=self.theme_manager.colors['dark']['button_bg'],
                                    fg=self.theme_manager.colors['dark']['button_fg'])
            delete_button.pack(side=tk.RIGHT, padx=2, pady=5)

    def save_groups(self):
        pinned_items = {k: v for k, v in self.clipboard_manager.clipboard_items.items() if v['pinned']}
        self.data_manager.save_data(self.groups, pinned_items)
        print("Groups and pinned items saved")

    def edit_group(self, group_id):
        new_name = simpledialog.askstring("Editar Grupo", "Ingrese el nuevo nombre del grupo:", 
                                          initialvalue=self.groups[group_id]['name'])
        if new_name:
            self.groups[group_id]['name'] = new_name
            self.refresh_groups()
            self.save_groups()

    def delete_group(self, group_id):
        if tk.messagebox.askyesno("Eliminar Grupo", "¿Está seguro de que desea eliminar este grupo?"):
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
        title_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        title_label = tk.Label(title_frame, text=f"Grupo: {self.groups[group_id]['name']}", 
                            font=('Segoe UI', 10, 'bold'),
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        title_label.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(title_frame, text="❌", command=group_window.destroy,
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=10,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'])
        close_button.pack(side=tk.RIGHT)

        # Marco para la lista de items
        items_frame = tk.Frame(group_window, bg=self.theme_manager.colors['dark']['bg'])
        items_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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
        dialog.geometry("295x150")
        dialog.configure(bg=self.theme_manager.colors['dark']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)

        # Barra de título personalizada
        title_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        title_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        title_label = tk.Label(title_frame, text="Nuevo Grupo", font=('Segoe UI', 10, 'bold'),
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        title_label.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(title_frame, text="❌", command=dialog.destroy,
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=10,
                                bg=self.theme_manager.colors['dark']['button_bg'],
                                fg=self.theme_manager.colors['dark']['button_fg'])
        close_button.pack(side=tk.RIGHT)

        # Contenido
        content_frame = tk.Frame(dialog, bg=self.theme_manager.colors['dark']['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        name_label = tk.Label(content_frame, text="Nombre del grupo:",
                            bg=self.theme_manager.colors['dark']['bg'],
                            fg=self.theme_manager.colors['dark']['fg'])
        name_label.pack(pady=(0, 5))

        name_entry = tk.Entry(content_frame, bg=self.theme_manager.colors['dark']['button_bg'],
                            fg=self.theme_manager.colors['dark']['fg'],
                            insertbackground=self.theme_manager.colors['dark']['fg'])
        name_entry.pack(fill=tk.X, pady=(0, 10))

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
                                activeforeground=self.theme_manager.colors['dark'].get('active_fg', '#FFFFFF'))
        save_button.pack()

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