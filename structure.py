# structure.py

import tkinter as tk
from tkinter import ttk
import threading
import win32gui
import pyautogui

from functions import Functions
from key_manager import KeyManager
from navigation import Navigation
from theme_manager import ThemeManager
from group_manager import GroupManager
from data_manager import DataManager
from settings_manager import SettingsManager

import logging

logger = logging.getLogger(__name__)

class ClipboardManager:
    def __init__(self, root, show_settings=False):
        self.root = root
        self.root.title("Portapapeles")

        self.data_manager = DataManager()
        groups, pinned_items, settings = self.data_manager.load_data()
        
        self.settings = settings
        self.settings_manager = SettingsManager(self.root, self)
        self.settings_manager.initialize_settings()

        self.window_width = settings['width']
        self.window_height = settings['height']
        self.window_x = 0
        self.window_y = 0

        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Manejar el cierre de la ventana

        
        self.root.withdraw()
        self.is_visible = False

        self.previous_window = None

        self.clipboard_items = {}
        for item_id, item_data in pinned_items.items():
            if isinstance(item_data['text'], dict):
                self.clipboard_items[item_id] = item_data
            else:
                # Si el texto no es un diccionario, lo convertimos a la estructura esperada
                self.clipboard_items[item_id] = {
                    'text': {'text': item_data['text'], 'formatted': {}},
                    'pinned': item_data['pinned']
                }
                
        self.current_clipboard = ""
        self.selected_index = None
        self.current_selection = {'type': 'button', 'index': 0}
        self.is_dark_mode = True
        
        self.paste_with_format = False
        
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
        self.key_manager = KeyManager(self)
        self.group_manager = GroupManager(self.root, self)
        
        self.group_manager.groups = groups
        
        self.create_gui()
        self.load_saved_data()
        
        self.navigation = Navigation(self)
        
        self.theme_manager.apply_theme()

        self.monitor_thread = threading.Thread(target=self.functions.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

        self.key_manager.update_hotkey(None, self.settings_manager.settings['hotkey'])
                
        if show_settings:
            self.root.after(100, self.settings_manager.show_settings_window)
        
        self.root.after(1000, self.navigation.check_window_state)
        self.key_manager.setup_global_keys()
        
        # scroll
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.cards_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
    def force_update(self):
        self.root.update_idletasks()
        self.root.update()
            
    def on_close(self):
        self.root.withdraw()
        self.is_visible = False

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

        self.clear_button = tk.Button(buttons_frame, text="    🖥️", command=self.show_settings, font=('Segoe UI', 10), bd=0, padx=10, width=5, height=2)
        self.clear_button.pack(side=tk.LEFT)

        self.close_button = tk.Button(buttons_frame, text="❌", command=self.functions.exit_app, font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2)
        self.close_button.pack(side=tk.LEFT)

        main_buttons_frame = tk.Frame(self.main_frame, bg=self.theme_manager.colors['dark']['bg'])
        main_buttons_frame.pack(fill=tk.X, padx=6, pady=0)

        self.button1 = tk.Button(main_buttons_frame, text="Grupos", 
                                 command=self.show_groups, font=('Segoe UI', 10), 
                                 bg=self.theme_manager.colors['dark']['button_bg'], 
                                 fg=self.theme_manager.colors['dark']['button_fg'],
                                 relief=tk.FLAT,
                                 bd=0,
                                 highlightthickness=1,
                                 pady=8)
        self.button1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=0)

        self.button2 = tk.Button(main_buttons_frame, text="Sin formato", 
                                 command=self.functions.toggle_paste_format, font=('Segoe UI', 10), 
                                 bg=self.theme_manager.colors['dark']['button_bg'], 
                                 fg=self.theme_manager.colors['dark']['button_fg'],
                                 relief=tk.FLAT,
                                 bd=0,
                                 highlightthickness=1,
                                 pady=8) 
        self.button2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=0)

        self.button3 = tk.Button(main_buttons_frame, text="Borrar Todo", 
                                 command=self.functions.clear_history, font=('Segoe UI', 10), 
                                 bg=self.theme_manager.colors['dark']['button_bg'], 
                                 fg=self.theme_manager.colors['dark']['button_fg'],
                                 relief=tk.FLAT,
                                 bd=0,
                                 highlightthickness=1,
                                 pady=8)                               
        self.button3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1, pady=0)

        self.canvas = tk.Canvas(self.main_frame, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.cards_frame = tk.Frame(self.canvas, bg=self.theme_manager.colors['dark']['bg'])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor='nw')

        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Variables para el movimiento de la ventana
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # Vincular eventos para mover la ventana
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<ButtonRelease-1>', self.stop_move)
        self.title_label.bind('<B1-Motion>', self.on_move)
        
        # Vincula eventos de scroll
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.cards_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def scrollbar_set(self, start, end):
        # Este método se llama cuando el canvas actualiza su región de scroll
        self.canvas.yview_moveto(float(start))

    def show_groups(self):
        logger.debug("Mostrando ventana de grupos")
        self.group_manager.show_groups_window()
        self.navigation.set_strategy('groups')
        self.root.withdraw()
        
        # Desvincula los eventos de teclado de la ventana principal
        self.root.unbind('<Up>')
        self.root.unbind('<Down>')
        self.root.unbind('<Left>')
        self.root.unbind('<Right>')
        self.root.unbind('<Return>')

    def show_settings(self):
        self.settings_manager.show_settings_window()
        self.navigation.set_strategy('settings')
        self.root.withdraw()
        
    def refresh_main_screen(self):
        # Actualizar la región de desplazamiento
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Volver a vincular eventos de scroll
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.cards_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Asegurarse de que el canvas tenga el foco
        self.canvas.focus_set()
        
        # Refrescar las tarjetas
        self.functions.refresh_cards()

    def show_main_screen(self):
        # Lógica para mostrar la pantalla principal
        self.navigation.set_strategy('main')
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.refresh_main_screen()

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

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def stop_move(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["item"] = None

    def on_move(self, event):
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{x}+{y}")
        self.window_x = x
        self.window_y = y

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        # Asegurarse de que el canvas tenga el foco
        self.canvas.focus_set()
        # Scroll
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def on_scroll(self, *args):
        # Este método se llama cuando se realiza un scroll
        if len(args) == 3 and isinstance(args[2], str):
            self.canvas.yview_moveto(args[0])
        elif len(args) == 2 and isinstance(args[0], str):
            self.canvas.yview_scroll(int(args[1]), args[0])