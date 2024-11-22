# keys_groups_screen.py

from key_screen_config import ScreenKeyConfig
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class GroupScreenAction(Enum):
    """Enumera las acciones disponibles en la pantalla de grupos"""
    NAVIGATE_UP = "up"
    NAVIGATE_DOWN = "down"
    NAVIGATE_LEFT = "left"
    NAVIGATE_RIGHT = "right"
    ACTIVATE = "return"
    ADD_GROUP = "alt+n"
    BACK_TO_MAIN = "escape"

class GroupsScreenKeyConfig(ScreenKeyConfig):
    def __init__(self, key_handler, manager):
        super().__init__(key_handler)
        self.manager = manager
        self.screen_name = "groups"
        self.actions = {}
        self.setup_keys()
        logger.debug("GroupsScreenKeyConfig initialized")

    def setup_keys(self) -> None:
        """Configura las teclas específicas para la pantalla de grupos"""
        self.register_action(GroupScreenAction.NAVIGATE_UP, 
                           lambda: self.handle_navigation('up'))
        self.register_action(GroupScreenAction.NAVIGATE_DOWN, 
                           lambda: self.handle_navigation('down'))
        self.register_action(GroupScreenAction.NAVIGATE_LEFT, 
                           lambda: self.handle_navigation('left'))
        self.register_action(GroupScreenAction.NAVIGATE_RIGHT, 
                           lambda: self.handle_navigation('right'))
        self.register_action(GroupScreenAction.ACTIVATE, 
                           self.handle_activation)
        
        # Atajos adicionales específicos de la pantalla de grupos
        self.register_action(GroupScreenAction.ADD_GROUP, 
                           self.manager.group_manager.add_group)
        self.register_action(GroupScreenAction.BACK_TO_MAIN, 
                           self.manager.show_main_screen)
        
        logger.debug("Groups screen keys setup completed")

    def register_action(self, action: GroupScreenAction, callback: callable) -> None:
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
        logger.debug(f"Groups screen navigation: {direction}")

    def handle_activation(self):
        """Maneja la activación del elemento seleccionado"""
        print("GroupsScreenKeyConfig: Handling activation")  # Debug
        self.manager.navigation.current_strategy.activate_selected()
        logger.debug("Groups screen item activated")

    def activate(self) -> None:
        """Activa la configuración de teclas para la pantalla de grupos"""
        super().activate()
        for action, callback in self.actions.items():
            if isinstance(action.value, str) and action.value.startswith('alt+'):
                self.key_handler.global_hotkeys.register_hotkey(action.value, callback)
        logger.info("Groups screen key configuration activated")

    def deactivate(self) -> None:
        """Desactiva la configuración de teclas de la pantalla de grupos"""
        super().deactivate()
        for action in self.actions:
            if isinstance(action.value, str) and action.value.startswith('alt+'):
                self.key_handler.global_hotkeys.unregister_hotkey(action.value)
        logger.info("Groups screen key configuration deactivated")