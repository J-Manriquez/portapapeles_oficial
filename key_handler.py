# key_handler.py
import pyperclip
import win32clipboard
import win32com.client
import keyboard
import win32gui
import win32api
import win32con
import pyautogui
import time
import logging

logger = logging.getLogger(__name__)

class KeyHandler:
    def __init__(self, manager):
        self.manager = manager
        self.global_hotkeys = {}
        self.screen_specific_hotkeys = {}
        self.current_screen = 'main'
        self.original_cursor_pos = None
        self.current_hotkey = None
        self.hotkey = self.manager.hotkey
        self.update_hotkey(None, self.hotkey)
        
    def update_hotkey(self, old_hotkey, new_hotkey):
        if old_hotkey:
            try:
                keyboard.remove_hotkey(old_hotkey)
            except KeyError:
                print(f"No se pudo eliminar el atajo anterior: {old_hotkey}")

        if not new_hotkey.lower().startswith('alt+'):
            new_hotkey = 'alt+' + new_hotkey
        
        keyboard.add_hotkey(new_hotkey, self.toggle_window)
        self.current_hotkey = new_hotkey
        print(f"Nuevo atajo configurado: {new_hotkey}")

    def register_global_hotkey(self, key, callback, priority=0):
        if key not in self.global_hotkeys:
            self.global_hotkeys[key] = []
        self.global_hotkeys[key].append((callback, priority))
        self.global_hotkeys[key].sort(key=lambda x: x[1], reverse=True)
        keyboard.add_hotkey(key, lambda: self.handle_global_hotkey(key))
        logger.debug(f"Registered global hotkey: {key}")

    def register_screen_hotkey(self, screen, key, callback):
        if screen not in self.screen_specific_hotkeys:
            self.screen_specific_hotkeys[screen] = {}
        self.screen_specific_hotkeys[screen][key] = callback
        logger.debug(f"Registered screen hotkey: {key} for screen {screen}")

    def unregister_global_hotkey(self, key):
        if key in self.global_hotkeys:
            del self.global_hotkeys[key]
            keyboard.remove_hotkey(key)
            logger.debug(f"Unregistered global hotkey: {key}")

    def unregister_screen_hotkey(self, screen, key):
        if screen in self.screen_specific_hotkeys and key in self.screen_specific_hotkeys[screen]:
            del self.screen_specific_hotkeys[screen][key]
            logger.debug(f"Unregistered screen hotkey: {key} for screen {screen}")

    def set_current_screen(self, screen):
        self.current_screen = screen
        logger.info(f"Current screen set to: {screen}")

    def handle_global_hotkey(self, key):
        if key in self.global_hotkeys:
            for callback, _ in self.global_hotkeys[key]:
                callback()

    def handle_key_press(self, event):
        key = event.keysym.lower()
        if self.current_screen in self.screen_specific_hotkeys and key in self.screen_specific_hotkeys[self.current_screen]:
            self.screen_specific_hotkeys[self.current_screen][key]()
        elif key in self.global_hotkeys:
            self.handle_global_hotkey(key)

    def setup_global_keys(self):
        keyboard.unhook_all()
        for key in self.global_hotkeys:
            keyboard.add_hotkey(key, lambda k=key: self.handle_global_hotkey(k))
        logger.info("Global keys setup completed")

    def toggle_window(self):
        logger.debug("Toggling window")
        if not self.manager.is_visible:
            logger.debug("Showing window")
            self.original_cursor_pos = win32gui.GetCursorPos()
            self.show_window()
        else:
            logger.debug("Hiding window")
            self.hide_window()

    def hide_window(self):
        self.manager.root.withdraw()
        self.manager.is_visible = False
        self.restore_focus()
        if self.original_cursor_pos:
            win32api.SetCursorPos(self.original_cursor_pos)
        self.setup_global_keys()

    def show_window(self):
        logger.debug("In show_window function")
        try:
            self.manager.previous_window = win32gui.GetForegroundWindow()
            mouse_x, mouse_y = pyautogui.position()
            
            window_x = mouse_x - self.manager.window_width // 2
            window_y = mouse_y - self.manager.window_height // 2
            
            screen_width, screen_height = pyautogui.size()
            window_x = max(0, min(window_x, screen_width - self.manager.window_width))
            window_y = max(0, min(window_y, screen_height - self.manager.window_height))
            
            self.manager.root.geometry(f"{self.manager.window_width}x{self.manager.window_height}+{window_x}+{window_y}")
            self.manager.window_x = window_x
            self.manager.window_y = window_y
            
            self.manager.root.deiconify()
            self.manager.root.lift()
            self.manager.root.attributes('-topmost', True)
            self.manager.is_visible = True
            self.manager.navigation.initialize_focus()
            self.setup_global_keys()
            
            self.manager.canvas.update_idletasks()
            self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))
            
            self.manager.root.update_idletasks()
            self.manager.root.after(100, lambda: self.manager.root.attributes('-topmost', False))
            self.manager.root.focus_force()
            
        except Exception as e:
            logger.error(f"Error al mostrar la ventana: {e}")

    def restore_focus(self):
        if self.manager.previous_window:
            try:
                win32gui.SetForegroundWindow(self.manager.previous_window)
            except Exception as e:
                logger.error(f"Error al restaurar el foco: {e}")
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