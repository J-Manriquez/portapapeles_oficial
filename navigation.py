from navigation_strategies import MainScreenNavigation, GroupsScreenNavigation, SettingsScreenNavigation

class Navigation:
    def __init__(self, manager):
        self.manager = manager
        self.strategies = {
            'main': MainScreenNavigation(manager),
            # 'groups': GroupsScreenNavigation(manager),
            # 'settings': SettingsScreenNavigation(manager)
        }
        self.current_strategy = self.strategies['main']

    def set_strategy(self, screen_type):
        if screen_type in self.strategies:
            self.current_strategy = self.strategies[screen_type]
            print(f"Estrategia de navegación cambiada a: {screen_type}")
        else:
            print(f"Estrategia de navegación no reconocida: {screen_type}")

    def navigate_vertical(self, event):
        self.current_strategy.navigate_vertical(event)

    def navigate_horizontal(self, event):
        self.current_strategy.navigate_horizontal(event)

    def activate_selected(self, event=None):
        self.current_strategy.activate_selected(event)

    def update_highlights(self):
        self.current_strategy.update_highlights()

    def initialize_focus(self):
        self.current_strategy.initialize_focus()

    def handle_focus(self, event=None):
        if self.manager.is_visible:
            self.manager.root.focus_force()

    def check_window_state(self):
        try:
            actual_visible = self.manager.root.winfo_viewable()
            if actual_visible != self.manager.is_visible:
                print(f"Corrigiendo estado de visibilidad: {self.manager.is_visible} -> {actual_visible}")
                self.manager.is_visible = actual_visible
        except Exception as e:
            print(f"Error al verificar estado de la ventana: {e}")

    def update_active_window(self):
        import win32gui
        self.manager.last_active_window = win32gui.GetForegroundWindow()

    # Métodos adicionales que podrían ser útiles
    def get_current_selection(self):
        return self.manager.current_selection

    def set_current_selection(self, selection_type, index):
        self.manager.current_selection = {'type': selection_type, 'index': index}
        self.update_highlights()

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