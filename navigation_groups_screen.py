# navigation_groups_screen.py

from enum import Enum
from typing import List, Optional, Dict
import tkinter as tk
import logging

logger = logging.getLogger(__name__)

class GroupScreenElement(Enum):
    TOP_BUTTONS = "top_buttons"
    GROUP_CARDS = "group_cards"
    ICONS = "card_icons"

class GroupsScreenNavigation:
    def __init__(self, manager):
        self.manager = manager
        self.navigation_state = {'enabled': True}
        self.navigation_order = [
            GroupScreenElement.TOP_BUTTONS,
            GroupScreenElement.GROUP_CARDS
        ]
        self.current_element: Optional[GroupScreenElement] = None
        self.current_index: int = 0
        self.state: Dict = self._initialize_state()
        logger.debug("GroupsScreenNavigation initialized")

    def _initialize_state(self) -> Dict:
        """Inicializa el estado de navegación"""
        return {
            'current_selection': {'type': 'group_cards', 'index': 0},
            'highlight_colors': {
                'dark': {'normal': '#444444', 'icon': '#666666'},
                'light': {'normal': '#cccccc', 'icon': '#aaaaaa'}
            }
        }

    def initialize_focus(self) -> None:
        """Inicializa el foco en la pantalla de grupos"""
        if self.get_cards_count() > 0:
            self.state['current_selection'] = {'type': 'group_cards', 'index': 0}
        else:
            self.state['current_selection'] = {'type': 'top_buttons', 'index': 0}
        
        self.navigation_state['enabled'] = True
        self.update_highlights()
        logger.debug(f"Groups focus initialized: {self.state['current_selection']}")

    def navigate_vertical(self, event) -> None:
        """Gestiona la navegación vertical"""
        direction = 1 if event.keysym == 'Down' else -1
        self._update_selection_vertical(direction)
        self.update_highlights()
        self.ensure_visible()
        logger.debug(f"Vertical navigation: {event.keysym}")

    def _update_selection_vertical(self, direction: int) -> None:
        """Actualiza la selección actual en dirección vertical"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        if direction > 0:  # Down
            if current_type == GroupScreenElement.TOP_BUTTONS.value:
                if self.get_cards_count() > 0:
                    self.state['current_selection'] = {
                        'type': GroupScreenElement.GROUP_CARDS.value,
                        'index': 0
                    }
            elif current_type == GroupScreenElement.GROUP_CARDS.value:
                if current_index < self.get_cards_count() - 1:
                    self.state['current_selection']['index'] = current_index + 1
        else:  # Up
            if current_type == GroupScreenElement.GROUP_CARDS.value:
                if current_index > 0:
                    self.state['current_selection']['index'] = current_index - 1
                else:
                    self.state['current_selection'] = {
                        'type': GroupScreenElement.TOP_BUTTONS.value,
                        'index': 0
                    }

    def navigate_horizontal(self, event) -> None:
        """Gestiona la navegación horizontal"""
        direction = 1 if event.keysym == 'Right' else -1
        self._update_selection_horizontal(direction)
        self.update_highlights()
        logger.debug(f"Horizontal navigation: {event.keysym}")

    def _update_selection_horizontal(self, direction: int) -> None:
        """Actualiza la selección actual en dirección horizontal"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        if direction > 0:  # Right
            if current_type == GroupScreenElement.TOP_BUTTONS.value:
                button_count = len(self.get_top_buttons())
                self.state['current_selection']['index'] = (current_index + 1) % button_count
            elif current_type == GroupScreenElement.GROUP_CARDS.value:
                self.state['current_selection'] = {
                    'type': GroupScreenElement.ICONS.value,
                    'index': current_index * 2  # Solo 2 iconos por tarjeta en grupos
                }
            elif current_type == GroupScreenElement.ICONS.value:
                if current_index % 2 < 1:  # Solo 2 iconos por tarjeta
                    self.state['current_selection']['index'] = current_index + 1
        else:  # Left
            if current_type == GroupScreenElement.TOP_BUTTONS.value:
                button_count = len(self.get_top_buttons())
                self.state['current_selection']['index'] = (current_index - 1) % button_count
            elif current_type == GroupScreenElement.ICONS.value:
                if current_index % 2 > 0:
                    self.state['current_selection']['index'] = current_index - 1
                else:
                    self.state['current_selection'] = {
                        'type': GroupScreenElement.GROUP_CARDS.value,
                        'index': current_index // 2
                    }

    def activate_selected(self, event=None) -> None:
        """Activa el elemento seleccionado actualmente"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        actions = {
            GroupScreenElement.TOP_BUTTONS.value: self._activate_top_button,
            GroupScreenElement.GROUP_CARDS.value: self._activate_group_card,
            GroupScreenElement.ICONS.value: self._activate_icon
        }

        if handler := actions.get(current_type):
            handler(current_index)
            logger.debug(f"Activated {current_type} at index {current_index}")

    def update_highlights(self) -> None:
        """Actualiza los destacados visuales"""
        self._clear_all_highlights()
        self._highlight_current_selection()
        logger.debug("Highlights updated")

    def _clear_all_highlights(self) -> None:
        """Limpia todos los destacados visuales"""
        theme = self.manager.theme_manager.colors[
            'dark' if self.manager.is_dark_mode else 'light'
        ]
        base_color = theme['card_bg']
        button_color = theme['button_bg']

        # Limpiar botones superiores
        for button in self.get_top_buttons():
            button.configure(bg=button_color)

        # Limpiar tarjetas y sus iconos
        for card in self.manager.group_manager.groups_frame.winfo_children():
            self._reset_card_colors(card, base_color, button_color)

    def _highlight_card(self, card: tk.Frame, color: str) -> None:
        """Resalta una tarjeta específica y sus elementos"""
        card.configure(bg=color)
        for child in card.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=color)
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.configure(bg=color)
                    elif isinstance(subchild, tk.Button):
                        # No cambiar el color de los botones aquí
                        # a menos que estemos en modo tarjeta
                        if self.state['current_selection']['type'] == GroupScreenElement.GROUP_CARDS.value:
                            subchild.configure(bg=color)
            elif isinstance(child, tk.Label):
                child.configure(bg=color)
            elif isinstance(child, tk.Button):
                if self.state['current_selection']['type'] == GroupScreenElement.GROUP_CARDS.value:
                    child.configure(bg=color)

    def _reset_card_colors(self, card: tk.Frame, base_color: str, button_color: str) -> None:
        """Resetea los colores de una tarjeta específica y sus elementos"""
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
    
    def _highlight_current_selection(self) -> None:
        """Aplica el destacado al elemento actualmente seleccionado"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        highlight_color = self._get_highlight_color()
        icon_highlight_color = self._get_icon_highlight_color()

        if current_type == GroupScreenElement.TOP_BUTTONS.value:
            buttons = self.get_top_buttons()
            if 0 <= current_index < len(buttons):
                buttons[current_index].configure(bg=highlight_color)

        elif current_type == GroupScreenElement.GROUP_CARDS.value:
            cards = self.get_group_cards()
            if current_index < len(cards):
                self._highlight_card(cards[current_index], highlight_color)

        elif current_type == GroupScreenElement.ICONS.value:
            cards = self.get_group_cards()
            card_index = current_index // 2
            icon_index = current_index % 2

            if card_index < len(cards):
                card = cards[card_index]
                # Resaltar la tarjeta completa
                self._highlight_card(card, highlight_color)

                # Resaltar el icono específico
                icons_frame = self._find_icons_frame(card)
                if icons_frame:
                    # Primero resetear todos los iconos al color base
                    for icon in icons_frame.winfo_children():
                        icon.configure(bg=highlight_color)
                    
                    # Luego resaltar el icono seleccionado
                    if icon_index < len(icons_frame.winfo_children()):
                        icons_frame.winfo_children()[icon_index].configure(bg=icon_highlight_color)

        # Forzar la actualización visual
        self.manager.root.update_idletasks()
    
    def _get_highlight_color(self) -> str:
        """Obtiene el color de resaltado según el tema actual"""
        theme_type = 'dark' if self.manager.is_dark_mode else 'light'
        return self.state['highlight_colors'][theme_type]['normal']

    def _get_icon_highlight_color(self) -> str:
        """Obtiene el color de resaltado para iconos según el tema actual"""
        theme_type = 'dark' if self.manager.is_dark_mode else 'light'
        return self.state['highlight_colors'][theme_type]['icon']
    
    def _find_icons_frame(self, card: tk.Frame) -> Optional[tk.Frame]:
        """Encuentra el frame de iconos en una tarjeta"""
        for child in card.winfo_children():
            if isinstance(child, tk.Frame) and len(child.winfo_children()) > 0:
                if all(isinstance(btn, tk.Button) for btn in child.winfo_children()):
                    return child
        return None

    def _activate_top_button(self, index: int) -> None:
        """Activa un botón superior"""
        buttons = self.get_top_buttons()
        if 0 <= index < len(buttons):
            buttons[index].invoke()

    def _activate_group_card(self, index: int) -> None:
        """Activa una tarjeta de grupo"""
        groups = list(self.manager.group_manager.groups.items())
        if index < len(groups):
            group_id, _ = groups[index]
            self.manager.group_manager.show_group_content(group_id)

    def _activate_icon(self, index: int) -> None:
        """Activa un icono"""
        card_index = index // 2
        icon_index = index % 2
        groups = list(self.manager.group_manager.groups.items())
        
        if card_index < len(groups):
            group_id, _ = groups[card_index]
            actions = {
                0: lambda: self.manager.group_manager.edit_group(group_id),
                1: lambda: self.manager.group_manager.delete_group(group_id)
            }
            if action := actions.get(icon_index):
                action()

    def ensure_visible(self) -> None:
        """Asegura que el elemento seleccionado esté visible"""
        current_type = self.state['current_selection']['type']
        if current_type in [GroupScreenElement.GROUP_CARDS.value, GroupScreenElement.ICONS.value]:
            current_index = self.state['current_selection']['index']
            card_index = current_index // 2 if current_type == GroupScreenElement.ICONS.value else current_index
            cards = self.get_group_cards()
            
            if card_index < len(cards):
                card = cards[card_index]
                bbox = self.manager.group_manager.canvas.bbox("all")
                if bbox:
                    card_y = card.winfo_y()
                    canvas_height = self.manager.group_manager.canvas.winfo_height()
                    if card_y > 0:
                        self.manager.group_manager.canvas.yview_moveto(card_y / bbox[3])

    def get_top_buttons(self) -> List[tk.Button]:
        """Obtiene los botones superiores"""
        return [
            self.manager.group_manager.add_button,
            self.manager.group_manager.close_button
        ]

    def get_group_cards(self) -> List[tk.Frame]:
        """Obtiene las tarjetas de grupo"""
        return self.manager.group_manager.groups_frame.winfo_children()

    def get_cards_count(self) -> int:
        """Obtiene el número de tarjetas"""
        return len(self.manager.group_manager.groups)

    def refresh_view(self) -> None:
        """Refresca la vista de grupos"""
        self.manager.group_manager.refresh_groups()
        self.update_highlights()