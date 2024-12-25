from tkinter import ttk


class ThemeManager:
    def __init__(self, manager):
        self.manager = manager
        self.colors = {
            'dark': {
                'bg': '#1e1e1e',
                'fg': '#ffffff',
                'button_bg': '#333333',
                'button_fg': '#ffffff',
                'listbox_bg': '#2d2d2d',
                'listbox_fg': '#ffffff',
                'active_bg': '#4E4E4E',
                'active_fg': '#FFFFFF',
                'hover_bg': '#4E4E4E',     # Añadir color específico para hover
                'hover_fg': '#FFFFFF',      # Añadir color específico para hover texto
                'card_bg': '#333333',
                'exit_button_bg': '#8B0000',
                'exit_button_fg': '#ffffff',
            },
            'light': {
                'bg': '#fffff0',
                'fg': '#000000',
                'button_bg': '#e0e0e0',
                'button_fg': '#000000',
                'listbox_bg': '#ffffff',
                'listbox_fg': '#000000',
                'active_bg': '#D0D0D0',
                'active_fg': '#000000',
                'hover_bg': '#D0D0D0',     # Añadir color específico para hover
                'hover_fg': '#000000',      # Añadir color específico para hover texto
                'card_bg': '#e0e0e0',
                'exit_button_bg': '#FF6B6B',
                'exit_button_fg': '#000000',
            }
        }

    def toggle_theme(self):
        """Cambia entre tema oscuro y claro"""
        self.manager.is_dark_mode = not self.manager.is_dark_mode
        self.manager.theme_button.config(text="🌙" if self.manager.is_dark_mode else "☀️")
        self.apply_theme()
        # Guardar el estado del tema en la configuración
        self.manager.settings['is_dark_mode'] = self.manager.is_dark_mode
        self.manager.settings_manager.save_settings()

    def apply_theme(self):
        """Aplica el tema actual a todos los elementos"""
        theme = self.colors['dark'] if self.manager.is_dark_mode else self.colors['light']

        # Configurar el fondo principal
        self.manager.root.configure(bg=theme['bg'])
        self.manager.main_frame.configure(style='Main.TFrame')

        # Configurar la barra de título
        self.manager.title_frame.configure(bg=theme['bg'])
        self.manager.title_label.configure(bg=theme['bg'], fg=theme['fg'])

        # Configurar el frame de botones principales
        main_buttons_frame = self.manager.main_frame.winfo_children()[1]  # Asumiendo que es el segundo hijo
        main_buttons_frame.configure(bg=theme['bg'])

        # Función para configurar hover en botones
        def setup_button_hover(button):
            def on_enter(e):
                button.configure(
                    bg=theme['hover_bg'],
                    fg=theme['hover_fg'],
                    activebackground=theme['hover_bg'],
                    activeforeground=theme['hover_fg']
                )

            def on_leave(e):
                button.configure(
                    bg=theme['button_bg'],
                    fg=theme['button_fg'],
                    activebackground=theme['button_bg'],
                    activeforeground=theme['button_fg']
                )

            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
            # Configurar colores iniciales
            button.configure(
                bg=theme['button_bg'],
                fg=theme['button_fg'],
                activebackground=theme['button_bg'],
                activeforeground=theme['button_fg']
            )

        # Configurar botones de la barra superior
        for button in [self.manager.theme_button, self.manager.clear_button, self.manager.close_button]:
            setup_button_hover(button)

        # Configurar botones principales
        for button in [self.manager.button1, self.manager.button2, self.manager.button3]:
            setup_button_hover(button)

        # Configurar canvas y frame de tarjetas
        self.manager.canvas.configure(bg=theme['bg'])
        self.manager.cards_frame.configure(bg=theme['bg'])

        # Refrescar las tarjetas para aplicar el nuevo tema
        self.manager.functions.refresh_cards()

        # Configurar estilo ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Main.TFrame', background=theme['bg'])

        # Forzar actualización de la interfaz
        self.manager.root.update_idletasks()
