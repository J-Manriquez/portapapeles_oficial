# key_manager.py

import traceback
import win32com.client
import win32clipboard
import keyboard
import win32gui
import win32api
import win32con
import pyperclip
import time
import pyautogui
import ctypes
import base64

class KeyManager:
    def __init__(self, manager):
        self.manager = manager
        self.hotkey = self.manager.hotkey
        self.current_hotkey = None
        self.update_hotkey(None, self.hotkey)
        self.original_cursor_pos = None
        self.CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
        print("KeyManager initialized")

    def update_hotkey(self, old_hotkey, new_hotkey):
        print(f"Updating hotkey from {old_hotkey} to {new_hotkey}")
        if old_hotkey:
            try:
                keyboard.remove_hotkey(old_hotkey)
                print(f"Removed old hotkey: {old_hotkey}")
            except KeyError:
                print(f"Failed to remove previous hotkey: {old_hotkey}")

        if not new_hotkey.lower().startswith('alt+'):
            new_hotkey = 'alt+' + new_hotkey
        
        keyboard.add_hotkey(new_hotkey, self.toggle_window)
        self.current_hotkey = new_hotkey
        print(f"New hotkey configured: {new_hotkey}")

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
        print("Hiding window")
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
            print("Window shown successfully")
        except Exception as e:
            print(f"Error showing window: {e}")

    def restore_focus(self):
        print("Restoring focus")
        if self.manager.previous_window:
            try:
                win32gui.SetForegroundWindow(self.manager.previous_window)
                print("Focus restored to previous window")
            except Exception as e:
                print(f"Error restoring focus: {e}")
                try:
                    self.manager.root.after(100, lambda: win32gui.SetForegroundWindow(self.manager.previous_window))
                    print("Attempting to restore focus after delay")
                except:
                    print("Failed to restore focus after delay")

    def setup_global_keys(self):
        print("Setting up global keys")
        keyboard.unhook_all()
        keyboard.add_hotkey(self.current_hotkey, self.toggle_window)
        keyboard.add_hotkey('up', lambda: self.handle_global_key('Up'))
        keyboard.add_hotkey('down', lambda: self.handle_global_key('Down'))
        keyboard.add_hotkey('left', lambda: self.handle_global_key('Left'))
        keyboard.add_hotkey('right', lambda: self.handle_global_key('Right'))
        keyboard.add_hotkey('enter', lambda: self.handle_global_key('Return'))
        print("Global keys set up")

    def handle_global_key(self, key):
        print(f"Handling global key: {key}")
        if self.manager.is_visible:
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
            print("Cursor position restored")

    def paste_content(self, clipboard_data):
        print("Starting paste_content method")
        try:
            self.hide_window()
            time.sleep(0.1)
            print("Window hidden")

            self.activate_target_window()
            print("Target window activated")
            
            if isinstance(clipboard_data, dict):
                text = clipboard_data.get('text', '')
                formatted = clipboard_data.get('formatted')
            else:
                text = str(clipboard_data)
                formatted = None

            print(f"Clipboard data - Text: {text}")
            print(f"Formatted data available: {'Yes' if formatted else 'No'}")
            print(f"Paste with format: {self.manager.paste_with_format}")

            # Guardar el contenido actual del portapapeles
            original_clipboard = self.get_clipboard_content()

            try:
                self.set_clipboard_content(text, formatted)
                
                # Intentar métodos de pegado en orden
                if not self.primary_paste_method():
                    print("Primary paste method failed, trying backup method")
                    if not self.backup_paste_method():
                        print("Backup paste method failed, trying fallback method")
                        self.fallback_paste_method(text)
            except Exception as e:
                print(f"Error during paste operation: {e}")
                print(traceback.format_exc())
            finally:
                # Restaurar el contenido original del portapapeles
                self.set_clipboard_content(original_clipboard)
            
        except Exception as e:
            print(f"Error in paste process: {e}")
            print(traceback.format_exc())
        finally:
            if self.original_cursor_pos:
                win32api.SetCursorPos(self.original_cursor_pos)
                print(f"Cursor position restored to original: {self.original_cursor_pos}")
            self.original_cursor_pos = None

    def primary_paste_method(self):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('^v')
            time.sleep(0.1)
            print("Primary paste method successful")
            return True
        except Exception as e:
            print(f"Primary paste method failed: {e}")
            return False

    def backup_paste_method(self):
        try:
            keyboard.send('ctrl+v')
            time.sleep(0.1)
            print("Backup paste method successful")
            return True
        except Exception as e:
            print(f"Backup paste method failed: {e}")
            return False

    def fallback_paste_method(self, text):
        try:
            pyperclip.copy(text)
            keyboard.write(text)
            print("Fallback paste method successful")
        except Exception as e:
            print(f"Fallback paste method failed: {e}")

    def get_clipboard_content(self):
        for _ in range(5):  # Intentar hasta 5 veces
            try:
                win32clipboard.OpenClipboard()
                try:
                    if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                        return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    return ""
                finally:
                    win32clipboard.CloseClipboard()
            except win32clipboard.error:
                print("Error accessing clipboard, retrying...")
                time.sleep(0.1)
        print("Failed to access clipboard after multiple attempts")
        return ""

    def set_clipboard_content(self, text, formatted=None):
        for _ in range(5):  # Intentar hasta 5 veces
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                try:
                    if self.manager.paste_with_format and formatted:
                        if isinstance(formatted, str) and formatted.startswith('<html>'):
                            cf_html = win32clipboard.RegisterClipboardFormat("HTML Format")
                            win32clipboard.SetClipboardData(cf_html, formatted.encode('utf-8'))
                        elif isinstance(formatted, bytes):
                            win32clipboard.SetClipboardData(win32con.CF_RTF, formatted)
                    else:
                        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
                    return  # Si llegamos aquí, la operación fue exitosa
                finally:
                    win32clipboard.CloseClipboard()
            except win32clipboard.error:
                print("Error setting clipboard content, retrying...")
                time.sleep(0.1)
        print("Failed to set clipboard content after multiple attempts")

    def activate_target_window(self):
        print("Activating target window")
        target_window = win32gui.GetForegroundWindow()
        win32gui.SetForegroundWindow(target_window)
        time.sleep(0.2)  # Increased delay to ensure window activation
        print("Target window activated")
        
print("key_manager.py loaded")