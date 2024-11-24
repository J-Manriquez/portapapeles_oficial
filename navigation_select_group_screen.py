# navigation_select_group_screen.py

from enum import Enum
from typing import List, Optional, Dict
import tkinter as tk
import logging

logger = logging.getLogger(__name__)

class SelectGroupScreenElement(Enum):
    TOP_BUTTONS = "top_buttons"
    GROUP_OPTIONS = "group_options"

class SelectGroupScreenNavigation:
    def __init__(self, manager):
        self.manager = manager
        self.navigation_state = {'enabled': True}
        self.navigation_order = [
            SelectGroupScreenElement.TOP_BUTTONS,
            SelectGroupScreenElement.GROUP_OPTIONS
        ]
        self.current_element: Optional[SelectGroupScreenElement] = None
        self.current_index: int = 0
        self.state: Dict = self._initialize_state()
        logger.debug("SelectGroupScreenNavigation initialized")

    def ensure_window_focus(self) -> None:
        """Asegura que la ventana de selección de grupo mantenga el foco"""
        if hasattr(self.manager, 'select_group_dialog') and self.manager.select_group_dialog.winfo_exists():
            self.manager.select_group_dialog.focus_force()
            self.manager.select_group_dialog.grab_set()

    def _initialize_state(self) -> Dict:
        """Inicializa el estado de navegación"""
        return {
            'current_selection': {'type': 'group_options', 'index': 0},
            'highlight_colors': {
                'dark': {'normal': '#444444', 'icon': '#666666'},
                'light': {'normal': '#cccccc', 'icon': '#aaaaaa'}
            }
        }

    def initialize_focus(self) -> None:
        """Inicializa el foco en la pantalla de selección de grupo"""
        if hasattr(self.manager, 'select_group_dialog'):
            self.manager.select_group_dialog.focus_force()
            
        if self.get_options_count() > 0:
            self.state['current_selection'] = {'type': 'group_options', 'index': 0}
        elif self.get_options_count() == 0:
            self.state['current_selection'] = {'type': 'top_buttons', 'index': 0}
        
        self.navigation_state['enabled'] = True
        self.update_highlights()
        logger.debug(f"Select group focus initialized: {self.state['current_selection']}")

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
            if current_type == SelectGroupScreenElement.TOP_BUTTONS.value:
                if self.get_options_count() > 0:
                    self.state['current_selection'] = {
                        'type': SelectGroupScreenElement.GROUP_OPTIONS.value,
                        'index': 0
                    }
            elif current_type == SelectGroupScreenElement.GROUP_OPTIONS.value:
                if current_index < self.get_options_count() - 1:
                    self.state['current_selection']['index'] = current_index + 1
        else:  # Up
            if current_type == SelectGroupScreenElement.GROUP_OPTIONS.value:
                if current_index > 0:
                    self.state['current_selection']['index'] = current_index - 1
                else:
                    self.state['current_selection'] = {
                        'type': SelectGroupScreenElement.TOP_BUTTONS.value,
                        'index': 0
                    }

    def navigate_horizontal(self, event) -> None:
        """Gestiona la navegación horizontal"""
        # En la pantalla de selección de grupo no hay navegación horizontal
        # ya que solo hay un botón superior (cerrar) y opciones verticales
        pass

    def activate_selected(self, event=None) -> None:
        """Activa el elemento seleccionado actualmente"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']

        if current_type == SelectGroupScreenElement.TOP_BUTTONS.value:
            self._activate_top_button(current_index)
        elif current_type == SelectGroupScreenElement.GROUP_OPTIONS.value:
            self._activate_group_option(current_index)

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
        base_color = theme['button_bg']

        # Limpiar botón superior (cerrar)
        if hasattr(self.manager, 'select_group_dialog'):
            close_button = self._get_close_button()
            if close_button:
                close_button.configure(bg=base_color)

        # Limpiar opciones de grupos
        for option in self._get_group_options():
            option.configure(bg=base_color)

    def _highlight_current_selection(self) -> None:
        """Aplica el destacado al elemento actualmente seleccionado"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        highlight_color = self._get_highlight_color()

        if current_type == SelectGroupScreenElement.TOP_BUTTONS.value:
            close_button = self._get_close_button()
            if close_button:
                close_button.configure(bg=highlight_color)
        elif current_type == SelectGroupScreenElement.GROUP_OPTIONS.value:
            options = self._get_group_options()
            if 0 <= current_index < len(options):
                options[current_index].configure(bg=highlight_color)

    def _activate_top_button(self, index: int) -> None:
        """Activa el botón superior (cerrar)"""
        if hasattr(self.manager, 'select_group_dialog'):
            close_button = self._get_close_button()
            if close_button:
                close_button.invoke()

    def _activate_group_option(self, index: int) -> None:
        """Activa una opción de grupo"""
        options = self._get_group_options()
        if 0 <= index < len(options):
            options[index].invoke()

    def ensure_visible(self) -> None:
        """Asegura que el elemento seleccionado esté visible"""
        if not hasattr(self.manager, 'select_group_dialog'):
            return

        current_type = self.state['current_selection']['type']
        if current_type == SelectGroupScreenElement.GROUP_OPTIONS.value:
            current_index = self.state['current_selection']['index']
            options = self._get_group_options()
            
            if 0 <= current_index < len(options):
                option = options[current_index]
                canvas = self._get_canvas()
                if canvas:
                    bbox = canvas.bbox("all")
                    if bbox:
                        option_y = option.winfo_y()
                        canvas_height = canvas.winfo_height()
                        if option_y > 0:
                            canvas.yview_moveto(option_y / bbox[3])

    def _get_close_button(self) -> Optional[tk.Button]:
        """Obtiene el botón de cerrar"""
        if hasattr(self.manager, 'select_group_dialog'):
            for child in self.manager.select_group_dialog.winfo_children():
                if isinstance(child, tk.Frame):
                    for button in child.winfo_children():
                        if isinstance(button, tk.Button) and button['text'] == "❌":
                            return button
        return None

    def _get_group_options(self) -> List[tk.Button]:
        """Obtiene la lista de botones de opciones de grupos"""
        options = []
        if hasattr(self.manager, 'select_group_dialog'):
            for child in self.manager.select_group_dialog.winfo_children():
                if isinstance(child, tk.Canvas):
                    content_frame = child.winfo_children()[0]
                    for button in content_frame.winfo_children():
                        if isinstance(button, tk.Button):
                            options.append(button)
        return options

    def _get_canvas(self) -> Optional[tk.Canvas]:
        """Obtiene el canvas del diálogo"""
        if hasattr(self.manager, 'select_group_dialog'):
            for child in self.manager.select_group_dialog.winfo_children():
                if isinstance(child, tk.Canvas):
                    return child
        return None

    def get_options_count(self) -> int:
        """Obtiene el número de opciones de grupos"""
        return len(self._get_group_options())

    def _get_highlight_color(self) -> str:
        """Obtiene el color de resaltado según el tema actual"""
        theme_type = 'dark' if self.manager.is_dark_mode else 'light'
        return self.state['highlight_colors'][theme_type]['normal']

    def refresh_view(self) -> None:
        """Refresca la vista de selección de grupo"""
        self.update_highlights()