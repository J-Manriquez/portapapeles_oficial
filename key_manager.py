# key_manager.py
import win32com
import win32clipboard
import keyboard
import win32gui
import win32com.client
import pyperclip
import time
import pyautogui
import win32api
import win32con
import ctypes
import re
from bs4 import BeautifulSoup

# Definir CF_HTML ya que no está en win32con
CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

class KeyManager:
    def __init__(self, manager):
        self.manager = manager
        self.hotkey = self.manager.hotkey
        self.current_hotkey = None
        self.update_hotkey(None, self.hotkey)
        self.original_cursor_pos = None

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

    def toggle_window(self):
        print("Toggling window")
        if not self.manager.is_visible:
            print("Showing window")
            self.original_cursor_pos = win32gui.GetCursorPos()
            self.show_window()
        else:
            print("Hiding window")
            self.hide_window()

    def hide_window(self):
        self.manager.root.withdraw()
        self.manager.is_visible = False
        self.restore_focus()
        if self.original_cursor_pos:
            win32api.SetCursorPos(self.original_cursor_pos)
        self.setup_global_keys()

    def show_window(self):
        print("In show_window function")
        try:
            self.manager.previous_window = win32gui.GetForegroundWindow()
            self.manager.root.deiconify()
            self.manager.root.lift()
            self.manager.root.attributes('-topmost', True)
            self.manager.is_visible = True
            self.manager.navigation.initialize_focus()
            self.setup_global_keys()
            
            self.manager.root.update_idletasks()
            self.manager.root.after(100, lambda: self.manager.root.attributes('-topmost', False))
            self.manager.root.focus_force()
            
        except Exception as e:
            print(f"Error al mostrar la ventana: {e}")

    def restore_focus(self):
        if self.manager.previous_window:
            try:
                win32gui.SetForegroundWindow(self.manager.previous_window)
            except Exception as e:
                print(f"Error al restaurar el foco: {e}")
                try:
                    self.manager.root.after(100, lambda: win32gui.SetForegroundWindow(self.manager.previous_window))
                except:
                    pass

    def setup_global_keys(self):
        keyboard.unhook_all()
        keyboard.add_hotkey(self.current_hotkey, self.toggle_window)
        keyboard.add_hotkey('up', lambda: self.handle_global_key('Up'))
        keyboard.add_hotkey('down', lambda: self.handle_global_key('Down'))
        keyboard.add_hotkey('left', lambda: self.handle_global_key('Left'))
        keyboard.add_hotkey('right', lambda: self.handle_global_key('Right'))
        keyboard.add_hotkey('enter', lambda: self.handle_global_key('Return'))

    def handle_global_key(self, key):
        if self.manager.is_visible:
            print(f"Handling global key: {key}")
            if key in ['Up', 'Down']:
                self.manager.navigation.navigate_vertical(type('Event', (), {'keysym': key})())
            elif key in ['Left', 'Right']:
                self.manager.navigation.navigate_horizontal(type('Event', (), {'keysym': key})())
            elif key == 'Return':
                self.manager.navigation.activate_selected()
            
            self.manager.root.update_idletasks()
            self.manager.root.after(10, self.manager.root.update)
            self.manager.root.after(20, self.restore_cursor_position)

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