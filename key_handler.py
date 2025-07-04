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
import tkinter as tk

from typing import Dict, Callable, Optional

# Definir CF_HTML ya que no está en win32con
CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

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
        # logger.debug(f"Registered global hotkey: {key}")

    def unregister_hotkey(self, key: str) -> None:
        """Elimina un atajo global"""
        if key in self._hotkeys:
            keyboard.remove_hotkey(key)
            del self._hotkeys[key]
            # logger.debug(f"Unregistered global hotkey: {key}")

    def update_hotkey(self, old_key: Optional[str], new_key: str, callback: Callable) -> None:
        """Actualiza un atajo existente con una nueva tecla"""
        if old_key:
            self.unregister_hotkey(old_key)
        self.register_hotkey(new_key, callback)
        # logger.debug(f"Updated hotkey from {old_key} to {new_key}")

class KeyHandler:
    """Coordinador principal del sistema de teclas"""

    def __init__(self, manager):
        self.manager = manager
        self.global_hotkeys = GlobalHotkeyManager()
        self.current_screen = 'main'
        # self.screen_specific_hotkeys: Dict[str, Dict[str, Callable]] = {}
        self.screen_specific_hotkeys = {}
        self.original_cursor_pos = None
        self.active_window = None  # rastrear la ventana activa
        self.last_keyboard_selection = None
        # Inicializar el hotkey principal
        self.setup_main_hotkey()

        self.setup_additional_hotkeys()

    def setup_additional_hotkeys(self):
        """Configura los atajos adicionales"""
        try:
            # Tecla para mostrar grupos
            groups_key = f"alt+{self.manager.settings.get('groups_key', 'g')}"
            self.global_hotkeys.register_hotkey(groups_key, self.show_groups_screen)

            # Tecla para nuevo grupo
            new_group_key = f"alt+{self.manager.settings.get('new_group_key', 'n')}"
            self.global_hotkeys.register_hotkey(new_group_key, self.show_new_group_dialog)

            # logger.debug(f"Additional hotkeys registered: {groups_key}, {new_group_key}")
        except Exception as e:
            logger.error(f"Error setting up additional hotkeys:{e}")

    def show_groups_screen(self):
        """Maneja la apertura de la pantalla de grupos"""
        try:
            # Guardar las dimensiones actuales de las cards
            current_dimensions = self._save_current_card_dimensions()

            # Ocultar la ventana actual
            self.hide_window()

            # Mostrar la ventana de grupos
            def show_groups():
                self.manager.group_manager.show_groups_window()
                # Restaurar las dimensiones de las cards
                self._restore_card_dimensions(current_dimensions)

            # Usar after para asegurar que la secuencia sea correcta
            self.manager.root.after(100, show_groups)

        except Exception as e:
            logger.error(f"Error showing groups screen: {e}")

    def _save_current_card_dimensions(self):
        """Guarda las dimensiones actuales de las cards"""
        dimensions = []
        if hasattr(self.manager, 'cards_frame'):
            for card in self.manager.cards_frame.winfo_children():
                if hasattr(card, 'item_id'):
                    dimensions.append({
                        'id': card.item_id,
                        'width': card.winfo_width(),
                        'height': card.winfo_height()
                    })
        return dimensions

    def _restore_card_dimensions(self, dimensions):
        """Restaura las dimensiones guardadas de las cards"""
        if hasattr(self.manager, 'cards_frame'):
            for card in self.manager.cards_frame.winfo_children():
                if hasattr(card, 'item_id'):
                    for dim in dimensions:
                        if dim['id'] == card.item_id:
                            card.configure(width=dim['width'], height=dim['height'])
                            card.pack_propagate(False)
                            break

    def show_new_group_dialog(self):
        """Maneja la apertura del diálogo de nuevo grupo desde cualquier pantalla"""
        try:
            # Ocultar todas las ventanas activas
            self.hide_window()  # Esto ocultará todas las ventanas activas

            # Asegurarse de que el manager y group_manager existen
            if hasattr(self.manager, 'group_manager'):
                # Usar after para asegurar que las ventanas se hayan ocultado primero
                self.manager.root.after(100, self.manager.group_manager.add_group)

        except Exception as e:
            logger.error(f"Error showing new group dialog: {e}")

    def register_global_hotkey(self, key: str, callback: Callable) -> None:
        """Registra un atajo de teclado global"""
        self.global_hotkeys.register_hotkey(key, callback)

    def register_screen_hotkey(self, screen: str, key: str, callback: Callable) -> None:
        """Registra un atajo de teclado específico para una pantalla"""
        if screen not in self.screen_specific_hotkeys:
            self.screen_specific_hotkeys[screen] = {}
        self.screen_specific_hotkeys[screen][key] = callback
        # logger.debug(f"Registered screen hotkey: {key} for screen {screen}")

    def unregister_screen_hotkey(self, screen: str, key: str) -> None:
        """Elimina un atajo de teclado específico de una pantalla"""
        if screen in self.screen_specific_hotkeys and key in self.screen_specific_hotkeys[screen]:
            del self.screen_specific_hotkeys[screen][key]
            # logger.debug(f"Unregistered screen hotkey: {key} for screen {screen}")

    def set_current_screen(self, screen: str) -> None:
        """Establece la pantalla actual para manejar los atajos de teclado"""
        self.current_screen = screen
        # logger.debug(f"Set current screen to: {screen}")

        # Limpiar los atajos anteriores
        self.screen_specific_hotkeys = {}

        # Reconfigurar los atajos según la pantalla actual
        if screen == 'select_group':
            self.manager.select_group_screen_keys.setup_keys()

    def handle_key_press(self, event):
        """Maneja las pulsaciones de teclas"""
        # print(f"KeyHandler received key: {event.keysym}")  # Debug
        key = event.keysym.lower()

        # Manejar teclas específicas de la pantalla actual
        if self.current_screen in self.screen_specific_hotkeys:
            if key in self.screen_specific_hotkeys[self.current_screen]:
                # print(f"Executing screen-specific handler for {key}")  # Debug
                self.screen_specific_hotkeys[self.current_screen][key]()
                return True

        # Propagar el evento a la estrategia de navegación actual
        if self.manager.is_visible:
            self.manager.navigation.handle_keyboard_event(event)
            return True

        # Manejar teclas globales
        if key in self.global_hotkeys._hotkeys:
            # print(f"Executing global handler for {key}")  # Debug
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
        """Alterna la visibilidad de las ventanas"""
        if self.check_open_windows():
            # Si hay ventanas abiertas, ocultarlas
            print('--CERRANDO SCREENS')
            self.hide_window()
            self.manager.is_visible = False  # Asegurar que el estado es correcto
        else:
            # Si no hay ventanas abiertas, mostrar la principal
            self.show_window()
            self.manager.is_visible = True  # Asegurar que el estado es correcto


    def check_open_windows(self) -> bool:
        """
        Verifica si hay ventanas abiertas
        Returns:
            bool: True si hay ventanas abiertas, False en caso contrario
        """
        windows_status = [
            # Ventana principal
            self.manager.is_visible,

            # Ventana de grupos
            hasattr(self.manager.group_manager, 'groups_window') and
            self.manager.group_manager.groups_window and
            self.manager.group_manager.groups_window.winfo_exists() and
            self.manager.group_manager.groups_window.winfo_viewable(),

            # Ventana de contenido de grupo
            hasattr(self.manager.group_manager.group_content_manager, 'content_window') and
            self.manager.group_manager.group_content_manager.content_window and
            self.manager.group_manager.group_content_manager.content_window.winfo_exists() and
            self.manager.group_manager.group_content_manager.content_window.winfo_viewable(),

            # Ventana de configuraciones
            hasattr(self.manager.settings_manager, 'settings_window') and
            self.manager.settings_manager.settings_window and
            self.manager.settings_manager.settings_window.winfo_exists() and
            self.manager.settings_manager.settings_window.winfo_viewable(),

            # Diálogo de selección de grupo
            hasattr(self.manager, 'select_group_dialog') and
            self.manager.select_group_dialog and
            self.manager.select_group_dialog.winfo_exists() and
            self.manager.select_group_dialog.winfo_viewable(),

            # Diálogo de edición de grupo
            hasattr(self.manager.group_manager, '_edit_dialog') and
            self.manager.group_manager._edit_dialog and
            self.manager.group_manager._edit_dialog.winfo_exists() and
            self.manager.group_manager._edit_dialog.winfo_viewable(),

            # Diálogo de edición de texto de grupo
            hasattr(self.manager.group_manager.group_content_manager, '_edit_dialog') and
            self.manager.group_manager.group_content_manager._edit_dialog and
            self.manager.group_manager.group_content_manager._edit_dialog.winfo_exists() and
            self.manager.group_manager.group_content_manager._edit_dialog.winfo_viewable()
        ]

        return any(windows_status)

    def show_window(self) -> None:
        """Muestra la ventana principal con animación de deslizamiento desde abajo"""
        try:
            self.manager.previous_window = win32gui.GetForegroundWindow()
            self.original_cursor_pos = win32gui.GetCursorPos()

            # Calcular posición final (donde está el mouse)
            mouse_x, mouse_y = pyautogui.position()
            final_window_x = mouse_x - self.manager.window_width // 2
            final_window_y = mouse_y - self.manager.window_height // 2

            # Ajustar a los límites de la pantalla
            screen_width, screen_height = pyautogui.size()
            final_window_x = max(0, min(final_window_x, screen_width - self.manager.window_width))
            final_window_y = max(0, min(final_window_y, screen_height - self.manager.window_height))

            # Posición inicial (abajo de la pantalla)
            start_window_x = final_window_x
            start_window_y = screen_height  # Comenzar desde abajo de la pantalla

            self.manager.window_x = final_window_x
            self.manager.window_y = final_window_y

            # Preparar completamente la ventana antes de mostrarla
            def prepare_and_show_window():
                # Asegurar que estamos en la navegación principal
                self.manager.navigation.set_strategy('main')
                self.manager.main_screen_keys.activate()
                
                # Reinicializar los estados de hover
                if hasattr(self.manager.navigation, 'current_strategy') and self.manager.navigation.current_strategy:
                    self.manager.navigation.current_strategy.last_keyboard_selection = None
                self._reset_hover_states()

                # Refrescar la vista principal (esto ya incluye la carga optimizada)
                self.manager.functions.refresh_cards()
                
                # Inicializar navegación y foco
                self.manager.navigation.initialize_focus()
                
                # Posicionar la ventana en la posición final desde el inicio
                self.manager.root.geometry(f"{self.manager.window_width}x{self.manager.window_height}+{final_window_x}+{start_window_y}")
                
                # Mostrar la ventana
                self.manager.root.deiconify()
                self.manager.root.lift()
                self.manager.root.attributes('-topmost', True)
                self.manager.is_visible = True
                
                # Forzar actualización completa de la interfaz
                self.manager.root.update_idletasks()
                self.manager.root.update()
                
                # Añadir pausa antes de iniciar la animación
                self.manager.root.after(50, lambda: self._animate_slide_up(start_window_y, final_window_y, final_window_x))

            # Ejecutar la preparación inmediatamente
            self.manager.root.after_idle(prepare_and_show_window)

        except Exception as e:
            logger.error(f"Error showing main window: {e}")

    def _animate_slide_up(self, start_y: int, final_y: int, window_x: int) -> None:
        """Anima el deslizamiento de la ventana desde abajo hasta la posición final"""
        try:
            # Configuración de la animación
            animation_duration = 300  # milisegundos
            animation_steps = 20
            step_delay = animation_duration // animation_steps
            
            # Calcular la distancia total
            total_distance = start_y - final_y
            
            def animate_step(current_step: int):
                if current_step <= animation_steps:
                    # Calcular progreso con easing (suavizado)
                    progress = current_step / animation_steps
                    # Aplicar easing out (desaceleración al final)
                    eased_progress = 1 - (1 - progress) ** 3
                    
                    # Calcular posición actual
                    current_y = int(start_y - (total_distance * eased_progress))
                    
                    # Actualizar posición de la ventana
                    try:
                        self.manager.root.geometry(f"{self.manager.window_width}x{self.manager.window_height}+{window_x}+{current_y}")
                        
                        # Programar siguiente paso
                        if current_step < animation_steps:
                            self.manager.root.after(step_delay, lambda: animate_step(current_step + 1))
                        else:
                            # Animación completada
                            self._finish_window_animation()
                    except tk.TclError:
                        # Si hay error, terminar animación
                        self._finish_window_animation()
                else:
                    self._finish_window_animation()
            
            # Iniciar animación
            animate_step(0)
            
        except Exception as e:
            logger.error(f"Error in slide animation: {e}")
            self._finish_window_animation()
    
    def _finish_window_animation(self) -> None:
        """Finaliza la animación y configura el estado final de la ventana"""
        try:
            # Asegurar posición final correcta
            self.manager.root.geometry(f"{self.manager.window_width}x{self.manager.window_height}+{self.manager.window_x}+{self.manager.window_y}")
            
            # Configurar foco final
            self.manager.root.focus_force()
            
            # Remover topmost después de un momento
            self.manager.root.after(100, lambda: self.manager.root.attributes('-topmost', False))
            
        except Exception as e:
            logger.error(f"Error finishing window animation: {e}")

    def _reset_hover_states(self):
        """Resetea todos los estados de hover de los elementos"""
        if hasattr(self.manager, 'cards_frame'):
            for card in self.manager.cards_frame.winfo_children():
                for child in card.winfo_children():
                    if isinstance(child, tk.Frame):
                        for btn in child.winfo_children():
                            if hasattr(btn, '_mouse_over'):
                                btn._mouse_over = False
                            if hasattr(btn, '_is_highlighted'):
                                btn._is_highlighted = False

    # def show_window(self) -> None:
    #     """Muestra la ventana principal"""
    #     try:
    #         self.manager.previous_window = win32gui.GetForegroundWindow()
    #         self.original_cursor_pos = win32gui.GetCursorPos()

    #         # Posicionar ventana
    #         mouse_x, mouse_y = pyautogui.position()
    #         window_x = mouse_x - self.manager.window_width // 2
    #         window_y = mouse_y - self.manager.window_height // 2

    #         # Ajustar a los límites de la pantalla
    #         screen_width, screen_height = pyautogui.size()
    #         window_x = max(0, min(window_x, screen_width - self.manager.window_width))
    #         window_y = max(0, min(window_y, screen_height - self.manager.window_height))

    #         self.manager.root.geometry(f"{self.manager.window_width}x{self.manager.window_height}+{window_x}+{window_y}")
    #         self.manager.window_x = window_x
    #         self.manager.window_y = window_y

    #         # Asegurarse de que estamos en la navegación principal
    #         self.manager.navigation.set_strategy('main')
    #         self._show_and_focus_window()

    #         # Inicializar el foco y la navegación
    #         self.manager.navigation.initialize_focus()

    #     except Exception as e:
    #         logger.error(f"Error showing window: {e}")
    #         # En caso de error, intentar restablecer a un estado conocido
    #         self.manager.navigation.set_strategy('main')
    #         self.manager.show_main_screen()

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
        """Oculta la ventana actualmente activa"""
        try:
            # Ocultar ventana de grupos
            if hasattr(self.manager.group_manager, 'groups_window') and \
            self.manager.group_manager.groups_window and \
            self.manager.group_manager.groups_window.winfo_exists():
                self.manager.group_manager.groups_window.withdraw()

            # Ocultar ventana de contenido de grupo
            if hasattr(self.manager.group_manager.group_content_manager, 'content_window') and \
            self.manager.group_manager.group_content_manager.content_window and \
            self.manager.group_manager.group_content_manager.content_window.winfo_exists():
                self.manager.group_manager.group_content_manager.content_window.withdraw()

            # Ocultar ventana de configuraciones
            if hasattr(self.manager.settings_manager, 'settings_window') and \
            self.manager.settings_manager.settings_window and \
            self.manager.settings_manager.settings_window.winfo_exists():
                self.manager.settings_manager.settings_window.withdraw()

            # Ocultar ventana de selección de grupo
            if hasattr(self.manager, 'select_group_dialog') and \
            self.manager.select_group_dialog and \
            self.manager.select_group_dialog.winfo_exists():
                try:
                    self.manager.select_group_dialog.withdraw()
                except tk.TclError:
                    pass  # Ignorar si la ventana ya no existe

            # Ocultar diálogo de edición de grupo
            if hasattr(self.manager.group_manager, '_edit_dialog') and \
            self.manager.group_manager._edit_dialog and \
            self.manager.group_manager._edit_dialog.winfo_exists():
                self.manager.group_manager._edit_dialog.withdraw()

            # Ocultar diálogo de edición de texto de grupo
            if hasattr(self.manager.group_manager.group_content_manager, '_edit_dialog') and \
            self.manager.group_manager.group_content_manager._edit_dialog and \
            self.manager.group_manager.group_content_manager._edit_dialog.winfo_exists():
                self.manager.group_manager.group_content_manager._edit_dialog.withdraw()

            # Ocultar ventana principal
            self.manager.root.withdraw()
            self.manager.is_visible = False
            self.restore_focus()

        except Exception as e:
            logger.error(f"Error hiding active window: {e}")

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
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                
                # Poner el texto plano
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                
                # Si hay contenido RTF original, usarlo
                if 'rtf_content' in format_info:
                    win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat("Rich Text Format"), format_info['rtf_content'])
                
                # Si hay contenido HTML original, usarlo
                elif 'html_content' in format_info:
                    win32clipboard.SetClipboardData(CF_HTML, format_info['html_content'])
                
                # Fallback: recrear formato si solo tenemos información de formato
                elif 'rtf' in format_info:
                    rtf_content = self.apply_rtf_format(text, format_info)
                    win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat("Rich Text Format"), rtf_content.encode('utf-8'))
                
                elif 'html' in format_info:
                    html_content = self.apply_html_format(text, format_info)
                    win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat("HTML Format"), html_content.encode('utf-8'))
                
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

