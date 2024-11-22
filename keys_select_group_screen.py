# keys_select_group_screen.py

from key_screen_config import ScreenKeyConfig
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SelectGroupScreenAction(Enum):
    """Enumera las acciones disponibles en la pantalla de selección de grupo"""
    NAVIGATE_UP = "up"
    NAVIGATE_DOWN = "down"
    ACTIVATE = "return"
    BACK = "escape"

class SelectGroupScreenKeyConfig(ScreenKeyConfig):
    def __init__(self, key_handler, manager):
        super().__init__(key_handler)
        self.manager = manager
        self.screen_name = "select_group"
        self.actions = {}
        self.setup_keys()
        logger.debug("SelectGroupScreenKeyConfig initialized")

    def setup_keys(self) -> None:
        """Configura las teclas específicas para la pantalla de selección de grupo"""
        self.register_action(SelectGroupScreenAction.NAVIGATE_UP, 
                           lambda: self.handle_navigation('up'))
        self.register_action(SelectGroupScreenAction.NAVIGATE_DOWN, 
                           lambda: self.handle_navigation('down'))
        self.register_action(SelectGroupScreenAction.ACTIVATE, 
                           self.handle_activation)
        self.register_action(SelectGroupScreenAction.BACK, 
                           self.handle_back)
        
        logger.debug("Select group screen keys setup completed")

    def register_action(self, action: SelectGroupScreenAction, callback: callable) -> None:
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
        
        logger.debug(f"Select group screen navigation: {direction}")

    def handle_activation(self):
        """Maneja la activación del elemento seleccionado"""
        print("SelectGroupScreenKeyConfig: Handling activation")  # Debug
        self.manager.navigation.current_strategy.activate_selected()
        logger.debug("Select group screen item activated")

    def handle_back(self):
        """Maneja el evento de retroceso"""
        if hasattr(self.manager, 'select_group_dialog'):
            self.manager.functions.close_dialog(self.manager.select_group_dialog)
        logger.debug("Handled back action")

    def activate(self) -> None:
        """Activa la configuración de teclas para la pantalla de selección de grupo"""
        super().activate()
        logger.info("Select group screen key configuration activated")

    def deactivate(self) -> None:
        """Desactiva la configuración de teclas de la pantalla de selección de grupo"""
        super().deactivate()
        logger.info("Select group screen key configuration deactivated")