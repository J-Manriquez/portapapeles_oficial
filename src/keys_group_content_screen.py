# keys_group_content_screen.py

from key_screen_config import ScreenKeyConfig
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class GroupContentScreenAction(Enum):
    """Enumera las acciones disponibles en la pantalla de contenido de grupo"""
    NAVIGATE_UP = "up"
    NAVIGATE_DOWN = "down"
    NAVIGATE_LEFT = "left"
    NAVIGATE_RIGHT = "right"
    ACTIVATE = "return"


class GroupContentScreenKeyConfig(ScreenKeyConfig):
    def __init__(self, key_handler, manager):
        super().__init__(key_handler)
        self.manager = manager
        self.screen_name = "group_content"
        self.actions = {}
        self.setup_keys()
        # logger.debug("GroupContentScreenKeyConfig initialized")

    def setup_keys(self) -> None:
        """Configura las teclas específicas para la pantalla de contenido de grupo"""
        self.register_action(GroupContentScreenAction.NAVIGATE_UP,
                           lambda: self.handle_navigation('up'))
        self.register_action(GroupContentScreenAction.NAVIGATE_DOWN,
                           lambda: self.handle_navigation('down'))
        self.register_action(GroupContentScreenAction.NAVIGATE_LEFT,
                           lambda: self.handle_navigation('left'))
        self.register_action(GroupContentScreenAction.NAVIGATE_RIGHT,
                           lambda: self.handle_navigation('right'))
        self.register_action(GroupContentScreenAction.ACTIVATE,
                           self.handle_activation)

         # Registrar la tecla de retroceso con manejo de errores
        try:
            back_key = self.manager.settings.get('back_key', 'backspace')
            self.register_hotkey(back_key,
                            lambda: self.manager.group_manager.group_content_manager.close_content_window(
                                self.manager.group_manager.group_content_manager.current_group_id))
        except Exception as e:
            print(f"Error registering back key: {e}")
            # Usar backspace como fallback
            self.register_hotkey('backspace',
                            lambda: self.manager.group_manager.group_content_manager.close_content_window(
                                self.manager.group_manager.group_content_manager.current_group_id))

        # logger.debug("Group content screen keys setup completed")

    def register_action(self, action: GroupContentScreenAction, callback: callable) -> None:
        """Registra una acción con su callback correspondiente"""
        self.actions[action] = callback
        if isinstance(action.value, str):
            self.register_hotkey(action.value, callback)
        # logger.debug(f"Registered action: {action.name}")

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
        # logger.debug(f"Group content screen navigation: {direction}")

    def handle_activation(self):
        """Maneja la activación del elemento seleccionado"""
        # print("GroupContentScreenKeyConfig: Handling activation")  # Debug
        self.manager.navigation.current_strategy.activate_selected()
        # logger.debug("Group content screen item activated")

    def activate(self) -> None:
        """Activa la configuración de teclas para la pantalla de contenido de grupo"""
        super().activate()
        for action, callback in self.actions.items():
            if isinstance(action.value, str):
                self.key_handler.register_screen_hotkey('group_content', action.value, callback)
        # logger.info("Group content screen key configuration activated")

    def deactivate(self) -> None:
        """Desactiva la configuración de teclas de la pantalla de contenido de grupo"""
        super().deactivate()
        for action in self.actions:
            if isinstance(action.value, str) and action.value.startswith('alt+'):
                self.key_handler.global_hotkeys.unregister_hotkey(action.value)
        # logger.info("Group content screen key configuration deactivated")
