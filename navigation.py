import logging
from main_screen_navigation import MainScreenNavigation
from groups_screen_navigation import GroupsScreenNavigation

logger = logging.getLogger(__name__)

class Navigation:
    def __init__(self, manager):
        self.manager = manager
        self.strategies = {
            'main': MainScreenNavigation(manager),
            'groups': GroupsScreenNavigation(manager),
        }
        self.current_strategy = self.strategies['main']
        logger.debug("Navigation inicializado")

    def set_strategy(self, screen_type):
        if screen_type in self.strategies:
            self.current_strategy = self.strategies[screen_type]
            if screen_type == 'main':
                self.manager.main_screen_keys.activate()
            elif screen_type == 'groups':
                # Aquí activaríamos las teclas de la pantalla de grupos cuando la implementemos
                pass
            logger.debug(f"Navigation strategy set to: {screen_type}")
        else:
            logger.error(f"Unknown navigation strategy: {screen_type}")

    def navigate_vertical(self, event):
        logger.debug(f"Navegación vertical: {event.keysym}")
        self.current_strategy.navigate_vertical(event)

    def navigate_horizontal(self, event):
        logger.debug(f"Navegación horizontal: {event.keysym}")
        self.current_strategy.navigate_horizontal(event)

    def activate_selected(self, event=None):
        logger.debug("Activando selección")
        self.current_strategy.activate_selected(event)

    def update_highlights(self):
        logger.debug("Actualizando highlights")
        self.current_strategy.update_highlights()

    def initialize_focus(self):
        logger.debug("Inicializando foco")
        self.current_strategy.initialize_focus()

    def get_cards_count(self):
        return self.current_strategy.get_cards_count()

    def handle_focus(self, event=None):
        if self.manager.is_visible:
            self.manager.root.focus_force()
        logger.debug("Manejando foco de la ventana")

    def check_window_state(self):
        try:
            actual_visible = self.manager.root.winfo_viewable()
            if actual_visible != self.manager.is_visible:
                logger.info(f"Corrigiendo estado de visibilidad: {self.manager.is_visible} -> {actual_visible}")
                self.manager.is_visible = actual_visible
        except Exception as e:
            logger.error(f"Error al verificar estado de la ventana: {e}")

    def update_active_window(self):
        import win32gui
        self.manager.last_active_window = win32gui.GetForegroundWindow()
        logger.debug(f"Ventana activa actualizada: {self.manager.last_active_window}")

    def get_current_selection(self):
        return self.manager.current_selection

    def set_current_selection(self, selection_type, index):
        self.manager.current_selection = {'type': selection_type, 'index': index}
        self.update_highlights()
        logger.debug(f"Selección actual establecida: {self.manager.current_selection}")

    def get_clipboard_items(self):
        return self.manager.clipboard_items

    def get_cards_frame(self):
        return self.manager.cards_frame

    def get_canvas(self):
        return self.manager.canvas

    def is_dark_mode(self):
        return self.manager.is_dark_mode

    def get_theme_colors(self):
        return self.manager.theme_manager.colors

    def ensure_visible(self):
        self.current_strategy.ensure_visible()
        logger.debug("Asegurando visibilidad del elemento seleccionado")

    def handle_global_key(self, key):
        logger.debug(f"Manejando tecla global: {key}")
        if self.manager.is_visible:
            if key in ['Up', 'Down']:
                self.navigate_vertical(type('Event', (), {'keysym': key})())
            elif key in ['Left', 'Right']:
                self.navigate_horizontal(type('Event', (), {'keysym': key})())
            elif key == 'Return':
                self.activate_selected()
            
            self.manager.root.update_idletasks()
            self.manager.root.after(10, self.manager.root.update)
            self.manager.root.after(20, self.manager.key_handler.restore_cursor_position)

    def refresh_navigation(self):
        logger.debug("Refrescando navegación")
        self.initialize_focus()
        self.update_highlights()
        if hasattr(self.current_strategy, 'refresh_view'):
            self.current_strategy.refresh_view()

    def on_window_focus(self, event):
        logger.debug("Ventana obtuvo el foco")
        self.refresh_navigation()

    def on_window_unfocus(self, event):
        logger.debug("Ventana perdió el foco")
        # Aquí puedes agregar lógica adicional si es necesario cuando la ventana pierde el foco