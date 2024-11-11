# structure.py

import tkinter as tk
from tkinter import ttk
import time
import threading
from datetime import datetime
import keyboard
import sys
import win32gui
from functions import Functions
from navigation import Navigation
from theme_manager import ThemeManager

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Portapapeles")

        window_width = 295
        window_height = 400
        
        self.window_width = window_width

        self.root.geometry(f"{window_width}x{window_height}+0+0")
        self.root.overrideredirect(True)
        
        self.root.withdraw()
        self.is_visible = False

        self.previous_window = None

        self.clipboard_items = {}  # Diccionario para almacenar los items del portapapeles
        self.current_clipboard = ""
        self.selected_index = None
        self.is_visible = False
        self.current_selection = {'type': 'button', 'index': 0}  # type puede ser 'button', 'card' o 'icon'
        self.is_dark_mode = True
        
        self.previous_window = None
        self.last_active_window = None
        self.selected_button = None  # Para la navegación de botones
        self.selected_card = None    # Para la navegación de cards
        self.selected_icon = None    # Para la navegación de iconos en una card
        self.total_buttons = 3
        self.icons_per_card = 3

        self.functions = Functions(self)
        self.navigation = Navigation(self)
        self.theme_manager = ThemeManager(self)

        self.create_gui()
        self.theme_manager.apply_theme()

        self.root.bind('<Return>', self.navigation.activate_selected)
        self.root.bind('<Up>', self.navigation.navigate_vertical)
        self.root.bind('<Down>', self.navigation.navigate_vertical)
        self.root.bind('<Left>', self.navigation.navigate_horizontal)
        self.root.bind('<Right>', self.navigation.navigate_horizontal)
        self.root.bind('<FocusIn>', self.navigation.handle_focus)

        self.monitor_thread = threading.Thread(target=self.functions.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

        keyboard.add_hotkey('alt+j', self.navigation.toggle_window)
        keyboard.add_hotkey('up', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Up')))
        keyboard.add_hotkey('down', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Down')))
        keyboard.add_hotkey('left', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Left')))
        keyboard.add_hotkey('right', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Right')))
        keyboard.add_hotkey('enter', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Return')))
             
        self.root.after(1000, self.navigation.check_window_state)

    def create_gui(self):
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_frame = tk.Frame(self.main_frame, bg=self.theme_manager.colors['dark']['bg'])
        self.title_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.title_label = tk.Label(self.title_frame, text="Portapapeles", font=('Segoe UI', 10, 'bold'), bg=self.theme_manager.colors['dark']['bg'], fg=self.theme_manager.colors['dark']['fg'])
        self.title_label.pack(side=tk.LEFT, padx=5)

        buttons_frame = tk.Frame(self.title_frame, bg=self.theme_manager.colors['dark']['bg'])
        buttons_frame.pack(side=tk.RIGHT, padx=4)

        self.clear_button = tk.Button(buttons_frame, text="      🗑️", command=self.functions.clear_history, font=('Segoe UI', 10), bd=0, padx=10, width=5, height=2)
        self.clear_button.pack(side=tk.LEFT)

        self.theme_button = tk.Button(buttons_frame, text="🌙", command=self.theme_manager.toggle_theme, font=('Segoe UI', 10), bd=0, padx=10, width=5, height=2)
        self.theme_button.pack(side=tk.LEFT)

        self.close_button = tk.Button(buttons_frame, text="❌", command=self.functions.exit_app, font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2)
        self.close_button.pack(side=tk.LEFT)

        main_buttons_frame = tk.Frame(self.main_frame, bg=self.theme_manager.colors['dark']['bg'])
        main_buttons_frame.pack(fill=tk.X, padx=8, pady=(5, 0))

        self.button1 = tk.Button(main_buttons_frame, text="Botón 1", font=('Segoe UI', 10), bg=self.theme_manager.colors['dark']['button_bg'], fg=self.theme_manager.colors['dark']['button_fg'])
        self.button1.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.button2 = tk.Button(main_buttons_frame, text="Botón 2", font=('Segoe UI', 10), bg=self.theme_manager.colors['dark']['button_bg'], fg=self.theme_manager.colors['dark']['button_fg'])
        self.button2.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.button3 = tk.Button(main_buttons_frame, text="Botón 3", font=('Segoe UI', 10), bg=self.theme_manager.colors['dark']['button_bg'], fg=self.theme_manager.colors['dark']['button_fg'])
        self.button3.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.canvas = tk.Canvas(self.main_frame, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.cards_frame = tk.Frame(self.canvas, bg=self.theme_manager.colors['dark']['bg'])  
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor='nw')

        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.pack_forget()

        self.canvas.bind('<Configure>', self.functions.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.functions.on_mousewheel)

        self.title_label.bind('<Button-1>', self.navigation.start_move)
        self.title_label.bind('<B1-Motion>', self.navigation.on_move)