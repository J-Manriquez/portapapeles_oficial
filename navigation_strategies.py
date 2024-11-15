from abc import ABC, abstractmethod
import tkinter as tk

class NavigationStrategy(ABC):
    @abstractmethod
    def navigate_vertical(self, event):
        pass

    @abstractmethod
    def navigate_horizontal(self, event):
        pass

    @abstractmethod
    def activate_selected(self, event=None):
        pass

    @abstractmethod
    def update_highlights(self):
        pass

    @abstractmethod
    def initialize_focus(self):
        pass

class MainScreenNavigation(NavigationStrategy):
    def __init__(self, manager):
        self.manager = manager

    def navigate_vertical(self, event):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if current_type == 'card':
            items = list(self.manager.clipboard_items.keys())
            if event.keysym == 'Up':
                if current_index > 0:
                    self.manager.current_selection['index'] = current_index - 1
                else:
                    self.manager.current_selection = {'type': 'button', 'index': 0}
            elif event.keysym == 'Down':
                if current_index < len(items) - 1:
                    self.manager.current_selection['index'] = current_index + 1
        
        elif current_type == 'button':
            if event.keysym == 'Up':
                if current_index < 3:
                    self.manager.current_selection = {'type': 'top_button', 'index': 0}
            elif event.keysym == 'Down':
                if current_index < 3:
                    if len(self.manager.clipboard_items) > 0:
                        self.manager.current_selection = {'type': 'card', 'index': 0}
                else:
                    self.manager.current_selection = {'type': 'button', 'index': 0}
        
        elif current_type == 'top_button':
            if event.keysym == 'Down':
                self.manager.current_selection = {'type': 'button', 'index': 0}
        
        elif current_type == 'icon':
            card_index = current_index // self.manager.icons_per_card
            if event.keysym == 'Up':
                if card_index > 0:
                    self.manager.current_selection = {'type': 'card', 'index': card_index - 1}
                else:
                    self.manager.current_selection = {'type': 'button', 'index': 0}
            elif event.keysym == 'Down':
                if card_index < len(self.manager.clipboard_items) - 1:
                    self.manager.current_selection = {'type': 'card', 'index': card_index + 1}
        
        self.ensure_visible()
        self.update_highlights()

    def navigate_horizontal(self, event):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if current_type == 'card':
            if event.keysym == 'Right':
                self.manager.current_selection = {'type': 'icon', 'index': current_index * self.manager.icons_per_card}
        
        elif current_type == 'icon':
            card_index = current_index // self.manager.icons_per_card
            icon_position = current_index % self.manager.icons_per_card
            
            if event.keysym == 'Left':
                if icon_position > 0:
                    self.manager.current_selection['index'] = current_index - 1
                else:
                    self.manager.current_selection = {'type': 'card', 'index': card_index}
            elif event.keysym == 'Right':
                if icon_position < self.manager.icons_per_card - 1:
                    self.manager.current_selection['index'] = current_index + 1
        
        elif current_type == 'button':
            if current_index < 3:  # Botones 1, 2, pegar
                if event.keysym == 'Left':
                    self.manager.current_selection['index'] = (current_index - 1) % 3
                elif event.keysym == 'Right':
                    self.manager.current_selection['index'] = (current_index + 1) % 3
            else:  # Barra superior
                if event.keysym == 'Left':
                    self.manager.current_selection['index'] = 3 + (current_index - 4) % 3
                elif event.keysym == 'Right':
                    self.manager.current_selection['index'] = 3 + (current_index - 2) % 3
        
        elif current_type == 'top_button':
            if event.keysym == 'Left':
                self.manager.current_selection['index'] = (current_index - 1) % 3
            elif event.keysym == 'Right':
                self.manager.current_selection['index'] = (current_index + 1) % 3
        
        self.update_highlights()

    def activate_selected(self, event=None):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if current_type == 'button':
            if current_index == 0:  # Botón 1
                self.manager.show_groups()
            elif current_index == 1:  # Botón 2
                self.manager.functions.toggle_paste_format()
            elif current_index == 2:  # Botón 3 (Borrar Todo)
                self.manager.functions.clear_history()
            elif current_index == 3:  # Botón Eliminar todas las cards
                self.manager.functions.clear_history()
            elif current_index == 4:  # Botón Cambiar tema
                self.manager.theme_manager.toggle_theme()
            elif current_index == 5:  # Botón Cerrar app
                self.manager.functions.exit_app()
        elif current_type == 'card':
            items = list(self.manager.clipboard_items.items())
            if current_index < len(items):
                item_id, item_data = items[current_index]
                clipboard_data = item_data['text']
                self.manager.key_manager.paste_content(clipboard_data)
        elif current_type == 'icon':
            items = list(self.manager.clipboard_items.keys())
            card_index = current_index // self.manager.icons_per_card
            icon_position = current_index % self.manager.icons_per_card
            
            if card_index < len(items):
                item_id = items[card_index]
                if icon_position == 0:  # Arrow
                    self.manager.functions.on_arrow_click(item_id)
                elif icon_position == 1:  # Pin
                    self.manager.functions.toggle_pin(item_id)
                elif icon_position == 2:  # Delete
                    self.manager.functions.delete_item(item_id)

    def update_highlights(self):
        self.clear_all_highlights()
        
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        highlight_color = '#444444' if self.manager.is_dark_mode else '#cccccc'
        icon_highlight_color = '#666666' if self.manager.is_dark_mode else '#aaaaaa'
        
        if current_type == 'button':
            buttons = [self.manager.button1, self.manager.button2, self.manager.button3]
            if 0 <= current_index < len(buttons):
                buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == 'top_button':
            top_buttons = [self.manager.clear_button, self.manager.theme_button, self.manager.close_button]
            if 0 <= current_index < len(top_buttons):
                top_buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == 'card':
            cards = self.manager.cards_frame.winfo_children()
            if current_index < len(cards):
                card = cards[current_index]
                self.highlight_entire_card(card, highlight_color)
        
        elif current_type == 'icon':
            card_index = current_index // self.manager.icons_per_card
            icon_position = current_index % self.manager.icons_per_card
            cards = self.manager.cards_frame.winfo_children()
            
            if card_index < len(cards):
                card = cards[card_index]
                icons_frame = None
                
                for child in card.winfo_children():
                    if isinstance(child, tk.Frame) and child.winfo_children() and isinstance(child.winfo_children()[0], tk.Button):
                        icons_frame = child
                        break
                
                if icons_frame and icon_position < len(icons_frame.winfo_children()):
                    icons = icons_frame.winfo_children()
                    if 0 <= icon_position < len(icons):
                        icons[icon_position].configure(bg=icon_highlight_color)

    def initialize_focus(self):
        if len(self.manager.clipboard_items) > 0:
            self.manager.current_selection = {'type': 'card', 'index': 0}
        else:
            self.manager.current_selection = {'type': 'button', 'index': 0}
        
        self.manager.root.focus_force()
        self.manager.root.update_idletasks()
        self.update_highlights()

    def clear_all_highlights(self):
        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        base_color = theme['card_bg']
        
        buttons = [self.manager.button1, self.manager.button2, self.manager.button3,
                   self.manager.clear_button, self.manager.theme_button, self.manager.close_button]
        for button in buttons:
            button.configure(bg=theme['button_bg'])
        
        for card in self.manager.cards_frame.winfo_children():
            card.configure(bg=base_color)
            
            for child in card.winfo_children():
                child.configure(bg=base_color)
                if isinstance(child, tk.Frame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, (tk.Label, tk.Button)):
                            subchild.configure(bg=base_color)

    def highlight_entire_card(self, card, color):
        card.configure(bg=color)
    
        text_frame = card.winfo_children()[0]  
        text_frame.configure(bg=color)
        for subwidget in text_frame.winfo_children():
            if isinstance(subwidget, tk.Label):
                subwidget.configure(bg=color)
        
        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        icons_frame = card.winfo_children()[-1]
        icons_frame.configure(bg=theme['card_bg'])
        for icon in icons_frame.winfo_children():
            icon.configure(bg=theme['card_bg'])

    def ensure_visible(self):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if current_type == 'card':
            cards = self.manager.cards_frame.winfo_children()
            if current_index < len(cards):
                widget = cards[current_index]
                bbox = self.manager.canvas.bbox("all")
                if bbox:
                    widget_y = widget.winfo_y()
                    canvas_height = self.manager.canvas.winfo_height()
                    if widget_y > 0:
                        self.manager.canvas.yview_moveto(widget_y / bbox[3])

class GroupsScreenNavigation(NavigationStrategy):
    def __init__(self, manager):
        self.manager = manager
        # Implementar la navegación específica para la pantalla de grupos

class SettingsScreenNavigation(NavigationStrategy):
    def __init__(self, manager):
        self.manager = manager
        # Implementar la navegación específica para la pantalla de configuraciones