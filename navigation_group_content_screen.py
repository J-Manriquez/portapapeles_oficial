# navigation_group_content_screen.py

from enum import Enum
from typing import List, Optional, Dict
import tkinter as tk
import logging

from navigation_groups_screen import GroupScreenElement

logger = logging.getLogger(__name__)

class GroupContentElement(Enum):
    TOP_BUTTONS = "top_buttons"  # Para el botón de cerrar
    CONTENT_CARDS = "content_cards"
    ICONS = "icons"

class GroupContentScreenNavigation:
    def __init__(self, manager):
        self.manager = manager
        self.navigation_state = {'enabled': True}
        self.navigation_order = [
            GroupContentElement.TOP_BUTTONS,
            GroupContentElement.CONTENT_CARDS
        ]
        self.current_element: Optional[GroupContentElement] = None
        self.current_index: int = 0
        self.state: Dict = self._initialize_state()
        self.last_keyboard_selection = None
        # logger.debug("GroupContentScreenNavigation initialized")

    def _initialize_state(self) -> Dict:
        """Inicializa el estado de navegación"""
        return {
            'current_selection': {'type': 'content_cards', 'index': 0},
            'highlight_colors': {
                'dark': {
                    'normal': self.manager.theme_manager.colors['dark']['hover_bg'], 
                    'icon': self.manager.theme_manager.colors['dark']['icon_hover_bg']
                },
                'light': {
                    'normal': self.manager.theme_manager.colors['light']['hover_bg'], 
                    'icon': self.manager.theme_manager.colors['light']['icon_hover_bg']
                }
            }
        }

    def initialize_focus(self) -> None:
        """Inicializa el foco en la pantalla de contenido de grupo"""
        if self.get_cards_count() > 0:
            self.state['current_selection'] = {'type': 'content_cards', 'index': 0}
        elif self.get_cards_count() == 0:
            self.state['current_selection'] = {'type': 'top_buttons', 'index': 0}

        self.navigation_state['enabled'] = True
        self.update_highlights()
        self.ensure_visible()
        logger.debug(f"Group content focus initialized: {self.state['current_selection']}")

    def navigate_vertical(self, event) -> None:
        direction = 1 if event.keysym == 'Down' else -1
        self._update_selection_vertical(direction)
        # Restaurar la selección por teclado
        self.last_keyboard_selection = self.state['current_selection'].copy()
        self.update_highlights()
        self.ensure_visible()

    def _update_selection_vertical(self, direction: int) -> None:
        """Actualiza la selección actual en dirección vertical"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        if direction > 0:  # Down
            if current_type == GroupContentElement.TOP_BUTTONS.value:
                if self.get_cards_count() > 0:
                    self.state['current_selection'] = {
                        'type': GroupContentElement.CONTENT_CARDS.value,
                        'index': 0
                    }
            elif current_type == GroupContentElement.CONTENT_CARDS.value:
                if current_index < self.get_cards_count() - 1:
                    self.state['current_selection']['index'] = current_index + 1
        else:  # Up
            if current_type == GroupContentElement.CONTENT_CARDS.value:
                if current_index > 0:
                    self.state['current_selection']['index'] = current_index - 1
                else:
                    self.state['current_selection'] = {
                        'type': GroupContentElement.TOP_BUTTONS.value,
                        'index': 0
                    }

    def navigate_horizontal(self, event) -> None:
        direction = 1 if event.keysym == 'Right' else -1
        self._update_selection_horizontal(direction)
        # Restaurar la selección por teclado
        self.last_keyboard_selection = self.state['current_selection'].copy()
        self.update_highlights()

    def _update_selection_horizontal(self, direction: int) -> None:
        """Actualiza la selección actual en dirección horizontal"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        if current_type == GroupContentElement.CONTENT_CARDS.value:
            if direction > 0:  # Right
                self.state['current_selection'] = {
                    'type': GroupContentElement.ICONS.value,
                    'index': current_index * 2  # Solo 2 iconos por tarjeta
                }
        elif current_type == GroupContentElement.ICONS.value:
            if direction > 0:  # Right
                if current_index % 2 == 0:  # Si estamos en el primer icono
                    self.state['current_selection']['index'] = current_index + 1
            else:  # Left
                if current_index % 2 == 1:  # Si estamos en el segundo icono
                    self.state['current_selection']['index'] = current_index - 1
                else:  # Si estamos en el primer icono
                    self.state['current_selection'] = {
                        'type': GroupContentElement.CONTENT_CARDS.value,
                        'index': current_index // 2
                    }

    def activate_selected(self, event=None) -> None:
        """Activa el elemento seleccionado actualmente"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        if current_type == GroupContentElement.TOP_BUTTONS.value:
            self._activate_top_button(current_index)
        elif current_type == GroupContentElement.CONTENT_CARDS.value:
            self._activate_card(current_index)
        elif current_type == GroupContentElement.ICONS.value:
            self._activate_icon(current_index)

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

        # Limpiar botón de cerrar
        if close_button := self._get_close_button():
            close_button._is_highlighted = False
            if not close_button._mouse_over:
                close_button.configure(bg=button_color)

        # Limpiar tarjetas y sus iconos
        for card in self._get_content_cards():
            self._reset_card_colors(card, base_color, button_color)

    def _highlight_current_selection(self) -> None:
        """Aplica el destacado al elemento actualmente seleccionado"""
        self._clear_all_highlights()

        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        # Guardar la última selección por teclado
        self.last_keyboard_selection = {
            'type': current_type,
            'index': current_index
        }

        highlight_color = self._get_highlight_color()
        icon_highlight_color = self._get_icon_highlight_color()

        if current_type == GroupContentElement.TOP_BUTTONS.value:
            # Resaltar el botón de cerrar
            if close_button := self._get_close_button():
                close_button._is_highlighted = True  # Agregar estado de highlight
                close_button.configure(bg=highlight_color)

        elif current_type == GroupContentElement.CONTENT_CARDS.value:
            cards = self._get_content_cards()
            if current_index < len(cards):
                self._highlight_card(cards[current_index], highlight_color)

        elif current_type == GroupContentElement.ICONS.value:
            cards = self._get_content_cards()
            card_index = current_index // 2
            icon_index = current_index % 2

            if card_index < len(cards):
                card = cards[card_index]
                self._highlight_card(card, highlight_color)

                icons_frame = self._find_icons_frame(card)
                if icons_frame and icon_index < len(icons_frame.winfo_children()):
                    icons = icons_frame.winfo_children()
                    for icon in icons:
                        icon.configure(bg=highlight_color)
                    icons[icon_index].configure(bg=icon_highlight_color)

    def _apply_highlight(self, selection_type, index):
        highlight_color = self._get_highlight_color()
        icon_highlight_color = self._get_icon_highlight_color()
        cards = self._get_content_cards()

        # Limpiar estado de highlight de todas las tarjetas
        for card in cards:
            for child in card.winfo_children():
                if isinstance(child, tk.Frame):
                    for btn in child.winfo_children():
                        if isinstance(btn, tk.Button):
                            btn._mouse_over = False

        if selection_type == GroupContentElement.CONTENT_CARDS.value:
            if index < len(cards):
                card = cards[index]
                self._highlight_card(card, highlight_color)

        elif selection_type == GroupContentElement.ICONS.value:
            card_index = index // 2
            icon_index = index % 2

            if card_index < len(cards):
                card = cards[card_index]
                self._highlight_card(card, highlight_color)

                icons_frame = self._find_icons_frame(card)
                if icons_frame and icon_index < len(icons_frame.winfo_children()):
                    icons = icons_frame.winfo_children()
                    for icon in icons:
                        icon.configure(bg=highlight_color)
                    icons[icon_index].configure(bg=icon_highlight_color)


    def _get_highlight_color(self) -> str:
        """Obtiene el color de resaltado según el tema actual"""
        theme_type = 'dark' if self.manager.is_dark_mode else 'light'
        return self.state['highlight_colors'][theme_type]['normal']

    def _get_icon_highlight_color(self) -> str:
        """Obtiene el color de resaltado para iconos según el tema actual"""
        theme_type = 'dark' if self.manager.is_dark_mode else 'light'
        return self.state['highlight_colors'][theme_type]['icon']

    def _get_close_button(self) -> Optional[tk.Button]:
        """Obtiene el botón de cerrar"""
        try:
            content_window = self.manager.group_manager.group_content_manager.content_window
            if content_window and content_window.winfo_exists():
                title_frame = content_window.winfo_children()[0]
                for child in title_frame.winfo_children():
                    if isinstance(child, tk.Button) and child['text'] == "❌":
                        return child
        except Exception as e:
            logger.error(f"Error getting close button: {e}")
        return None

    def _get_content_cards(self) -> List[tk.Frame]:
        """Obtiene las tarjetas de contenido del grupo"""
        if hasattr(self.manager.group_manager.group_content_manager, 'items_frame'):
            return self.manager.group_manager.group_content_manager.items_frame.winfo_children()
        return []

    def _find_icons_frame(self, card: tk.Frame) -> Optional[tk.Frame]:
        """Encuentra el frame de iconos en una tarjeta"""
        for child in card.winfo_children():
            if isinstance(child, tk.Frame) and len(child.winfo_children()) > 0:
                if all(isinstance(btn, tk.Button) for btn in child.winfo_children()):
                    return child
        return None

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
                        # Solo cambiar el color de los botones si estamos en modo tarjeta
                        if self.state['current_selection']['type'] == GroupContentElement.CONTENT_CARDS.value:
                            subchild.configure(bg=color)
            elif isinstance(child, tk.Label):
                child.configure(bg=color)
            elif isinstance(child, tk.Button):
                # Solo cambiar el color de los botones si estamos en modo tarjeta
                if self.state['current_selection']['type'] == GroupContentElement.CONTENT_CARDS.value:
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
                        if not hasattr(subchild, '_mouse_over') or not subchild._mouse_over:
                            subchild.configure(bg=button_color)
            elif isinstance(child, tk.Label):
                child.configure(bg=base_color)
            elif isinstance(child, tk.Button):
                if not hasattr(child, '_mouse_over') or not child._mouse_over:
                    child.configure(bg=button_color)

    def _activate_top_button(self, index: int) -> None:
        """Activa el botón superior (cerrar)"""
        close_button = self._get_close_button()
        if close_button:
            close_button.invoke()

    def _activate_card(self, index: int) -> None:
        """Activa una tarjeta (pegar contenido)"""
        group_items = self.manager.group_manager.groups[self.manager.group_manager.group_content_manager.current_group_id]['items']
        if index < len(group_items):
            item = group_items[index]

            # Ocultar todas las ventanas antes de pegar el contenido
            if hasattr(self.manager.group_manager.group_content_manager, 'content_window') and \
            self.manager.group_manager.group_content_manager.content_window:
                self.manager.group_manager.group_content_manager.content_window.withdraw()

            if hasattr(self.manager.group_manager, 'groups_window') and \
            self.manager.group_manager.groups_window:
                self.manager.group_manager.groups_window.withdraw()

            if hasattr(self.manager, 'root'):
                self.manager.root.withdraw()

            # Pegar el contenido
            self.manager.key_handler.paste_content(item['text'])

            # Limpiar referencias a las ventanas
            if hasattr(self.manager.group_manager.group_content_manager, 'content_window'):
                self.manager.group_manager.group_content_manager.content_window.destroy()
                self.manager.group_manager.group_content_manager.content_window = None

            if hasattr(self.manager.group_manager, 'groups_window'):
                self.manager.group_manager.groups_window.destroy()
                self.manager.group_manager.groups_window = None

            # Restablecer la navegación a la pantalla principal
            self.manager.navigation.set_strategy('main')

    def _activate_icon(self, index: int) -> None:
        """Activa un icono"""
        group_items = self.manager.group_manager.groups[self.manager.group_manager.group_content_manager.current_group_id]['items']
        card_index = index // 2
        icon_position = index % 2

        if card_index < len(group_items):
            item = group_items[card_index]
            actions = {
                0: ('edit', lambda: self.manager.group_manager.group_content_manager.edit_group_item(
                    self.manager.group_manager.group_content_manager.current_group_id,
                    item['id']
                )),
                1: ('delete', lambda: self.manager.group_manager.group_content_manager.remove_item_from_group(
                    self.manager.group_manager.group_content_manager.current_group_id,
                    item['id'],
                    self.manager.group_manager.group_content_manager.items_frame
                ))
            }

            if action := actions.get(icon_position):
                action_name, action_func = action
                action_func()

    def get_cards_count(self) -> int:
        """Obtiene el número de tarjetas en la vista actual"""
        group_id = self.manager.group_manager.group_content_manager.current_group_id
        if group_id in self.manager.group_manager.groups:
            return len(self.manager.group_manager.groups[group_id]['items'])
        return 0

    def ensure_visible(self) -> None:
        """Asegura que el elemento seleccionado esté visible"""
        current_type = self.state['current_selection']['type']
        if current_type in [GroupContentElement.CONTENT_CARDS.value,
                          GroupContentElement.ICONS.value]:
            current_index = self.state['current_selection']['index']
            card_index = current_index // 2 if current_type == GroupContentElement.ICONS.value else current_index

            cards = self._get_content_cards()
            if card_index < len(cards):
                card = cards[card_index]
                canvas = self.manager.group_manager.group_content_manager.canvas
                if canvas:
                    bbox = canvas.bbox("all")
                    if bbox:
                        card_y = card.winfo_y()
                        canvas_height = canvas.winfo_height()
                        if card_y > 0:
                            canvas.yview_moveto(card_y / bbox[3])

    def refresh_view(self) -> None:
        """Refresca la vista de contenido del grupo"""
        if hasattr(self.manager.group_manager.group_content_manager, 'current_group_id'):
            self.manager.group_manager.group_content_manager.refresh_group_content(
                self.manager.group_manager.group_content_manager.current_group_id
            )
        self.update_highlights()
