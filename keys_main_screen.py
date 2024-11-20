# main_screen_keys.py

from key_screen_config import ScreenKeyConfig
import logging

logger = logging.getLogger(__name__)

class MainScreenKeyConfig(ScreenKeyConfig):
    def __init__(self, key_handler, manager):
        super().__init__(key_handler)
        self.manager = manager

    def setup_keys(self):
        self.register_hotkey('up', lambda: self.handle_navigation('up'))
        self.register_hotkey('down', lambda: self.handle_navigation('down'))
        self.register_hotkey('left', lambda: self.handle_navigation('left'))
        self.register_hotkey('right', lambda: self.handle_navigation('right'))
        self.register_hotkey('enter', self.handle_activation)
        logger.debug("Main screen keys setup completed")

    def handle_navigation(self, direction):
        if direction in ['up', 'down']:
            self.manager.navigation.navigate_vertical(type('Event', (), {'keysym': direction.capitalize()})())
        elif direction in ['left', 'right']:
            self.manager.navigation.navigate_horizontal(type('Event', (), {'keysym': direction.capitalize()})())
        logger.debug(f"Main screen navigation: {direction}")

    def handle_activation(self):
        self.manager.navigation.activate_selected()
        logger.debug("Main screen item activated")