from enum import Enum
import logging
from typing import Optional, Callable, Dict
from key_screen_config import ScreenKeyConfig

logger = logging.getLogger(__name__)

class MainScreenAction(Enum):
    """Enumera las acciones disponibles en la pantalla principal"""
    NAVIGATE_UP = "up"
    NAVIGATE_DOWN = "down"
    NAVIGATE_LEFT = "left"
    NAVIGATE_RIGHT = "right"
    ACTIVATE = "return"
    TOGGLE_FORMAT = "alt+f"
    SHOW_GROUPS = "alt+g"
    CLEAR_HISTORY = "alt+c"

class MainScreenKeyConfig(ScreenKeyConfig):
    def __init__(self, key_handler, manager):
        super().__init__(key_handler)
        self.manager = manager
        self.screen_name = "main"
        self.actions: Dict[MainScreenAction, Callable] = {}
        self.setup_keys()
        logger.debug("MainScreenKeyConfig initialized")

    def setup_keys(self) -> None:
        """Configura las teclas específicas para la pantalla principal"""
        self.register_action(MainScreenAction.NAVIGATE_UP, 
                           lambda: self.handle_navigation('up'))
        self.register_action(MainScreenAction.NAVIGATE_DOWN, 
                           lambda: self.handle_navigation('down'))
        self.register_action(MainScreenAction.NAVIGATE_LEFT, 
                           lambda: self.handle_navigation('left'))
        self.register_action(MainScreenAction.NAVIGATE_RIGHT, 
                           lambda: self.handle_navigation('right'))
        self.register_action(MainScreenAction.ACTIVATE, 
                           self.handle_activation)

        
        # Atajos adicionales específicos de la pantalla principal
        self.register_action(MainScreenAction.TOGGLE_FORMAT, 
                           self.manager.functions.toggle_paste_format)
        self.register_action(MainScreenAction.SHOW_GROUPS, 
                           self.manager.show_groups)
        self.register_action(MainScreenAction.CLEAR_HISTORY, 
                           self.manager.functions.clear_history)
        
        logger.debug("Main screen keys setup completed")

    def register_action(self, action: MainScreenAction, callback: Callable) -> None:
        """Registra una acción con su callback correspondiente"""
        self.actions[action] = callback
        if isinstance(action.value, str):
            self.register_hotkey(action.value, callback)
        logger.debug(f"Registered action: {action.name}")

    def handle_navigation(self, direction: str) -> None:
        """Maneja los eventos de navegación"""
        event = type('Event', (), {'keysym': direction.capitalize()})()
        
        # Actualizar el estado de selección en el manager
        current_selection = self.manager.navigation.current_strategy.state['current_selection']
        self.manager.current_selection = current_selection
        
        if direction in ['up', 'down']:
            self.manager.navigation.navigate_vertical(event)
        else:
            self.manager.navigation.navigate_horizontal(event)
        logger.debug(f"Main screen navigation: {direction}")
        
    def handle_activation(self):
        """Maneja la activación del elemento seleccionado"""
        print("MainScreenKeyConfig: Handling activation")  # Debug
        self.manager.navigation.current_strategy.activate_selected()
        logger.debug("Main screen item activated")

    def activate(self) -> None:
        """Activa la configuración de teclas para la pantalla principal"""
        super().activate()
        for action, callback in self.actions.items():
            if isinstance(action.value, str) and action.value.startswith('alt+'):
                self.key_handler.global_hotkeys.register_hotkey(action.value, callback)
        logger.info("Main screen key configuration activated")

    def deactivate(self) -> None:
        """Desactiva la configuración de teclas de la pantalla principal"""
        super().deactivate()
        for action in self.actions:
            if isinstance(action.value, str) and action.value.startswith('alt+'):
                self.key_handler.global_hotkeys.unregister_hotkey(action.value)
        logger.info("Main screen key configuration deactivated")
# navigation_main_screen.py

from enum import Enum
from typing import List, Optional, Dict
import tkinter as tk
import logging

logger = logging.getLogger(__name__)

class MainScreenElement(Enum):
    TOP_BUTTONS = "top_buttons"
    MAIN_BUTTONS = "main_buttons"
    CARDS = "cards"
    ICONS = "icons"

class MainScreenNavigation:
    def __init__(self, manager):
        self.manager = manager
        self.navigation_state = {'enabled': True}
        self.navigation_order = [
            MainScreenElement.TOP_BUTTONS,
            MainScreenElement.MAIN_BUTTONS,
            MainScreenElement.CARDS
        ]
        self.current_element: Optional[MainScreenElement] = None
        self.current_index: int = 0
        self.state: Dict = self._initialize_state()
        logger.debug("MainScreenNavigation initialized")

    def _initialize_state(self) -> Dict:
        """Inicializa el estado de navegación"""
        return {
            'current_selection': {'type': 'main_buttons', 'index': 0},
            'highlight_colors': {
                'dark': {'normal': '#444444', 'icon': '#666666'},
                'light': {'normal': '#cccccc', 'icon': '#aaaaaa'}
            }
        }
        
    def initialize_focus(self):
        """Inicializa el foco en la pantalla principal"""
        if self.get_cards_count() > 0:
            self.state['current_selection'] = {'type': 'cards', 'index': 0}
        else:
            self.state['current_selection'] = {'type': 'main_buttons', 'index': 0}
        
        self.navigation_state['enabled'] = True 
        
        # Asegurar que la ventana principal tenga el foco
        self.manager.root.focus_force()
        
        # Actualizar los highlights después de inicializar el foco
        self.update_highlights()
        
        logger.debug(f"Main screen focus initialized: {self.state['current_selection']}")

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
        
        print(f"Before navigation: type={current_type}, index={current_index}")  # Debug

        if direction > 0:  # Down
            if current_type == MainScreenElement.TOP_BUTTONS.value:
                self.state['current_selection'] = {
                    'type': MainScreenElement.MAIN_BUTTONS.value,
                    'index': 0
                }
            elif current_type == MainScreenElement.MAIN_BUTTONS.value:
                if self.get_cards_count() > 0:
                    self.state['current_selection'] = {
                        'type': MainScreenElement.CARDS.value,
                        'index': 0
                    }
            elif current_type == MainScreenElement.CARDS.value:
                if current_index < self.get_cards_count() - 1:
                    self.state['current_selection']['index'] = current_index + 1
        else:  # Up
            if current_type == MainScreenElement.CARDS.value:
                if current_index > 0:
                    self.state['current_selection']['index'] = current_index - 1
                else:
                    self.state['current_selection'] = {
                        'type': MainScreenElement.MAIN_BUTTONS.value,
                        'index': 0
                    }
            elif current_type == MainScreenElement.MAIN_BUTTONS.value:
                self.state['current_selection'] = {
                    'type': MainScreenElement.TOP_BUTTONS.value,
                    'index': 0
                }
        
        print(f"After navigation: type={self.state['current_selection']['type']}, index={self.state['current_selection']['index']}")  # Debug
        
        # Actualizar visualización
        self.update_highlights()
        self.ensure_visible()
    
    def navigate_horizontal(self, event) -> None:
        """Gestiona la navegación horizontal"""
        print(f"MainScreenNavigation: Navigating horizontally {event.keysym}")  # Debug
        direction = 1 if event.keysym == 'Right' else -1
        self._update_selection_horizontal(direction)
        self.update_highlights()
        logger.debug(f"Horizontal navigation: {event.keysym}")

    def get_button_count(self, button_type: str) -> int:
        """Obtiene el número de botones según el tipo"""
        if button_type == MainScreenElement.TOP_BUTTONS.value:
            return 3  # theme_button, clear_button, close_button
        elif button_type == MainScreenElement.MAIN_BUTTONS.value:
            return 3  # button1, button2, button3
        return 0

    def _update_selection_horizontal(self, direction: int) -> None:
        """Actualiza la selección actual en dirección horizontal"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        
        print(f"Horizontal navigation - Before: type={current_type}, index={current_index}")  # Debug

        if direction > 0:  # Right
            if current_type in [MainScreenElement.TOP_BUTTONS.value, 
                            MainScreenElement.MAIN_BUTTONS.value]:
                button_count = self.get_button_count(current_type)
                self.state['current_selection']['index'] = (current_index + 1) % button_count
            elif current_type == MainScreenElement.CARDS.value:
                self.state['current_selection'] = {
                    'type': MainScreenElement.ICONS.value,
                    'index': current_index * 3
                }
            elif current_type == MainScreenElement.ICONS.value:
                if current_index % 3 < 2:  # Si no es el último icono
                    self.state['current_selection']['index'] = current_index + 1
        else:  # Left
            if current_type in [MainScreenElement.TOP_BUTTONS.value, 
                            MainScreenElement.MAIN_BUTTONS.value]:
                button_count = self.get_button_count(current_type)
                self.state['current_selection']['index'] = (current_index - 1) % button_count
            elif current_type == MainScreenElement.ICONS.value:
                if current_index % 3 > 0:  # Si no es el primer icono
                    self.state['current_selection']['index'] = current_index - 1
                else:
                    self.state['current_selection'] = {
                        'type': MainScreenElement.CARDS.value,
                        'index': current_index // 3
                    }
        
        print(f"Horizontal navigation - After: type={self.state['current_selection']['type']}, index={self.state['current_selection']['index']}")  # Debug
        
        # Actualizar visualización
        self.update_highlights()

    def activate_selected(self, event=None):
        """Activa el elemento seleccionado actualmente"""
        print(f"MainScreenNavigation: Attempting to activate selection")  # Debug
        print(f"Current selection state: {self.state['current_selection']}")  # Debug
        
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        
        print(f"Activating: {current_type} at index {current_index}")  # Debug

        # Mapeo de tipos a funciones de activación
        actions = {
            'main_buttons': self._activate_main_button,
            'top_buttons': self._activate_top_button,
            'cards': self._activate_card,
            'icons': self._activate_icon
        }

        if handler := actions.get(current_type):
            print(f"Executing handler for {current_type}")  # Debug
            handler(current_index)
        else:
            print(f"No handler found for type: {current_type}")  # Debug
            
    def update_highlights(self) -> None:
        """Actualiza los destacados visuales"""
        print("Updating highlights")  # Debug
        self._clear_all_highlights()
        
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        highlight_color = self._get_highlight_color()
        icon_highlight_color = self._get_icon_highlight_color()
        
        if current_type == MainScreenElement.MAIN_BUTTONS.value:
            buttons = [self.manager.button1, self.manager.button2, self.manager.button3]
            if 0 <= current_index < len(buttons):
                buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == MainScreenElement.TOP_BUTTONS.value:
            buttons = [self.manager.theme_button, self.manager.clear_button, self.manager.close_button]
            if 0 <= current_index < len(buttons):
                buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == MainScreenElement.CARDS.value:
            cards = self.manager.cards_frame.winfo_children()
            if current_index < len(cards):
                self._highlight_card(cards[current_index], highlight_color)
        
        elif current_type == MainScreenElement.ICONS.value:
            card_index = current_index // 3
            icon_position = current_index % 3
            cards = self.manager.cards_frame.winfo_children()
            
            if card_index < len(cards):
                card = cards[card_index]
                icons_frame = self._find_icons_frame(card)
                
                if icons_frame and icon_position < len(icons_frame.winfo_children()):
                    self._highlight_card(card, highlight_color)
                    icons = icons_frame.winfo_children()
                    if 0 <= icon_position < len(icons):
                        icons[icon_position].configure(bg=icon_highlight_color)
        
        self.manager.root.update_idletasks()
        self.manager.root.after(10, self.manager.root.update)

    def handle_specific_keys(self, event) -> None:
        """Maneja teclas específicas de la pantalla principal"""
        key_handlers = {
            'f5': self.refresh_view,
            'escape': self.manager.key_handler.hide_window
        }
        
        handler = key_handlers.get(event.keysym.lower())
        if handler:
            handler()
            
    def _move_up(self, current_type: str, current_index: int) -> None:
        """Maneja el movimiento hacia arriba"""
        if current_type in [MainScreenElement.CARDS.value, MainScreenElement.ICONS.value]:
            if current_index > 0:
                self.state['current_selection']['index'] = current_index - 1
            else:
                self.state['current_selection'] = {
                    'type': MainScreenElement.MAIN_BUTTONS.value, 
                    'index': 0
                }
        elif current_type == MainScreenElement.MAIN_BUTTONS.value:
            self.state['current_selection'] = {
                'type': MainScreenElement.TOP_BUTTONS.value, 
                'index': 0
            }
        logger.debug(f"Moved up to {self.state['current_selection']}")

    def _move_down(self, current_type: str, current_index: int) -> None:
        """Maneja el movimiento hacia abajo"""
        if current_type == MainScreenElement.TOP_BUTTONS.value:
            self.state['current_selection'] = {
                'type': MainScreenElement.MAIN_BUTTONS.value, 
                'index': 0
            }
        elif current_type == MainScreenElement.MAIN_BUTTONS.value:
            if self.get_cards_count() > 0:
                self.state['current_selection'] = {
                    'type': MainScreenElement.CARDS.value, 
                    'index': 0
                }
        elif current_type == MainScreenElement.CARDS.value:
            if current_index < self.get_cards_count() - 1:
                self.state['current_selection']['index'] = current_index + 1
        logger.debug(f"Moved down to {self.state['current_selection']}")

    def _move_left(self, current_type: str, current_index: int) -> None:
        """Maneja el movimiento hacia la izquierda"""
        if current_type in [MainScreenElement.TOP_BUTTONS.value, 
                        MainScreenElement.MAIN_BUTTONS.value]:
            button_count = self.get_button_count(current_type)
            self.state['current_selection']['index'] = (current_index - 1) % button_count
        elif current_type == MainScreenElement.ICONS.value:
            if current_index % 3 > 0:
                self.state['current_selection']['index'] = current_index - 1
            else:
                self.state['current_selection'] = {
                    'type': MainScreenElement.CARDS.value,
                    'index': current_index // 3
                }
        logger.debug(f"Moved left to {self.state['current_selection']}")

    def _move_right(self, current_type: str, current_index: int) -> None:
        """Maneja el movimiento hacia la derecha"""
        if current_type in [MainScreenElement.TOP_BUTTONS.value, 
                        MainScreenElement.MAIN_BUTTONS.value]:
            button_count = self.get_button_count(current_type)
            self.state['current_selection']['index'] = (current_index + 1) % button_count
        elif current_type == MainScreenElement.CARDS.value:
            self.state['current_selection'] = {
                'type': MainScreenElement.ICONS.value,
                'index': current_index * 3
            }
        elif current_type == MainScreenElement.ICONS.value:
            if current_index % 3 < 2:
                self.state['current_selection']['index'] = current_index + 1
        logger.debug(f"Moved right to {self.state['current_selection']}")

    def _activate_main_button(self, index: int) -> None:
        """Activa un botón principal"""
        actions = {
            0: ('groups', self.manager.show_groups),
            1: ('format', self.manager.functions.toggle_paste_format),
            2: ('clear', self.manager.functions.clear_history)
        }
        if action := actions.get(index):
            action_name, action_func = action
            action_func()
            logger.debug(f"Activated main button '{action_name}' at index {index}")
    
    def _activate_top_button(self, index: int) -> None:
        """Activa un botón superior"""
        actions = {
            0: ('theme', self.manager.theme_manager.toggle_theme),
            1: ('settings', self.manager.show_settings),
            2: ('exit', self.manager.functions.exit_app)
        }
        if action := actions.get(index):
            action_name, action_func = action
            action_func()
            logger.debug(f"Activated top button '{action_name}' at index {index}")
            
    def _activate_card(self, index: int) -> None:
        """Activa una tarjeta (pegar contenido)"""
        items = list(self.manager.clipboard_items.items())
        if index < len(items):
            item_id, item_data = items[index]
            clipboard_data = item_data['text']
            self.manager.key_handler.paste_content(clipboard_data)
            logger.debug(f"Activated card at index {index}")

    def _activate_icon(self, index):
        """Activa un icono de tarjeta"""
        print(f"Activating icon at index {index}")  # Debug
        items = list(self.manager.clipboard_items.keys())
        card_index = index // 3
        icon_position = index % 3
        
        print(f"Card index: {card_index}, Icon position: {icon_position}")  # Debug
        
        if card_index < len(items):
            item_id = items[card_index]
            actions = {
                0: ('arrow', lambda: self.manager.functions.on_arrow_click(item_id)),
                1: ('pin', lambda: self.manager.functions.toggle_pin(item_id)),
                2: ('delete', lambda: self.manager.functions.delete_item(item_id))
            }
            
            if action := actions.get(icon_position):
                action_name, action_func = action
                print(f"Executing {action_name} action for icon")  # Debug
                action_func()
            else:
                print(f"No action found for icon position {icon_position}")  # Debug
                    
    def get_cards_count(self) -> int:
        """Obtiene el número de tarjetas en la pantalla principal"""
        return len(self.manager.cards_frame.winfo_children())
    
    
    def _get_highlight_color(self) -> str:
        """Obtiene el color de resaltado según el tema actual"""
        theme_type = 'dark' if self.manager.is_dark_mode else 'light'
        return self.state['highlight_colors'][theme_type]['normal']

    def _get_icon_highlight_color(self) -> str:
        """Obtiene el color de resaltado para iconos según el tema actual"""
        theme_type = 'dark' if self.manager.is_dark_mode else 'light'
        return self.state['highlight_colors'][theme_type]['icon']

    def _highlight_current_selection(self) -> None:
        """Aplica el destacado al elemento actualmente seleccionado"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        highlight_color = self._get_highlight_color()
        icon_highlight_color = self._get_icon_highlight_color()

        if current_type == MainScreenElement.MAIN_BUTTONS.value:
            buttons = [
                self.manager.button1,
                self.manager.button2,
                self.manager.button3
            ]
            if 0 <= current_index < len(buttons):
                buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == MainScreenElement.TOP_BUTTONS.value:
            buttons = [
                self.manager.theme_button,
                self.manager.clear_button,
                self.manager.close_button
            ]
            if 0 <= current_index < len(buttons):
                buttons[current_index].configure(bg=highlight_color)
        
        elif current_type == MainScreenElement.CARDS.value:
            cards = self.manager.cards_frame.winfo_children()
            if current_index < len(cards):
                self._highlight_card(cards[current_index], highlight_color)
        
        elif current_type == MainScreenElement.ICONS.value:
            cards = self.manager.cards_frame.winfo_children()
            card_index = current_index // 3
            icon_index = current_index % 3
            
            if card_index < len(cards):
                card = cards[card_index]
                # Resaltar la tarjeta completa
                self._highlight_card(card, highlight_color)
                
                # Resaltar el icono específico
                icons_frame = self._find_icons_frame(card)
                if icons_frame and icon_index < len(icons_frame.winfo_children()):
                    # Resetear el color de todos los iconos primero
                    for icon in icons_frame.winfo_children():
                        icon.configure(bg=highlight_color)
                    # Resaltar el icono seleccionado
                    icons_frame.winfo_children()[icon_index].configure(bg=icon_highlight_color)

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
                        if self.state['current_selection']['type'] == MainScreenElement.CARDS.value:
                            subchild.configure(bg=color)
            elif isinstance(child, tk.Label):
                child.configure(bg=color)
            elif isinstance(child, tk.Button):
                if self.state['current_selection']['type'] == MainScreenElement.CARDS.value:
                    child.configure(bg=color)

    def _find_icons_frame(self, card: tk.Frame) -> Optional[tk.Frame]:
        """Encuentra el frame que contiene los iconos en una tarjeta"""
        for child in card.winfo_children():
            if isinstance(child, tk.Frame) and len(child.winfo_children()) > 0:
                if all(isinstance(btn, tk.Button) for btn in child.winfo_children()):
                    return child
        return None

    def _clear_all_highlights(self) -> None:
        """Limpia todos los destacados visuales"""
        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        base_color = theme['card_bg']
        button_color = theme['button_bg']
        
        # Limpiar botones superiores
        top_buttons = [
            self.manager.theme_button,
            self.manager.clear_button,
            self.manager.close_button
        ]
        for button in top_buttons:
            button.configure(bg=button_color)
        
        # Limpiar botones principales
        main_buttons = [
            self.manager.button1,
            self.manager.button2,
            self.manager.button3
        ]
        for button in main_buttons:
            button.configure(bg=button_color)
        
        # Limpiar tarjetas y sus iconos
        for card in self.manager.cards_frame.winfo_children():
            self._reset_card_colors(card, base_color, button_color)

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

    def update_highlights(self) -> None:
        """Actualiza los destacados visuales"""
        print("Updating highlights")  # Debug
        self._clear_all_highlights()
        self._highlight_current_selection()
        
        # Forzar la actualización visual
        self.manager.root.update_idletasks()
    
    def ensure_visible(self) -> None:
        """Asegura que el elemento seleccionado esté visible"""
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        
        if current_type == 'cards':
            cards = self.manager.cards_frame.winfo_children()
            if current_index < len(cards):
                card = cards[current_index]
                bbox = self.manager.canvas.bbox("all")
                if bbox:
                    card_y = card.winfo_y()
                    canvas_height = self.manager.canvas.winfo_height()
                    if card_y > 0:
                        self.manager.canvas.yview_moveto(card_y / bbox[3])
    
    def _handle_activation(self):
        """Maneja específicamente la activación por Enter"""
        print("Handling Enter activation")  # Debug
        current_type = self.state['current_selection']['type']
        current_index = self.state['current_selection']['index']
        
        print(f"Activating: type={current_type}, index={current_index}")  # Debug
        
        activation_map = {
            'main_buttons': self._activate_main_button,
            'top_buttons': self._activate_top_button,
            'cards': self._activate_card,
            'icons': self._activate_icon
        }
        
        if handler := activation_map.get(current_type):
            handler(current_index)
            print(f"Activation handler executed for {current_type}")  # Debug
        else:
            print(f"No activation handler found for {current_type}")  # Debug