# main_screen_navigation.py

import tkinter as tk

class MainScreenNavigation:
    def __init__(self, manager):
        self.manager = manager
        self.navigation_order = ['top_buttons', 'main_buttons', 'cards']   

    def navigate_vertical(self, event):
        print(f"MainScreenNavigation: Navigating vertically {event.keysym}")
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        print(f"Before navigation: type={current_type}, index={current_index}")
        
        if event.keysym == 'Up':
            self.move_up(current_type, current_index)
        elif event.keysym == 'Down':
            self.move_down(current_type, current_index)

        self.update_highlights()
        self.ensure_visible()
        print(f"After navigation: type={self.manager.current_selection['type']}, index={self.manager.current_selection['index']}")
        self.update_highlights()

    def move_up(self, current_type, current_index):
        if current_type in ['cards', 'icons']:
            if current_index > 0:
                self.manager.current_selection['index'] = current_index - 1
            else:
                self.manager.current_selection = {'type': 'main_buttons', 'index': 0}
        elif current_type == 'main_buttons':
            self.manager.current_selection = {'type': 'top_buttons', 'index': 0}
        elif current_type == 'top_buttons':
            # Si ya estamos en los botones superiores, no hacemos nada
            pass
        print(f"After move_up: {self.manager.current_selection}")
        
    def move_down(self, current_type, current_index):
        if current_type == 'top_buttons':
            self.manager.current_selection = {'type': 'main_buttons', 'index': 0}
        elif current_type == 'main_buttons':
            if self.get_cards_count() > 0:
                self.manager.current_selection = {'type': 'cards', 'index': 0}
        elif current_type == 'cards':
            if current_index < self.get_cards_count() - 1:
                self.manager.current_selection['index'] = current_index + 1
        print(f"After move_down: {self.manager.current_selection}")
        
    def navigate_horizontal(self, event):
        print(f"MainScreenNavigation: Navigating horizontally {event.keysym}")  
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']

        if event.keysym == 'Left':
            self.move_left(current_type, current_index)
        elif event.keysym == 'Right':
            self.move_right(current_type, current_index)

        self.update_highlights()

    def move_left(self, current_type, current_index):
        if current_type in ['top_buttons', 'main_buttons']:
            self.manager.current_selection['index'] = (current_index - 1) % self.get_button_count(current_type)
        elif current_type == 'icons':
            if current_index % 3 > 0:
                self.manager.current_selection['index'] = current_index - 1
            else:
                self.manager.current_selection = {'type': 'cards', 'index': current_index // 3}

    def move_right(self, current_type, current_index):
        if current_type in ['top_buttons', 'main_buttons']:
            self.manager.current_selection['index'] = (current_index + 1) % self.get_button_count(current_type)
        elif current_type == 'cards':
            self.manager.current_selection = {'type': 'icons', 'index': current_index * 3}
        elif current_type == 'icons':
            if current_index % 3 < 2:
                self.manager.current_selection['index'] = current_index + 1

    def activate_selected(self, event=None):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']

        if current_type == 'main_buttons':
            self.activate_main_button(current_index)
        elif current_type == 'top_buttons':
            self.activate_top_button(current_index)
        elif current_type == 'cards':
            self.activate_card(current_index)
        elif current_type == 'icons':
            self.activate_icon(current_index)

    def activate_main_button(self, index):
        if index == 0:  # Botón Grupos
            self.manager.show_groups()
        elif index == 1:  # Botón Pegar (con/sin formato)
            self.manager.functions.toggle_paste_format()
        elif index == 2:  # Botón Borrar Todo
            self.manager.functions.clear_history()

    def activate_top_button(self, index):
        if index == 0:  # Botón Cambiar tema
            self.manager.theme_manager.toggle_theme()
        elif index == 1:  # Botón Configuración
            self.manager.show_settings()
        elif index == 2:  # Botón Cerrar app
            self.manager.functions.exit_app()

    def activate_card(self, index):
        items = list(self.manager.clipboard_items.items())
        if index < len(items):
            item_id, item_data = items[index]
            clipboard_data = item_data['text']
            self.manager.key_manager.paste_content(clipboard_data)
            
    def activate_icon(self, index):
        items = list(self.manager.clipboard_items.keys())
        card_index = index // 3
        icon_position = index % 3
        
        if card_index < len(items):
            item_id = items[card_index]
            if icon_position == 0:  # Arrow
                self.manager.functions.on_arrow_click(item_id)
            elif icon_position == 1:  # Pin
                self.manager.functions.toggle_pin(item_id)
            elif icon_position == 2:  # Delete
                self.manager.functions.delete_item(item_id)

    def initialize_focus(self):
        if self.get_cards_count() > 0:
            self.manager.current_selection = {'type': 'cards', 'index': 0}
        else:
            self.manager.current_selection = {'type': 'main_buttons', 'index': 0}
        
        self.manager.root.focus_force()
        self.manager.root.update_idletasks()
        self.update_highlights()
    
    def update_highlights(self):
        print("Updating highlights")
        self.clear_all_highlights()
        
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        highlight_color = '#444444' if self.manager.is_dark_mode else '#cccccc'
        icon_highlight_color = '#666666' if self.manager.is_dark_mode else '#aaaaaa'
        
        if current_type == 'main_buttons':
            buttons = [self.manager.button1, self.manager.button2, self.manager.button3]
            if 0 <= current_index < len(buttons):
                buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == 'top_buttons':
            top_buttons = [self.manager.theme_button, self.manager.clear_button, self.manager.close_button]
            if 0 <= current_index < len(top_buttons):
                top_buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == 'cards':
            cards = self.manager.cards_frame.winfo_children()
            if current_index < len(cards):
                self.highlight_entire_card(cards[current_index], highlight_color)
        
        elif current_type == 'icons':
            card_index = current_index // 3
            icon_position = current_index % 3
            cards = self.manager.cards_frame.winfo_children()
            
            if card_index < len(cards):
                card = cards[card_index]
                icons_frame = self.find_icons_frame(card)
                
                if icons_frame and icon_position < len(icons_frame.winfo_children()):
                    icons = icons_frame.winfo_children()
                    if 0 <= icon_position < len(icons):
                        self.highlight_entire_card(card, highlight_color)
                        icons[icon_position].configure(bg=icon_highlight_color)
                        
        print(f"Highlighted: {current_type}, index: {current_index}")
        self.manager.root.update_idletasks()
        self.manager.root.after(10, self.manager.root.update)

    def highlight_entire_card(self, card, color):
        card.configure(bg=color)
        for child in card.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=color)
                for subchild in child.winfo_children():
                    if isinstance(subchild, (tk.Label, tk.Button)):
                        subchild.configure(bg=color)
            elif isinstance(child, (tk.Label, tk.Button)):
                child.configure(bg=color)

    def clear_all_highlights(self):
        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        base_color = theme['card_bg']
        button_color = theme['button_bg']
        
        buttons = [self.manager.button1, self.manager.button2, self.manager.button3,
                self.manager.theme_button, self.manager.clear_button, self.manager.close_button]
        for button in buttons:
            button.configure(bg=button_color)
        
        for card in self.manager.cards_frame.winfo_children():
            self.reset_card_colors(card, base_color, button_color)

    def reset_card_colors(self, card, base_color, button_color):
        card.configure(bg=base_color)
        for child in card.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=base_color)
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.configure(bg=base_color)
                    elif isinstance(subchild, tk.Button):
                        subchild.configure(bg=button_color)
            elif isinstance(child, tk.Label):
                child.configure(bg=base_color)
            elif isinstance(child, tk.Button):
                child.configure(bg=button_color)

    def ensure_visible(self):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if current_type == 'cards':
            cards = self.manager.cards_frame.winfo_children()
            if current_index < len(cards):
                widget = cards[current_index]
                bbox = self.manager.canvas.bbox("all")
                if bbox:
                    widget_y = widget.winfo_y()
                    canvas_height = self.manager.canvas.winfo_height()
                    if widget_y > 0:
                        self.manager.canvas.yview_moveto(widget_y / bbox[3])

    def get_cards_count(self):
        return len(self.manager.cards_frame.winfo_children())

    def get_button_count(self, button_type):
        if button_type == 'top_buttons':
            return 3  # Asumiendo que siempre hay 3 botones superiores
        elif button_type == 'main_buttons':
            return 3  # Asumiendo que siempre hay 3 botones principales

    def find_icons_frame(self, card):
        for child in card.winfo_children():
            if isinstance(child, tk.Frame) and child.winfo_children() and isinstance(child.winfo_children()[0], tk.Button):
                return child
        return None