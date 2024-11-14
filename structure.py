# structure.py

import tkinter as tk
from tkinter import ttk
import time
import threading
from datetime import datetime
import keyboard # type: ignore
import sys
import win32gui # type: ignore
from functions import Functions
from navigation import Navigation
from theme_manager import ThemeManager
from group_manager import GroupManager
from data_manager import DataManager
from settings_manager import SettingsManager

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Portapapeles")

        self.data_manager = DataManager()
        groups, pinned_items, settings = self.data_manager.load_data()

        self.settings = settings
        self.window_width = settings['width']
        self.window_height = settings['height']

        self.root.geometry(f"{self.window_width}x{self.window_height}+0+0")
        self.root.overrideredirect(True)
        
        self.root.withdraw()
        self.is_visible = False

        self.previous_window = None

        self.clipboard_items = pinned_items
        self.current_clipboard = ""
        self.selected_index = None
        self.current_selection = {'type': 'button', 'index': 0}
        self.is_dark_mode = True
        
        self.paste_with_format = True
        
        self.previous_window = None
        self.last_active_window = None
        self.selected_button = None
        self.selected_card = None
        self.selected_icon = None
        self.total_buttons = 6
        self.top_buttons = 3
        self.icons_per_card = 3
        self.hotkey = f"alt+{settings['hotkey']}"

        self.theme_manager = ThemeManager(self)
        self.functions = Functions(self)
        self.navigation = Navigation(self)
        self.group_manager = GroupManager(self.root, self)
        self.settings_manager = SettingsManager(self.root, self)
        
        self.group_manager.groups = groups
        
        self.create_gui()
        self.load_saved_data()
        self.theme_manager.apply_theme()

        self.root.bind('<Return>', self.navigation.activate_selected)
        self.root.bind('<Up>', self.navigation.navigate_vertical)
        self.root.bind('<Down>', self.navigation.navigate_vertical)
        self.root.bind('<Left>', self.navigation.navigate_horizontal)
        self.root.bind('<Right>', self.navigation.navigate_horizontal)
        self.root.bind('<FocusIn>', self.navigation.handle_focus)

        self.monitor_thread = threading.Thread(target=self.functions.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

        self.navigation.update_hotkey(None, self.settings_manager.settings['hotkey'])
        keyboard.add_hotkey('up', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Up')))
        keyboard.add_hotkey('down', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Down')))
        keyboard.add_hotkey('left', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Left')))
        keyboard.add_hotkey('right', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Right')))
        keyboard.add_hotkey('enter', lambda: self.root.after(0, lambda: self.navigation.handle_global_key('Return')))    
        
        self.root.after(1000, self.navigation.check_window_state)
        self.root.bind("<Map>", self.on_main_window_map)
        self.root.bind("<Unmap>", self.on_main_window_unmap)

    def create_gui(self):
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_frame = tk.Frame(self.main_frame, bg=self.theme_manager.colors['dark']['bg'])
        self.title_frame.pack(fill=tk.X, padx=3, pady=(0,6))

        self.title_label = tk.Label(self.title_frame, text="Portapapeles", font=('Segoe UI', 10, 'bold'), bg=self.theme_manager.colors['dark']['bg'], fg=self.theme_manager.colors['dark']['fg'])
        self.title_label.pack(side=tk.LEFT, padx=5)

        buttons_frame = tk.Frame(self.title_frame, bg=self.theme_manager.colors['dark']['bg'])
        buttons_frame.pack(side=tk.RIGHT, padx=4)

        self.theme_button = tk.Button(buttons_frame, text="🌙", command=self.theme_manager.toggle_theme, font=('Segoe UI', 10), bd=0, padx=10, width=5, height=2)
        self.theme_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(buttons_frame, text="    🖥️", command=self.settings_manager.show_settings_window, font=('Segoe UI', 10), bd=0, padx=10, width=5, height=2)
        self.clear_button.pack(side=tk.LEFT)

        self.close_button = tk.Button(buttons_frame, text="❌", command=self.functions.exit_app, font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2)
        self.close_button.pack(side=tk.LEFT)

        main_buttons_frame = tk.Frame(self.main_frame, bg=self.theme_manager.colors['dark']['bg'])
        main_buttons_frame.pack(fill=tk.X, padx=6, pady=0)

        self.button1 = tk.Button(main_buttons_frame, text="Grupos", 
                                 command=self.show_groups, font=('Segoe UI', 10), 
                                 bg=self.theme_manager.colors['dark']['button_bg'], 
                                 fg=self.theme_manager.colors['dark']['button_fg'],
                                 relief=tk.FLAT,  # Quita el efecto 3D
                                 bd=0,  # Quita el borde
                                 highlightthickness=1, # Añade un borde fino
                                 pady=8)
        self.button1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=0)

        self.button2 = tk.Button(main_buttons_frame, text="Con formato", 
                                 command=self.functions.toggle_paste_format, font=('Segoe UI', 10), 
                                 bg=self.theme_manager.colors['dark']['button_bg'], 
                                 fg=self.theme_manager.colors['dark']['button_fg'],
                                 relief=tk.FLAT,  # Quita el efecto 3D
                                 bd=0,  # Quita el borde
                                 highlightthickness=1, # Añade un borde fino
                                 pady=8) 
        self.button2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=0)

        self.button3 = tk.Button(main_buttons_frame, text="Borrar Todo", 
                                 command=self.functions.clear_history, font=('Segoe UI', 10), 
                                 bg=self.theme_manager.colors['dark']['button_bg'], 
                                 fg=self.theme_manager.colors['dark']['button_fg'],
                                 relief=tk.FLAT,  # Quita el efecto 3D
                                 bd=0,  # Quita el borde
                                 highlightthickness=1, # Añade un borde fino
                                 pady=8)                               
        self.button3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=0)

        self.canvas = tk.Canvas(self.main_frame, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.cards_frame = tk.Frame(self.canvas, bg=self.theme_manager.colors['dark']['bg'])  
        # self.canvas.create_window((0, 0), window=self.cards_frame, anchor='nw')

        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cards_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack_forget()

        # self.canvas.bind('<Configure>', self.functions.on_canvas_configure)
        # self.canvas.bind_all("<MouseWheel>", self.functions.on_mousewheel)

        self.title_label.bind('<Button-1>', self.navigation.start_move)
        self.title_label.bind('<B1-Motion>', self.navigation.on_move)
        
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.cards_frame.bind('<Configure>', self.on_frame_configure)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
        
    def show_groups(self):
        self.group_manager.show_groups_window()
        
    def load_saved_data(self):
        groups, pinned_items, _ = self.data_manager.load_data()
        self.group_manager.groups = groups
        self.clipboard_items.update(pinned_items)
        self.functions.refresh_cards()
        
    def on_main_window_map(self, event):
        if self.group_manager.groups_window and self.group_manager.groups_window.winfo_exists():
            self.group_manager.groups_window.deiconify()

    def on_main_window_unmap(self, event):
        if self.group_manager.groups_window and self.group_manager.groups_window.winfo_exists():
            self.group_manager.groups_window.withdraw()