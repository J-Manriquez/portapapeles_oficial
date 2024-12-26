# navigation_strategies.py

from abc import ABC, abstractmethod

class NavigationStrategy(ABC):
    @abstractmethod
    def navigate_vertical(self, event):
        pass

    @abstractmethod
    def navigate_horizontal(self, event):
        pass

    @abstractmethod
    def activate_selected(self, event=None):
        pass

    @abstractmethod
    def update_highlights(self):
        pass

    @abstractmethod
    def initialize_focus(self):
        pass

# Nota: Las implementaciones concretas de MainScreenNavigation, GroupsScreenNavigation,
# y SettingsScreenNavigation ahora están en archivos separados.