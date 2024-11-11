# functions.py

import tkinter as tk
import uuid
import win32clipboard
import win32gui
import time
import sys

class Functions:
    def __init__(self, manager):
        self.manager = manager

    def create_card(self, item_id, item_data, index):
        card_width = self.manager.window_width + 1

        card_container = tk.Frame(self.manager.cards_frame, width=card_width)
        card_container.pack(fill=tk.BOTH, padx=2, pady=2)

        text_frame = tk.Frame(card_container)
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


    def refresh_cards(self):
        for widget in self.manager.cards_frame.winfo_children():
            widget.destroy()

        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        
        for index, (item_id, item_data) in enumerate(self.manager.clipboard_items.items()):
            card = self.create_card(item_id, item_data, index)
            self.apply_theme_to_card(card, theme)

        self.manager.canvas.update_idletasks()
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))

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

    def delete_item(self, item_id):
        if item_id in self.manager.clipboard_items and not self.manager.clipboard_items[item_id]['pinned']:
            del self.manager.clipboard_items[item_id]
            self.refresh_cards()

    def on_arrow_click(self, index):
        pass

    def clear_history(self):
        self.manager.clipboard_items = {k: v for k, v in self.manager.clipboard_items.items() if v['pinned']}
        self.refresh_cards()

    def on_canvas_configure(self, event):
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.manager.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def monitor_clipboard(self):
        while True:
            clipboard_content = self.get_clipboard_text()
            if clipboard_content and clipboard_content != self.manager.current_clipboard:
                self.manager.current_clipboard = clipboard_content
                if clipboard_content not in [item['text'] for item in self.manager.clipboard_items.values()]:
                    new_id = str(uuid.uuid4())
                    self.manager.clipboard_items[new_id] = {
                        'text': clipboard_content,
                        'pinned': False
                    }
                    if len(self.manager.clipboard_items) > 20:
                        unpinned_items = [k for k, v in self.manager.clipboard_items.items() if not v['pinned']]
                        if unpinned_items:
                            del self.manager.clipboard_items[unpinned_items[-1]]
                    self.manager.root.after(0, self.refresh_cards)  # Ejecuta refresh_cards en el hilo principal
            time.sleep(1)

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
        
        
        