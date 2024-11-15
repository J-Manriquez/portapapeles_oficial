# key_manager.py
import win32com
import win32clipboard  # type: ignore
import keyboard
import win32gui
import win32com.client
import pyperclip
import time
import pyautogui

# Definir CF_HTML ya que no está en win32con
CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

class KeyManager:
    def __init__(self, manager):
        self.manager = manager
        self.hotkey = self.manager.hotkey
        self.update_hotkey(None, self.hotkey)

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
        if not self.manager.is_visible:
            self.manager.root.after(10, self.manager.functions.recalculate_card_heights)
        try:
            if self.manager.is_visible:
                self.hide_window()
            else:
                self.manager.previous_window = win32gui.GetForegroundWindow()
                self.manager.root.after(10, self.show_window)
        except Exception as e:
            print(f"Error al alternar la ventana: {e}")

    def hide_window(self):
        try:
            self.manager.root.attributes('-topmost', False)
            self.manager.root.withdraw()
            self.manager.is_visible = False
            self.restore_focus()
        except Exception as e:
            print(f"Error al ocultar la ventana: {e}")

    def show_window(self):
        try:
            self.manager.previous_window = win32gui.GetForegroundWindow()
            
            # Obtener la posición actual del cursor
            mouse_x, mouse_y = pyautogui.position()
            
            # Calcular la posición de la ventana
            window_x = mouse_x - self.manager.window_width // 2
            window_y = mouse_y - self.manager.window_height // 2
            
            # Asegurar que la ventana no se salga de la pantalla
            screen_width, screen_height = pyautogui.size()
            window_x = max(0, min(window_x, screen_width - self.manager.window_width))
            window_y = max(0, min(window_y, screen_height - self.manager.window_height))
            
            self.manager.root.geometry(f"{self.manager.window_width}x{self.manager.window_height}+{window_x}+{window_y}")
            self.manager.window_x = window_x  # Guarda la posición x de la ventana
            self.manager.window_y = window_y  # Guarda la posición y de la ventana
            
            self.manager.root.deiconify()
            self.manager.root.geometry("+0+0") 
            self.manager.root.lift()  
            self.manager.root.attributes('-topmost', True)
            
            self.manager.is_visible = True
            
            self.manager.navigation.initialize_focus()
        
            if not hasattr(self.manager, 'current_selection') or not self.manager.current_selection:
                self.manager.current_selection = {'type': 'card', 'index': 0}
            
            self.manager.root.focus_force()
            self.manager.navigation.update_highlights()
            
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

    def handle_global_key(self, key):
        if self.manager.is_visible:
            if key in ['Up', 'Down']:
                self.manager.navigation.navigate_vertical(type('Event', (), {'keysym': key})())
            elif key in ['Left', 'Right']:
                self.manager.navigation.navigate_horizontal(type('Event', (), {'keysym': key})())
            elif key == 'Return':
                self.manager.navigation.activate_selected()
            self.manager.root.after(10, self.manager.root.update_idletasks)
            return 'break'  # Prevenir que el evento se propague
        return None

    def setup_global_keys(self):
        keyboard.add_hotkey('up', lambda: self.manager.root.after(0, lambda: self.handle_global_key('Up')))
        keyboard.add_hotkey('down', lambda: self.manager.root.after(0, lambda: self.handle_global_key('Down')))
        keyboard.add_hotkey('left', lambda: self.manager.root.after(0, lambda: self.handle_global_key('Left')))
        keyboard.add_hotkey('right', lambda: self.manager.root.after(0, lambda: self.handle_global_key('Right')))
        keyboard.add_hotkey('enter', lambda: self.manager.root.after(0, lambda: self.handle_global_key('Return')))

    def paste_content(self, clipboard_data):
        try:
            self.hide_window()
            
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
                    win32clipboard.SetClipboardData(CF_HTML, formatted.encode('utf-8'))
                win32clipboard.CloseClipboard()
            else:
                # Pegar sin formato
                pyperclip.copy(text)
            
            time.sleep(0.05)
            
            if self.manager.previous_window:
                win32gui.SetForegroundWindow(self.manager.previous_window)
                time.sleep(0.05)
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys("^v")
                
        except Exception as e:
            print(f"Error en el proceso de pegado: {e}")