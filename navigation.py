# navigation.py

from main_screen_navigation import MainScreenNavigation
# from groups_screen_navigation import GroupsScreenNavigation
# from settings_screen_navigation import SettingsScreenNavigation

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
       #printf"Estrategia de navegación cambiada a: {screen_type}")
        else:
            print(f"Estrategia de navegación no reconocida: {screen_type}")

    def navigate_vertical(self, event):
   #printf"Navigating vertically: {event.keysym}")  # Añade este print para depuración
        self.current_strategy.navigate_vertical(event)

    def navigate_horizontal(self, event):
   #printf"Navigating horizontally: {event.keysym}")  # Añade este print para depuración
        self.current_strategy.navigate_horizontal(event)

    def activate_selected(self, event=None):
   #print"Activating selected")  # Añade este print para depuración
        self.current_strategy.activate_selected(event)

    def update_highlights(self):
        self.current_strategy.update_highlights()


    def get_cards_count(self):
        return len(self.manager.cards_frame.winfo_children()) if hasattr(self.manager, 'cards_frame') else 0

    def initialize_focus(self):
        if self.get_cards_count() > 0:
            self.manager.current_selection = {'type': 'cards', 'index': 0}
        else:
            self.manager.current_selection = {'type': 'main_buttons', 'index': 0}
        
        self.update_highlights()
        self.manager.root.update_idletasks()

    def handle_focus(self, event=None):
        if self.manager.is_visible:
            self.manager.root.focus_force()

    def check_window_state(self):
        try:
            actual_visible = self.manager.root.winfo_viewable()
            if actual_visible != self.manager.is_visible:
           #print'**********'f"Corrigiendo estado de visibilidad: {self.manager.is_visible} -> {actual_visible}")
                self.manager.is_visible = actual_visible
        except Exception as e:
            print(f"Error al verificar estado de la ventana: {e}")

    def update_active_window(self):
        import win32gui
        self.manager.last_active_window = win32gui.GetForegroundWindow()

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