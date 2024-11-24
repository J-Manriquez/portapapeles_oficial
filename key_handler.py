# key_handler.py
import keyboard
import win32gui
import win32api
import win32clipboard
import win32com.client
import win32con
import pyautogui
import pyperclip
import time
import logging
from typing import Dict, Callable, Optional

logger = logging.getLogger(__name__)

class GlobalHotkeyManager:
    """Maneja los atajos de teclado globales de la aplicación"""
    
    def __init__(self):
        self._hotkeys: Dict[str, Callable] = {}
        keyboard.unhook_all()
    
    def register_hotkey(self, key: str, callback: Callable) -> None:
        """Registra un nuevo atajo global"""
        if key in self._hotkeys:
            keyboard.remove_hotkey(key)
        self._hotkeys[key] = callback
        keyboard.add_hotkey(key, callback)
        logger.debug(f"Registered global hotkey: {key}")
    
    def unregister_hotkey(self, key: str) -> None:
        """Elimina un atajo global"""
        if key in self._hotkeys:
            keyboard.remove_hotkey(key)
            del self._hotkeys[key]
            logger.debug(f"Unregistered global hotkey: {key}")
    
    def update_hotkey(self, old_key: Optional[str], new_key: str, callback: Callable) -> None:
        """Actualiza un atajo existente con una nueva tecla"""
        if old_key:
            self.unregister_hotkey(old_key)
        self.register_hotkey(new_key, callback)
        logger.debug(f"Updated hotkey from {old_key} to {new_key}")

class KeyHandler:
    """Coordinador principal del sistema de teclas"""
    
    def __init__(self, manager):
        self.manager = manager
        self.global_hotkeys = GlobalHotkeyManager()
        self.current_screen = 'main'
        # self.screen_specific_hotkeys: Dict[str, Dict[str, Callable]] = {}
        self.screen_specific_hotkeys = {}
        self.original_cursor_pos = None
        
        # Inicializar el hotkey principal
        self.setup_main_hotkey()
        
    def register_global_hotkey(self, key: str, callback: Callable) -> None:
        """Registra un atajo de teclado global"""
        self.global_hotkeys.register_hotkey(key, callback)
        
    def register_screen_hotkey(self, screen: str, key: str, callback: Callable) -> None:
        """Registra un atajo de teclado específico para una pantalla"""
        if screen not in self.screen_specific_hotkeys:
            self.screen_specific_hotkeys[screen] = {}
        self.screen_specific_hotkeys[screen][key] = callback
        logger.debug(f"Registered screen hotkey: {key} for screen {screen}")

    def unregister_screen_hotkey(self, screen: str, key: str) -> None:
        """Elimina un atajo de teclado específico de una pantalla"""
        if screen in self.screen_specific_hotkeys and key in self.screen_specific_hotkeys[screen]:
            del self.screen_specific_hotkeys[screen][key]
            logger.debug(f"Unregistered screen hotkey: {key} for screen {screen}")

    def set_current_screen(self, screen: str) -> None:
        """Establece la pantalla actual para manejar los atajos de teclado"""
        self.current_screen = screen
        logger.debug(f"Set current screen to: {screen}")
        
        # Limpiar los atajos anteriores
        self.screen_specific_hotkeys = {}
        
        # Reconfigurar los atajos según la pantalla actual
        if screen == 'select_group':
            self.manager.select_group_screen_keys.setup_keys()

    def handle_key_press(self, event):
        """Maneja las pulsaciones de teclas"""
        print(f"KeyHandler received key: {event.keysym}")  # Debug
        key = event.keysym.lower()
        
        # Manejar teclas específicas de la pantalla actual
        if self.current_screen in self.screen_specific_hotkeys:
            if key in self.screen_specific_hotkeys[self.current_screen]:
                print(f"Executing screen-specific handler for {key}")  # Debug
                self.screen_specific_hotkeys[self.current_screen][key]()
                return True
        
        # Propagar el evento a la estrategia de navegación actual
        if self.manager.is_visible:
            self.manager.navigation.handle_keyboard_event(event)
            return True
        
        # Manejar teclas globales
        if key in self.global_hotkeys._hotkeys:
            print(f"Executing global handler for {key}")  # Debug
            self.global_hotkeys._hotkeys[key]()
            return True
            
        # Asegurar que la ventana correcta tiene el foco
        if self.current_screen == 'main':
            self.manager.root.focus_force()
        elif self.current_screen == 'select_group' and hasattr(self.manager, 'select_group_dialog'):
            self.manager.select_group_dialog.focus_force()
        
        return False

    def setup_main_hotkey(self) -> None:
        """Configura el atajo principal de la aplicación"""
        hotkey = self.manager.hotkey
        if not hotkey.lower().startswith('alt+'):
            hotkey = 'alt+' + hotkey
        self.global_hotkeys.register_hotkey(hotkey, self.toggle_window)
        
    def toggle_window(self) -> None:
        """Alterna la visibilidad de la ventana principal"""
        logger.debug("Toggling window")
        if not self.manager.is_visible:
            # Asegurarse de que estamos en la estrategia principal
            self.manager.navigation.set_strategy('main')
            self.show_window()
        else:
            self.hide_window()
            
    def show_window(self) -> None:
        """Muestra la ventana principal"""
        try:
            self.manager.previous_window = win32gui.GetForegroundWindow()
            self.original_cursor_pos = win32gui.GetCursorPos()
            
            # Posicionar ventana
            mouse_x, mouse_y = pyautogui.position()
            window_x = mouse_x - self.manager.window_width // 2
            window_y = mouse_y - self.manager.window_height // 2
            
            # Ajustar a los límites de la pantalla
            screen_width, screen_height = pyautogui.size()
            window_x = max(0, min(window_x, screen_width - self.manager.window_width))
            window_y = max(0, min(window_y, screen_height - self.manager.window_height))
            
            self.manager.root.geometry(f"{self.manager.window_width}x{self.manager.window_height}+{window_x}+{window_y}")
            self.manager.window_x = window_x
            self.manager.window_y = window_y
            
            # Asegurarse de que estamos en la navegación principal
            self.manager.navigation.set_strategy('main')
            self._show_and_focus_window()
            
            # Inicializar el foco y la navegación
            self.manager.navigation.initialize_focus()
            
        except Exception as e:
            logger.error(f"Error showing window: {e}")
            # En caso de error, intentar restablecer a un estado conocido
            self.manager.navigation.set_strategy('main')
            self.manager.show_main_screen()
            
    def _show_and_focus_window(self) -> None:
        """Muestra y enfoca la ventana principal"""
        self.manager.root.deiconify()
        self.manager.root.lift()
        self.manager.root.attributes('-topmost', True)
        self.manager.is_visible = True
        self.manager.navigation.initialize_focus()
        
        self.manager.canvas.update_idletasks()
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))
        
        self.manager.root.update_idletasks()
        self.manager.root.after(100, lambda: self.manager.root.attributes('-topmost', False))
        self.manager.root.focus_force()

    def hide_window(self) -> None:
        """Oculta la ventana principal"""
        self.manager.root.withdraw()
        self.manager.is_visible = False
        self.restore_focus()
        if self.original_cursor_pos:
            win32api.SetCursorPos(self.original_cursor_pos)
            self.original_cursor_pos = None

    def restore_focus(self) -> None:
        """Restaura el foco a la ventana anterior"""
        if self.manager.previous_window:
            try:
                win32gui.SetForegroundWindow(self.manager.previous_window)
            except Exception as e:
                logger.error(f"Error restoring focus: {e}")
                try:
                    self.manager.root.after(100, lambda: win32gui.SetForegroundWindow(self.manager.previous_window))
                except:
                    pass

    def restore_cursor_position(self):
        if self.original_cursor_pos:
            win32api.SetCursorPos(self.original_cursor_pos)

    def paste_content(self, clipboard_data):
        try:
            self.hide_window()
            current_cursor_pos = win32gui.GetCursorPos()
            
            if isinstance(clipboard_data, dict):
                text = clipboard_data.get('text', '')
                format_info = clipboard_data.get('formatted', {})
            else:
                text = str(clipboard_data)
                format_info = {}

            if self.manager.paste_with_format and format_info:
                formatted_content = self.apply_format_to_text(text, format_info)
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, formatted_content)
                win32clipboard.CloseClipboard()
            else:
                pyperclip.copy(text)
            
            time.sleep(0.05)
            
            if self.manager.previous_window:
                win32gui.SetForegroundWindow(self.manager.previous_window)
                time.sleep(0.05)
                
                win32api.SetCursorPos(current_cursor_pos)
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys("^v")
            
            self.original_cursor_pos = None
            
        except Exception as e:
            print(f"Error en el proceso de pegado: {e}")
        finally:
            if self.original_cursor_pos:
                win32api.SetCursorPos(self.original_cursor_pos)
            self.original_cursor_pos = None

    def apply_format_to_text(self, text, format_info):
        if 'rtf' in format_info:
            return self.apply_rtf_format(text, format_info)
        elif 'html' in format_info:
            return self.apply_html_format(text, format_info)
        else:
            return text

    def apply_rtf_format(self, text, format_info):
        rtf = r"{\rtf1\ansi\deff0"
        if format_info.get('font'):
            rtf += r"{\fonttbl{\f0\fnil " + format_info['font'] + r";}}"
        if format_info.get('color'):
            rtf += r"{\colortbl;\red" + str(format_info['color'][0]) + r"\green" + str(format_info['color'][1]) + r"\blue" + str(format_info['color'][2]) + r";}"
        rtf += r"\f0"
        if format_info.get('size'):
            rtf += r"\fs" + str(int(format_info['size'] * 2))
        if format_info.get('bold'):
            rtf += r"\b"
        if format_info.get('italic'):
            rtf += r"\i"
        rtf += " " + text.replace("\n", r"\par ") + r"}"
        return rtf

    def apply_html_format(self, text, format_info):
        html = "<div style='"
        if format_info.get('font'):
            html += f"font-family: {format_info['font']}; "
        if format_info.get('size'):
            html += f"font-size: {format_info['size']}pt; "
        if format_info.get('color'):
            html += f"color: rgb{format_info['color']}; "
        html += "'>"
        if format_info.get('bold'):
            html += "<strong>"
        if format_info.get('italic'):
            html += "<em>"
        html += text
        if format_info.get('italic'):
            html += "</em>"
        if format_info.get('bold'):
            html += "</strong>"
        html += "</div>"
        return html

