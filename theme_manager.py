#theme_manager.py

import tkinter as tk
from tkinter import ttk

class ThemeManager:
    def __init__(self, manager):
        self.manager = manager
        self.colors = {
            'dark': {
                # 4 tonos de negro frío para tema oscuro
                'bg': '#0f0f0f',              # Fondo principal - negro más intenso
                'fg': '#ffffff',              # Texto - blanco puro
                'button_bg': '#1a1a1a',       # Botones superiores y principales - negro menos intenso
                'button_fg': '#ffffff',
                'main_button_bg': '#1a1a1a',  # Botones principales (grupos, formato, borrar)
                'main_button_fg': '#ffffff',
                'card_bg': '#1a1a1a',         # Cards - mismo tono que botones
                'hover_bg': '#2a2a2a',        # Hover simple (30% más claro)
                'icon_hover_bg': '#3a3a3a',   # Hover sobre hover (50% más claro)
                'listbox_bg': '#1a1a1a',
                'listbox_fg': '#ffffff',
                'active_bg': '#2a2a2a',
                'active_fg': '#ffffff',
                'exit_button_bg': '#8B0000',  # Rojo oscuro
                'exit_button_fg': '#ffffff',
                'success_bg': '#228B22',      # Verde oscuro
                'success_fg': '#ffffff',
                'error_bg': '#8B0000',        # Rojo oscuro
                'error_fg': '#ffffff',
            },
            'light': {
                # 4 tonos de blanco para tema claro
                'bg': '#f5f5f5',              # Fondo principal - blanco con contraste
                'fg': '#000000',              # Texto - negro puro
                'button_bg': '#ffffff',       # Botones superiores y principales - blanco brillante
                'button_fg': '#000000',
                'main_button_bg': '#ffffff',  # Botones principales (grupos, formato, borrar)
                'main_button_fg': '#000000',
                'card_bg': '#ffffff',         # Cards - blanco brillante
                'hover_bg': '#e6e6e6',        # Hover simple (30% más oscuro)
                'icon_hover_bg': '#cccccc',   # Hover sobre hover (50% más oscuro)
                'listbox_bg': '#ffffff',
                'listbox_fg': '#000000',
                'active_bg': '#e6e6e6',
                'active_fg': '#000000',
                'exit_button_bg': '#FF6B6B',  # Rojo claro
                'exit_button_fg': '#000000',
                'success_bg': '#32CD32',      # Verde claro
                'success_fg': '#000000',
                'error_bg': '#FF6B6B',        # Rojo claro
                'error_fg': '#000000',
            }
        }

    def toggle_theme(self):
        self.manager.is_dark_mode = not self.manager.is_dark_mode
        self.manager.theme_button.config(text="🌙" if self.manager.is_dark_mode else "☀️")
        self.apply_theme()

    def apply_theme(self):
        theme = self.colors['dark'] if self.manager.is_dark_mode else self.colors['light']

        self.manager.root.configure(bg=theme['bg'])
        self.manager.main_frame.configure(style='Main.TFrame')
        self.manager.title_frame.configure(bg=theme['bg'])
        self.manager.title_label.configure(bg=theme['bg'], fg=theme['fg'])

        self.manager.clear_button.configure(
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['button_bg'],
            activeforeground=theme['button_fg']
        )
        self.manager.theme_button.configure(
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['button_bg'],
            activeforeground=theme['button_fg']
        )

        self.manager.close_button.configure(
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['button_bg'],
            activeforeground=theme['button_fg']
        )

        self.manager.button1.configure(
            bg=theme['main_button_bg'],
            fg=theme['main_button_fg'],
            activebackground=theme['main_button_bg'],
            activeforeground=theme['main_button_fg']
        )

        self.manager.button2.configure(
            bg=theme['main_button_bg'],
            fg=theme['main_button_fg'],
            activebackground=theme['main_button_bg'],
            activeforeground=theme['main_button_fg']
        )

        self.manager.button3.configure(
            bg=theme['main_button_bg'],
            fg=theme['main_button_fg'],
            activebackground=theme['main_button_bg'],
            activeforeground=theme['main_button_fg']
        )

        self.manager.canvas.configure(bg=theme['bg'])
        self.manager.cards_frame.configure(bg=theme['bg'])

        self.manager.functions.refresh_cards()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Main.TFrame', background=theme['bg'])
