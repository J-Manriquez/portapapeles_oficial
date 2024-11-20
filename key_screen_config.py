# screen_key_config.py

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class ScreenKeyConfig(ABC):
    def __init__(self, key_handler):
        self.key_handler = key_handler
        self.screen_name = self.__class__.__name__.lower().replace('keyconfig', '')
        self.hotkeys = {}

    @abstractmethod
    def setup_keys(self):
        """
        Configurar las teclas específicas para esta pantalla.
        Debe ser implementado por cada subclase.
        """
        pass

    def register_hotkey(self, key, callback):
        """
        Registrar una tecla rápida para esta pantalla.
        """
        self.hotkeys[key] = callback
        self.key_handler.register_screen_hotkey(self.screen_name, key, callback)
        logger.debug(f"Registered hotkey '{key}' for screen '{self.screen_name}'")

    def unregister_all_hotkeys(self):
        """
        Desregistrar todas las teclas rápidas de esta pantalla.
        """
        for key in self.hotkeys:
            self.key_handler.unregister_screen_hotkey(self.screen_name, key)
        self.hotkeys.clear()
        logger.debug(f"Unregistered all hotkeys for screen '{self.screen_name}'")

    def activate(self):
        """
        Activar la configuración de teclas para esta pantalla.
        """
        self.key_handler.set_current_screen(self.screen_name)
        self.setup_keys()
        logger.info(f"Activated key configuration for screen '{self.screen_name}'")

    def deactivate(self):
        """
        Desactivar la configuración de teclas para esta pantalla.
        """
        self.unregister_all_hotkeys()
        logger.info(f"Deactivated key configuration for screen '{self.screen_name}'")

    @abstractmethod
    def handle_navigation(self, direction):
        """
        Manejar la navegación en una dirección específica.
        Debe ser implementado por cada subclase.
        """
        pass

    @abstractmethod
    def handle_activation(self):
        """
        Manejar la activación del elemento seleccionado actualmente.
        Debe ser implementado por cada subclase.
        """
        pass