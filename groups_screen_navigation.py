import tkinter as tk
import logging

logger = logging.getLogger(__name__)

class GroupsScreenNavigation:
    def __init__(self, manager):
        self.manager = manager
        self.navigation_order = ['top_buttons', 'group_cards']
        logger.debug("GroupsScreenNavigation inicializado")

    def navigate_vertical(self, event):
        logger.debug(f"Navegación vertical: {event.keysym}")
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if event.keysym == 'Up':
            self.move_up(current_type, current_index)
        elif event.keysym == 'Down':
            self.move_down(current_type, current_index)

        self.update_highlights()
        self.ensure_visible()
        logger.debug(f"Nueva selección: {self.manager.current_selection}")

    def move_up(self, current_type, current_index):
        logger.debug(f"Moviendo arriba desde {current_type}, {current_index}")
        if current_type == 'group_cards':
            if current_index > 0:
                self.manager.current_selection['index'] = current_index - 1
            else:
                self.manager.current_selection = {'type': 'top_buttons', 'index': 0}
        elif current_type == 'group_card_icons':
            card_index = current_index // 3
            self.manager.current_selection = {'type': 'group_cards', 'index': card_index}
        elif current_type == 'top_buttons':
            pass  # No hacer nada si ya estamos en los botones superiores
        
    def move_down(self, current_type, current_index):
        logger.debug(f"Moviendo abajo desde {current_type}, {current_index}")
        if current_type == 'top_buttons':
            if self.get_group_cards_count() > 0:
                self.manager.current_selection = {'type': 'group_cards', 'index': 0}
        elif current_type == 'group_cards':
            if current_index < self.get_group_cards_count() - 1:
                self.manager.current_selection['index'] = current_index + 1
        elif current_type == 'group_card_icons':
            card_index = current_index // 3
            if card_index < self.get_group_cards_count() - 1:
                self.manager.current_selection = {'type': 'group_cards', 'index': card_index + 1}
                
    def navigate_horizontal(self, event):
        logger.debug(f"Navegación horizontal: {event.keysym}")
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']

        if event.keysym == 'Left':
            self.move_left(current_type, current_index)
        elif event.keysym == 'Right':
            self.move_right(current_type, current_index)

        self.update_highlights()

    def move_left(self, current_type, current_index):
        num_buttons = len(self.get_top_buttons())
        if current_type == 'top_buttons':
            self.manager.current_selection['index'] = (current_index - 1) % self.get_top_button_count
        elif current_type == 'group_card_icons':
            if current_index % 3 > 0:
                self.manager.current_selection['index'] = current_index - 1
            else:
                self.manager.current_selection = {'type': 'group_cards', 'index': current_index // 3}

    def move_right(self, current_type, current_index):
        num_buttons = len(self.get_top_buttons())
        if current_type == 'top_buttons':
            self.manager.current_selection['index'] = (current_index + 1) % num_buttons
        elif current_type == 'group_cards':
            icons = self.get_card_icons(self.get_group_cards()[current_index])
            if icons:
                self.manager.current_selection = {'type': 'group_card_icons', 'index': current_index * 3}
        elif current_type == 'group_card_icons':
            card_index = current_index // 3
            icon_position = current_index % 3
            icons = self.get_card_icons(self.get_group_cards()[card_index])
            if icon_position < len(icons) - 1:
                self.manager.current_selection['index'] = current_index + 1

    def activate_selected(self, event=None):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']

        if current_type == 'top_buttons':
            self.activate_top_button(current_index)
        elif current_type == 'group_cards':
            self.activate_group_card(current_index)
        elif current_type == 'group_card_icons':
            self.activate_group_card_icon(current_index)

    def activate_top_button(self, index):
        if index == 0:  # Botón Añadir Grupo
            self.manager.group_manager.add_group()
        elif index == 1:  # Botón Cerrar
            self.manager.group_manager.close_groups_window()

    def activate_group_card(self, index):
        groups = list(self.manager.group_manager.groups.items())
        if index < len(groups):
            group_id, _ = groups[index]
            self.manager.group_manager.show_group_content(group_id)

    def activate_group_card_icon(self, index):
        groups = list(self.manager.group_manager.groups.items())
        card_index = index // 3
        icon_position = index % 2
        
        if card_index < len(groups):
            group_id, _ = groups[card_index]
            if icon_position == 0:  # Edit
                self.manager.group_manager.edit_group(group_id)
            elif icon_position == 1:  # Delete
                self.manager.group_manager.delete_group(group_id)

    def update_highlights(self):
        self.clear_all_highlights()
        
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        highlight_color = '#444444' if self.manager.is_dark_mode else '#cccccc'
        icon_highlight_color = '#666666' if self.manager.is_dark_mode else '#aaaaaa'
        
        if current_type == 'top_buttons':
            top_buttons = self.get_top_buttons()
            if 0 <= current_index < len(top_buttons):
                top_buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == 'group_cards':
            group_cards = self.get_group_cards()
            if current_index < len(group_cards):
                self.highlight_group_card(group_cards[current_index], highlight_color)
        
        elif current_type == 'group_card_icons':
            card_index = current_index // 3
            icon_position = current_index % 3
            group_cards = self.get_group_cards()
            
            if card_index < len(group_cards):
                card = group_cards[card_index]
                icons = self.get_card_icons(card)
                
                if icons and 0 <= icon_position < len(icons):
                    self.highlight_group_card(card, highlight_color)
                    icons[icon_position].configure(bg=icon_highlight_color)

    def clear_all_highlights(self):
        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        base_color = theme['card_bg']
        button_color = theme['button_bg']
        
        for button in self.get_top_buttons():
            button.configure(bg=button_color)
        
        for card in self.get_group_cards():
            self.reset_card_colors(card, base_color, button_color)

    def reset_card_colors(self, card, base_color, button_color):
        card.configure(bg=base_color)
        for child in card.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=base_color)
            elif isinstance(child, tk.Frame):  # Frame de iconos
                child.configure(bg=base_color)
                for icon in child.winfo_children():
                    if isinstance(icon, tk.Button):
                        icon.configure(bg=button_color)

    def highlight_group_card(self, card, color):
        card.configure(bg=color)
        for child in card.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=color)
            elif isinstance(child, tk.Frame):  # Para el frame de iconos
                child.configure(bg=color)

    def highlight_group_card(self, card, color):
        card.configure(bg=color)
        for child in card.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=color)
            elif isinstance(child, tk.Frame):  # Frame de iconos
                child.configure(bg=color)
                for icon in child.winfo_children():
                    if isinstance(icon, tk.Button):
                        icon.configure(bg=color)

    def ensure_visible(self):
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if current_type in ['group_cards', 'group_card_icons']:
            group_cards = self.get_group_cards()
            if current_index < len(group_cards):
                widget = group_cards[current_index]
                bbox = self.manager.group_manager.canvas.bbox("all")
                if bbox:
                    widget_y = widget.winfo_y()
                    canvas_height = self.manager.group_manager.canvas.winfo_height()
                    if widget_y > 0:
                        self.manager.group_manager.canvas.yview_moveto(widget_y / bbox[3])

    def initialize_focus(self):
        logger.debug("Inicializando foco")
        if self.get_group_cards_count() > 0:
            self.manager.current_selection = {'type': 'group_cards', 'index': 0}
        else:
            self.manager.current_selection = {'type': 'top_buttons', 'index': 0}
        
        self.update_highlights()
        logger.debug(f"Foco inicial: {self.manager.current_selection}")

    def get_group_cards_count(self):
        return len(self.manager.group_manager.groups)

    def get_top_buttons(self):
        return [self.manager.group_manager.add_button, self.manager.group_manager.close_button]

    def get_group_cards(self):
        return self.manager.group_manager.groups_frame.winfo_children()

    def get_top_button_count(self):
        return len(self.get_top_buttons())

    def get_card_icons(self, card):
        icons_frame = [child for child in card.winfo_children() if isinstance(child, tk.Frame)]
        if icons_frame:
            return icons_frame[0].winfo_children()
        return []