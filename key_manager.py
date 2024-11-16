# key_manager.py
import win32com
import win32clipboard  # type: ignore
import keyboard
import win32gui
import win32com.client
import pyperclip
import time
import pyautogui
import win32api
import win32con
import ctypes

# Definir CF_HTML ya que no está en win32con
CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

class KeyManager:
    def __init__(self, manager):
        self.manager = manager
        self.hotkey = self.manager.hotkey
        self.update_hotkey(None, self.hotkey)
        self.original_cursor_pos = None

    def update_hotkey(self, old_hotkey, new_hotkey):
        if old_hotkey:
            try:
                keyboard.remove_hotkey(old_hotkey)
            except KeyError:
                print(f"No se pudo eliminar el atajo anterior: {old_hotkey}")

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
            
            # Forzar la actualización de la ventana
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
            self.manager.root.after(20, self.restore_cursor_position)  # Restaurar cursor después de la actualización

    def restore_cursor_position(self):
        if self.original_cursor_pos:
            win32api.SetCursorPos(self.original_cursor_pos)


    def paste_content(self, clipboard_data):
        try:
            # Ocultar la ventana de la aplicación
            self.hide_window()
            
            # Guardar la posición actual del cursor
            current_cursor_pos = win32gui.GetCursorPos()
            
            if isinstance(clipboard_data, dict):
                text = clipboard_data.get('text', '')
                formatted = clipboard_data.get('formatted')
            else:
                text = str(clipboard_data)
                formatted = None

            if self.manager.paste_with_format and formatted:
                # Pegar con formato
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                if isinstance(formatted, str) and formatted.startswith('{\\rtf'):
                    win32clipboard.SetClipboardData(win32con.CF_RTF, formatted.encode('utf-8'))
                elif isinstance(formatted, str):
                    CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
                    win32clipboard.SetClipboardData(CF_HTML, formatted.encode('utf-8'))
                win32clipboard.CloseClipboard()
            else:
                # Pegar sin formato
                pyperclip.copy(text)
            
            # Esperar un poco para asegurar que el portapapeles se ha actualizado
            time.sleep(0.05)
            
            # Restaurar el foco a la ventana anterior
            if self.manager.previous_window:
                win32gui.SetForegroundWindow(self.manager.previous_window)
                time.sleep(0.05)
                
                # Restaurar la posición del cursor
                win32api.SetCursorPos(current_cursor_pos)
                
                # Simular la pulsación de teclas Ctrl+V para pegar
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys("^v")
            
            # Limpiar la posición original del cursor
            self.original_cursor_pos = None
            
        except Exception as e:
            print(f"Error en el proceso de pegado: {e}")
        finally:
            # Asegurarse de que la posición del cursor se restaure incluso si hay un error
            if self.original_cursor_pos:
                win32api.SetCursorPos(self.original_cursor_pos)
            self.original_cursor_pos = None