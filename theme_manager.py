#theme_manager.py

import tkinter as tk
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
                'active_bg': '#4E4E4E',  # Añadido
                'active_fg': '#FFFFFF',  # Añadido
                'card_bg': '#333333',
                'exit_button_bg': '#8B0000',  # Rojo oscuro
                'exit_button_fg': '#ffffff',
            },
            'light': {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'button_bg': '#e0e0e0',
                'button_fg': '#000000',
                'listbox_bg': '#ffffff',
                'listbox_fg': '#000000',
                'active_bg': '#D0D0D0',  # Añadido
                'active_fg': '#000000',  # Añadido
                'card_bg': '#ffffff',
                'exit_button_bg': '#FF6B6B',  # Rojo claro
                'exit_button_fg': '#000000',
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
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['button_bg'],
            activeforeground=theme['button_fg']
        )

        self.manager.button2.configure(
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['button_bg'],
            activeforeground=theme['button_fg']
        )

        self.manager.button3.configure(
            bg=theme['button_bg'],
            fg=theme['button_fg'],
            activebackground=theme['button_bg'],
            activeforeground=theme['button_fg']
        )

        self.manager.canvas.configure(bg=theme['bg'])
        self.manager.cards_frame.configure(bg=theme['bg'])

        self.manager.functions.refresh_cards()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Main.TFrame', background=theme['bg'])
