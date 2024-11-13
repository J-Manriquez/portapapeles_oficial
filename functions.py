# functions.py

import tkinter as tk
import uuid
import win32clipboard # type: ignore
import win32gui # type: ignore
import time
import sys
from utils import measure_time

class Functions:
    def __init__(self, manager):
        self.manager = manager
        self.min_card_height = 40  # Altura mínima en píxeles (2 líneas + 2*2 padding)
        self.max_card_height = 76  # Altura máxima en píxeles (4 líneas + 2*2 padding)
        self.line_height = 18  # Altura estimada de una línea de texto


    @measure_time
    def create_card(self, item_id, item_data, index):
        card_width = self.manager.window_width - 4  # Ajuste para el padding
        card_height = max(self.min_card_height, self.calculate_card_height(item_data['text']))

        # Obtén el color de fondo actual
        current_theme = 'dark' if self.manager.is_dark_mode else 'light'
        bg_color = self.manager.theme_manager.colors[current_theme]['card_bg']

        card_container = tk.Frame(self.manager.cards_frame, width=card_width, height=card_height, bg=bg_color)
        card_container.pack(fill=tk.BOTH, padx=2, pady=2)
        card_container.pack_propagate(False)  # Evita que el contenido afecte el tamaño del contenedor

        text_frame = tk.Frame(card_container, bg=bg_color)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Procesamos el texto para mostrarlo de forma limpia
        processed_text = self.process_text(item_data['text'])

        text_label = tk.Label(text_frame, text=processed_text,
                            justify=tk.LEFT, anchor='w', padx=10, pady=5,
                            bg=card_container['bg'],
                            fg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['fg'], width=int(24))
        text_label.pack(fill=tk.X, expand=True, side=tk.LEFT)

        icons_frame = tk.Frame(card_container, bg=card_container['bg'])
        icons_frame.pack(side=tk.RIGHT, padx=3)

        arrow_button = tk.Button(icons_frame, text="➡️",
                                command=lambda: self.on_arrow_click(item_id),
                                font=('Segoe UI', 10), bd=0,
                                padx=2,
                                bg=card_container['bg'],
                                fg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['fg'])
        arrow_button.pack(side=tk.LEFT)
        
        pin_text = "📌" if item_data['pinned'] else "📍"
        pin_button = tk.Button(icons_frame, text=pin_text,
                            command=lambda: self.toggle_pin(item_id),
                            font=('Segoe UI', 10), bd=0,
                            padx=2,
                            bg=card_container['bg'],
                            fg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['fg'])
        pin_button.pack(side=tk.LEFT)

        delete_button = tk.Button(icons_frame, text="✖️",
                                command=lambda: self.delete_item(item_id),
                                font=('Segoe UI', 10), bd=0,
                                padx=2,
                                bg=card_container['bg'],
                                fg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['fg'])
        delete_button.pack(side=tk.LEFT)
        
        return card_container
    
    def calculate_card_height(self, text):
        lines = len(text.split('\n'))
        content_height = min(lines * self.line_height, 4 * self.line_height)  # Máximo 4 líneas
        return min(max(content_height + 4, self.min_card_height), self.max_card_height)
    
    def process_text(self, text):
        """
        Procesa el texto para mostrarlo de forma limpia y ordenada
        """
        # Eliminamos espacios extras y tabulaciones al inicio y final
        text = text.strip()
        
        # Dividimos el texto en líneas
        lines = text.splitlines()
        
        # Eliminamos líneas vacías consecutivas y espacios extras
        clean_lines = []
        prev_empty = False
        for line in lines:
            line = line.strip()
            
            # Si la línea está vacía
            if not line:
                if not prev_empty:  # Solo mantenemos una línea vacía
                    clean_lines.append('')
                    prev_empty = True
            else:
                clean_lines.append(line)
                prev_empty = False
        
        # Tomamos solo las primeras 3 líneas para la vista previa
        preview_lines = clean_lines[:3]
        
        # Si hay más líneas, indicamos cuántas más hay
        if len(clean_lines) > 3:
            remaining_lines = len(clean_lines) - 3
            preview_lines.append(f"+ {remaining_lines} líneas más")
            
        # Unimos las líneas con saltos de línea
        return '\n'.join(preview_lines)

    @measure_time
    def refresh_cards(self):
        if not hasattr(self.manager, 'cards_frame') or not self.manager.cards_frame.winfo_exists():
            print("cards_frame no existe o ha sido destruido")
            return
        # Eliminar tarjetas obsoletas
        existing_cards = {child.item_id: child for child in self.manager.cards_frame.winfo_children() if hasattr(child, 'item_id')}
        
        for item_id in list(existing_cards.keys()):
            if item_id not in self.manager.clipboard_items:
                existing_cards[item_id].destroy()
                del existing_cards[item_id]

        # Actualizar o crear nuevas tarjetas
        for index, (item_id, item_data) in enumerate(self.manager.clipboard_items.items()):
            if item_id in existing_cards:
                card = existing_cards[item_id]
                self.update_card(card, item_data)
            else:
                card = self.create_card(item_id, item_data, index)
                card.item_id = item_id

            card.pack(fill=tk.X, padx=2, pady=2)

        # Actualizar la región de desplazamiento
        self.manager.canvas.update_idletasks()
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))
        self.recalculate_card_heights()
        

    def update_card(self, card, item_data):
        processed_text = self.process_text(item_data['text'])
        text_label = card.winfo_children()[0].winfo_children()[0]
        text_label.config(text=processed_text)

        new_height = self.calculate_card_height(processed_text)
        card.config(height=new_height)

        # Actualizar el estado del botón de pin
        pin_button = card.winfo_children()[1].winfo_children()[1]
        pin_text = "📌" if item_data['pinned'] else "📍"
        pin_button.config(text=pin_text)
        
    def apply_theme_to_card(self, card, theme):
        card.configure(bg=theme['card_bg'])
        
        for child in card.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=theme['card_bg'])
                for subchild in child.winfo_children():
                    if isinstance(subchild, (tk.Label, tk.Button)):
                        subchild.configure(bg=theme['card_bg'], fg=theme['fg'])
            elif isinstance(child, (tk.Label, tk.Button)):
                child.configure(bg=theme['card_bg'], fg=theme['fg'])

    def toggle_pin(self, item_id):
        if item_id in self.manager.clipboard_items:
            self.manager.clipboard_items[item_id]['pinned'] = not self.manager.clipboard_items[item_id]['pinned']
            self.refresh_cards()
            self.manager.group_manager.save_groups()  # Guardar después de cambiar el estado de anclaje

    def delete_item(self, item_id):
        if item_id in self.manager.clipboard_items and not self.manager.clipboard_items[item_id]['pinned']:
            del self.manager.clipboard_items[item_id]
            self.refresh_cards()
            self.manager.group_manager.save_groups()  # Guardar después de eliminar un item

    
    def clear_history(self):
        self.manager.clipboard_items = {k: v for k, v in self.manager.clipboard_items.items() if v['pinned']}
        self.refresh_cards()
        self.manager.group_manager.save_groups()  # Guardar después de limpiar el historial
        if self.manager.current_selection['type'] == 'card':
            self.manager.current_selection = {'type': 'button', 'index': 0}
        self.manager.navigation.update_highlights()

    def on_canvas_configure(self, event):
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.manager.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    @measure_time
    def monitor_clipboard(self):
        while True:
            try:
                clipboard_content = self.get_clipboard_text()
                if clipboard_content and clipboard_content != self.manager.current_clipboard:
                    self.manager.current_clipboard = clipboard_content
                    if clipboard_content not in [item['text'] for item in self.manager.clipboard_items.values()]:
                        new_id = str(uuid.uuid4())
                        new_item = {
                            'text': clipboard_content,
                            'pinned': False,
                            'with_format': self.manager.paste_with_format
                        }
                        # Usar after para actualizar la GUI en el hilo principal
                        self.manager.root.after(0, self.add_clipboard_item, new_id, new_item)
            except Exception as e:
                print(f"Error en monitor_clipboard: {e}")
            time.sleep(0.5)

    def add_clipboard_item(self, new_id, new_item):
        self.manager.clipboard_items[new_id] = new_item
        if len(self.manager.clipboard_items) > 20:
            unpinned_items = [k for k, v in self.manager.clipboard_items.items() if not v['pinned']]
            if unpinned_items:
                del self.manager.clipboard_items[unpinned_items[-1]]
        self.refresh_cards()
        self.manager.group_manager.save_groups()

    # @measure_time
    def get_clipboard_text(self):
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return data
        except Exception as e:
            print(f"Error al obtener texto del portapapeles: {e}")
            return None

    def exit_app(self):
        self.manager.root.quit()
        sys.exit()
    
    @measure_time    
    def toggle_paste_format(self):
        self.manager.paste_with_format = not self.manager.paste_with_format
        new_text = "Con formato" if self.manager.paste_with_format else "Sin formato"
        self.manager.button3.config(text=new_text)
        self.manager.navigation.update_highlights()
        
    @measure_time
    def recalculate_card_heights(self):
        for card in self.manager.cards_frame.winfo_children():
            if hasattr(card, 'item_id'):
                item_data = self.manager.clipboard_items[card.item_id]
                new_height = self.calculate_card_height(item_data['text'])
                card.config(height=new_height)
        
        self.manager.canvas.update_idletasks()
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))
        
    def on_arrow_click(self, item_id):
        if not self.manager.group_manager.groups:
            tk.messagebox.showinfo("Sin Grupos", "No hay grupos disponibles. Cree un grupo primero.")
            return

        dialog = tk.Toplevel(self.manager.root)
        dialog.title("Seleccionar Grupo")
        dialog.geometry("295x400")
        dialog.configure(bg=self.manager.theme_manager.colors['dark']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)

        # Barra de título personalizada
        title_frame = tk.Frame(dialog, bg=dialog.cget('bg'))
        title_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        title_label = tk.Label(title_frame, text="Seleccionar Grupo", font=('Segoe UI', 10, 'bold'),
                            bg=dialog.cget('bg'), fg=self.manager.theme_manager.colors['dark']['fg'])
        title_label.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(title_frame, text="❌", command=dialog.destroy,
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=10,
                                bg=self.manager.theme_manager.colors['dark']['button_bg'],
                                fg=self.manager.theme_manager.colors['dark']['button_fg'])
        close_button.pack(side=tk.RIGHT)

        # Contenido
        content_frame = tk.Frame(dialog, bg=dialog.cget('bg'))
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for group_id, group_info in self.manager.group_manager.groups.items():
            group_button = tk.Button(content_frame, text=group_info['name'],
                                    command=lambda gid=group_id: self.add_to_group(item_id, gid, dialog),
                                    bg=self.manager.theme_manager.colors['dark']['button_bg'],
                                    fg=self.manager.theme_manager.colors['dark']['button_fg'],
                                    activebackground=self.manager.theme_manager.colors['dark']['active_bg'],
                                    activeforeground=self.manager.theme_manager.colors['dark']['active_fg'],
                                    bd=0, padx=10, pady=5, width=30, anchor='w')
            group_button.pack(fill=tk.X, pady=2)

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

    def add_to_group(self, item_id, group_id, dialog):
        self.manager.group_manager.add_item_to_group(item_id, group_id)
        dialog.destroy()
        # tk.messagebox.showinfo("Éxito", "Item agregado al grupo exitosamente.")