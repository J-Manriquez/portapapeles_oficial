
import logging
from typing import Dict, Optional, Any
from enum import Enum, auto
from navigation_main_screen import MainScreenNavigation
from navigation_groups_screen import GroupsScreenNavigation
from navigation_select_group_screen import SelectGroupScreenNavigation

logger = logging.getLogger(__name__)

class ScreenType(Enum):
    MAIN = auto()
    GROUPS = auto()
    SETTINGS = auto()
    SELECT_GROUP = auto()

class Navigation:
    def __init__(self, manager):
        self.manager = manager
        self.strategies = {}
        self._initialize_strategies()
        self.current_strategy = None
        self.navigation_state = {'enabled': True}
        
        self.strategies: Dict[ScreenType, Any] = {
            ScreenType.MAIN: MainScreenNavigation(manager),
            ScreenType.GROUPS: GroupsScreenNavigation(manager),
            ScreenType.SELECT_GROUP: SelectGroupScreenNavigation(manager)
        }
        self.current_strategy = self.strategies[ScreenType.MAIN]
        self.current_screen = ScreenType.MAIN
        logger.debug("Navigation initialized")
        
    def _initialize_strategies(self):
        """Inicializa las estrategias de navegación con manejo de errores"""
        try:
            self.strategies = {
                ScreenType.MAIN: MainScreenNavigation(self.manager),
                ScreenType.GROUPS: GroupsScreenNavigation(self.manager),
                ScreenType.SELECT_GROUP: SelectGroupScreenNavigation(self.manager) 
            }
            self.set_strategy('main')
        except Exception as e:
            logger.error(f"Error initializing navigation strategies: {e}")
            raise

    def set_strategy(self, screen_type: str) -> None:
        """Cambia la estrategia de navegación con verificaciones"""
        try:
            screen_mapping = {
                'main': ScreenType.MAIN,
                'groups': ScreenType.GROUPS,
                'select_group': ScreenType.SELECT_GROUP,
                'settings': ScreenType.SETTINGS,
            }
            
            if screen_type not in screen_mapping:
                raise ValueError(f"Invalid screen type: {screen_type}")
            
            if screen_type == 'select_group':
                self.manager.root.after(100, lambda: self.current_strategy.ensure_window_focus())

            screen_enum = screen_mapping[screen_type]
            if screen_enum in self.strategies:
                self.current_screen = screen_enum
                self.current_strategy = self.strategies[screen_enum]
                self._configure_screen_navigation(screen_enum)
                logger.debug(f"Navigation strategy set to: {screen_type}")
            else:
                raise ValueError(f"No strategy found for screen: {screen_type}")
        except Exception as e:
            logger.error(f"Error setting navigation strategy: {e}")
            self._fallback_to_main_strategy()
    
    def _fallback_to_main_strategy(self):
        """Sistema de recuperación para casos de error"""
        try:
            logger.warning("Falling back to main navigation strategy")
            self.current_strategy = self.strategies['main']
            self.manager.show_main_screen()
        except Exception as e:
            logger.critical(f"Critical error in navigation fallback: {e}")

    def _configure_screen_navigation(self, screen_type: ScreenType) -> None:
        """Configura la navegación específica para cada pantalla"""
        if screen_type == ScreenType.MAIN:
            self.manager.main_screen_keys.activate()
            if hasattr(self.manager, 'groups_screen_keys'):
                self.manager.groups_screen_keys.deactivate()
        elif screen_type == ScreenType.GROUPS:
            self.manager.main_screen_keys.deactivate()
            if hasattr(self.manager, 'groups_screen_keys'):
                self.manager.groups_screen_keys.activate()
        elif screen_type == ScreenType.SELECT_GROUP:
            self.manager.main_screen_keys.deactivate()
            if hasattr(self.manager, 'groups_screen_keys'):
                self.manager.groups_screen_keys.deactivate()
            if hasattr(self.manager, 'select_group_screen_keys'):
                self.manager.select_group_screen_keys.activate()

    def handle_keyboard_event(self, event):
        """Maneja los eventos de teclado"""
        print(f"Navigation received keyboard event: {event.keysym}")  # Debug
        try:
            if not self.navigation_state['enabled']:
                return
                
            key = event.keysym.lower()
            print(f"Processing key: {key}")  # Debug
            
            # Manejar Enter explícitamente
            if key == 'return':
                print("Enter key detected, activating selection")  # Debug
                self.current_strategy.activate_selected()  # Llamar directamente a la estrategia actual
                return
                
            # Resto de la navegación
            if key in ['up', 'down']:
                self.navigate_vertical(event)
            elif key in ['left', 'right']:
                self.navigate_horizontal(event)
                
        except Exception as e:
            logger.error(f"Error handling keyboard event: {e}")
            
    def handle_escape(self) -> None:
        """Maneja la tecla Escape según el contexto"""
        if self.current_screen != ScreenType.MAIN:
            self.manager.show_main_screen()
        else:
            self.manager.key_handler.hide_window()

    def navigate_vertical(self, event) -> None:
        """Gestiona la navegación vertical"""
        logger.debug(f"Vertical navigation: {event.keysym}")
        self.current_strategy.navigate_vertical(event)
        self.update_highlights()
        self.ensure_visible()

    def navigate_horizontal(self, event) -> None:
        """Gestiona la navegación horizontal"""
        logger.debug(f"Horizontal navigation: {event.keysym}")
        self.current_strategy.navigate_horizontal(event)
        self.update_highlights()

    def activate_selected(self, event=None) -> None:
        """Activa el elemento seleccionado actualmente"""
        logger.debug("Activating selected item")
        self.current_strategy.activate_selected(event)

    def update_highlights(self) -> None:
        """Actualiza los destacados visuales"""
        logger.debug("Updating highlights")
        self.current_strategy.update_highlights()

    def initialize_focus(self) -> None:
        """Inicializa el foco en la pantalla actual"""
        logger.debug("Initializing focus")
        self.current_strategy.initialize_focus()

    def ensure_visible(self) -> None:
        """Asegura que el elemento seleccionado esté visible"""
        self.current_strategy.ensure_visible()
        logger.debug("Ensuring selected item visibility")

    def refresh_navigation(self) -> None:
        """Refresca el estado de navegación actual"""
        logger.debug("Refreshing navigation")
        self.initialize_focus()
        self.update_highlights()
        if hasattr(self.current_strategy, 'refresh_view'):
            self.current_strategy.refresh_view()

    def get_current_selection(self) -> dict:
        """Obtiene la selección actual"""
        return self.manager.current_selection

    def set_current_selection(self, selection_type: str, index: int) -> None:
        """Establece la selección actual"""
        self.manager.current_selection = {'type': selection_type, 'index': index}
        self.update_highlights()
        logger.debug(f"Current selection set to: {self.manager.current_selection}")

    def get_cards_count(self) -> int:
        """Obtiene el número de tarjetas en la vista actual"""
        return self.current_strategy.get_cards_count()

    def on_window_focus(self, event) -> None:
        """Maneja el evento de obtención de foco de la ventana"""
        logger.debug("Window gained focus")
        self.refresh_navigation()

    def on_window_unfocus(self, event) -> None:
        """Maneja el evento de pérdida de foco de la ventana"""
        logger.debug("Window lost focus")
        # Implementar lógica adicional si es necesario
        
    def check_window_state(self) -> None:
        """Verifica y corrige el estado de visibilidad de la ventana"""
        try:
            actual_visible = self.manager.root.winfo_viewable()
            if actual_visible != self.manager.is_visible:
                logger.info(f"Correcting visibility state: {self.manager.is_visible} -> {actual_visible}")
                self.manager.is_visible = actual_visible
        except Exception as e:
            logger.error(f"Error checking window state: {e}")
        
        # Programar la próxima verificación
        self.manager.root.after(1000, self.check_window_state)
        
    