# navigation.py
import win32com.client
import tkinter as tk
import win32gui
import keyboard
import time
import pyperclip
from utils import measure_time  

class Navigation:
    def __init__(self, manager):
        self.manager = manager

    @measure_time
    def navigate_vertical(self, event):
        if not self.manager.is_visible:
            return
        
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        try:
            if current_type == 'card':
                items = list(self.manager.clipboard_items.keys())
                if event.keysym == 'Up':
                    if current_index > 0:
                        self.manager.current_selection['index'] = current_index - 1
                    else:
                        # Mover a los botones 1, 2 y pegar
                        self.manager.current_selection = {'type': 'button', 'index': 0}
                elif event.keysym == 'Down':
                    if current_index < len(items) - 1:
                        self.manager.current_selection['index'] = current_index + 1
            
            elif current_type == 'button':
                if event.keysym == 'Up':
                    if current_index < 3:  # Estamos en los botones 1, 2, pegar
                        # Mover a la barra superior
                        self.manager.current_selection = {'type': 'top_button', 'index': 0}
                    else:  # Estamos en la barra superior
                        # No hacer nada, ya estamos en la parte superior
                        pass
                elif event.keysym == 'Down':
                    if current_index < 3:  # Estamos en los botones 1, 2, pegar
                        if len(self.manager.clipboard_items) > 0:
                            # Mover a la primera card
                            self.manager.current_selection = {'type': 'card', 'index': 0}
                    else:  # Estamos en la barra superior
                        # Mover a los botones 1, 2, pegar
                        self.manager.current_selection = {'type': 'button', 'index': 0}
            
            elif current_type == 'top_button':
                if event.keysym == 'Down':
                    # Mover a los botones 1, 2, pegar
                    self.manager.current_selection = {'type': 'button', 'index': 0}
            
            elif current_type == 'icon':
                card_index = current_index // self.manager.icons_per_card
                if event.keysym == 'Up':
                    if card_index > 0:
                        self.manager.current_selection = {'type': 'card', 'index': card_index - 1}
                    else:
                        # Mover a los botones 1, 2, pegar
                        self.manager.current_selection = {'type': 'button', 'index': 0}
                elif event.keysym == 'Down':
                    if card_index < len(self.manager.clipboard_items) - 1:
                        self.manager.current_selection = {'type': 'card', 'index': card_index + 1}
            
            if len(self.manager.cards_frame.winfo_children()) > 0:
                target_widget = None
                if current_type == 'card' and self.manager.current_selection['index'] < len(self.manager.clipboard_items):
                    target_widget = self.manager.cards_frame.winfo_children()[self.manager.current_selection['index']]
                
                if target_widget:
                    self.ensure_visible(target_widget)
            
            self.update_highlights()
            
        except Exception as e:
            print(f"Error en navegación vertical: {e}")
            
    @measure_time
    def navigate_horizontal(self, event):
        if not self.manager.is_visible:
            return
        
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        try:
            if current_type == 'card':
                if event.keysym == 'Right':
                    # Mover al icono de flecha (primer icono)
                    self.manager.current_selection = {'type': 'icon', 'index': current_index * self.manager.icons_per_card}
                # No hay acción para 'Left' en una card
            
            elif current_type == 'icon':
                card_index = current_index // self.manager.icons_per_card
                icon_position = current_index % self.manager.icons_per_card
                
                if event.keysym == 'Left':
                    if icon_position > 0:
                        # Mover al icono anterior
                        self.manager.current_selection['index'] = current_index - 1
                    else:
                        # Volver a la card
                        self.manager.current_selection = {'type': 'card', 'index': card_index}
                elif event.keysym == 'Right':
                    if icon_position < self.manager.icons_per_card - 1:
                        # Mover al siguiente icono
                        self.manager.current_selection['index'] = current_index + 1
                    # No hay acción si estamos en el último icono
            
            elif current_type == 'button':
                if current_index < 3:  # Botones 1, 2, pegar
                    if event.keysym == 'Left':
                        self.manager.current_selection['index'] = (current_index - 1) % 3
                    elif event.keysym == 'Right':
                        self.manager.current_selection['index'] = (current_index + 1) % 3
                else:  # Barra superior
                    if event.keysym == 'Left':
                        self.manager.current_selection['index'] = 3 + (current_index - 4) % 3
                    elif event.keysym == 'Right':
                        self.manager.current_selection['index'] = 3 + (current_index - 2) % 3
            
            elif current_type == 'top_button':
                if event.keysym == 'Left':
                    self.manager.current_selection['index'] = (current_index - 1) % 3
                elif event.keysym == 'Right':
                    self.manager.current_selection['index'] = (current_index + 1) % 3
            
            self.update_highlights()
            
        except Exception as e:
            print(f"Error en navegación horizontal: {e}")
    @measure_time
    def activate_selected(self, event=None):
        start_time = time.time()
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        if current_type == 'button':
            if current_index == 0:  # Botón 1
                pass  # Implementar función para Botón 1
            elif current_index == 1:  # Botón 2
                pass  # Implementar función para Botón 2
            elif current_index == 2:  # Botón 3 (Pegar con/sin formato)
                self.manager.functions.toggle_paste_format()
            elif current_index == 3:  # Botón Eliminar todas las cards
                self.manager.functions.clear_history()
            elif current_index == 4:  # Botón Cambiar tema
                self.manager.theme_manager.toggle_theme()
            elif current_index == 5:  # Botón Cerrar app
                self.manager.functions.exit_app()
        elif current_type == 'card':
            items = list(self.manager.clipboard_items.items())
            if current_index < len(items):
                item_id, item_data = items[current_index]
                clipboard_data = item_data['text']
                self.paste_content(clipboard_data)
        elif current_type == 'icon':
            items = list(self.manager.clipboard_items.keys())
            card_index = current_index // self.manager.icons_per_card
            icon_position = current_index % self.manager.icons_per_card
            
            if card_index < len(items):
                item_id = items[card_index]
                if icon_position == 0:  # Arrow
                    pass
                elif icon_position == 1:  # Pin
                    self.manager.functions.toggle_pin(item_id)
                elif icon_position == 2:  # Delete
                    self.manager.functions.delete_item(item_id)

        end_time = time.time()
        print(f"Tiempo total de operación: {(end_time - start_time) * 1000:.2f} ms")
        
    @measure_time
    def paste_content(self, clipboard_data):
        try:
            self.hide_window()
            
            # Copiar el contenido al portapapeles
            pyperclip.copy(clipboard_data)
            
            # Esperar un poco para asegurar que el portapapeles se ha actualizado
            time.sleep(0.05)
            
            if self.manager.previous_window:
                # Cambiar al foco a la ventana anterior
                win32gui.SetForegroundWindow(self.manager.previous_window)
                
                # Esperar un poco para asegurar que la ventana tiene el foco
                time.sleep(0.05)
                
                # Crear un objeto shell para enviar las teclas
                shell = win32com.client.Dispatch("WScript.Shell")
                
                # Enviar Ctrl+V para pegar
                shell.SendKeys("^v")
                
        except Exception as e:
            print(f"Error en el proceso de pegado: {e}")
    
    def hide_window(self, event=None):
        try:
            self.manager.root.attributes('-topmost', False)
            self.manager.root.withdraw()
            self.manager.is_visible = False
            self.restore_focus()
        except Exception as e:
            print(f"Error al ocultar la ventana: {e}")

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

    def check_window_state(self):
        try:
            actual_visible = self.manager.root.winfo_viewable()
            if actual_visible != self.manager.is_visible:
                print(f"Corrigiendo estado de visibilidad: {self.manager.is_visible} -> {actual_visible}")
                self.manager.is_visible = actual_visible
        except Exception as e:
            print(f"Error al verificar estado de la ventana: {e}")

    def update_active_window(self):
        self.manager.last_active_window = win32gui.GetForegroundWindow()

    @measure_time
    def show_window(self):
        try:
            self.manager.previous_window = win32gui.GetForegroundWindow()
            
            self.manager.root.deiconify()
            self.manager.root.geometry("+0+0") 
            self.manager.root.lift()  
            self.manager.root.attributes('-topmost', True)
            
            self.manager.is_visible = True
            
            self.initialize_focus()
        
            if not hasattr(self.manager, 'current_selection') or not self.manager.current_selection:
                self.manager.current_selection = {'type': 'card', 'index': 0}
            
            self.manager.root.focus_force()
            self.update_highlights()
            
        except Exception as e:
            print(f"Error al mostrar la ventana: {e}")

    def initialize_focus(self):
        try:
            # Iniciar la selección en la primera card si hay cards disponibles
            if len(self.manager.clipboard_items) > 0:
                self.manager.current_selection = {'type': 'card', 'index': 0}
            else:
                # Si no hay cards, iniciar en el primer botón principal
                self.manager.current_selection = {'type': 'button', 'index': 0}
            
            self.manager.root.focus_force()
            self.manager.root.update_idletasks()
            self.update_highlights()
            
        except Exception as e:
            print(f"Error al inicializar foco: {e}")

    def handle_focus(self, event=None):
        if self.manager.is_visible:
            self.manager.root.focus_force()

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
            
    def handle_global_key(self, key):
        if self.manager.is_visible:
            if key in ['Up', 'Down']:
                self.navigate_vertical(type('Event', (), {'keysym': key})())
            elif key in ['Left', 'Right']:
                self.navigate_horizontal(type('Event', (), {'keysym': key})())
            elif key == 'Return':
                self.activate_selected()
            self.manager.root.after(10, self.manager.root.update_idletasks)
            return 'break'  # Prevenir que el evento se propague
        return None

    def start_move(self, event):
        self.manager.x = event.x
        self.manager.y = event.y

    def on_move(self, event):
        dx = event.x - self.manager.x
        dy = event.y - self.manager.y
        x = self.manager.root.winfo_x() + dx
        y = self.manager.root.winfo_y() + dy
        self.manager.root.geometry("+{}+{}".format(x, y))
        self.manager.x = event.x
        self.manager.y = event.y

    def ensure_visible(self, widget):
        if widget is None:
            return
            
        try:
            bbox = self.manager.canvas.bbox("all")
            if bbox:
                widget_y = widget.winfo_y()
                canvas_height = self.manager.canvas.winfo_height()
                if widget_y > 0:
                    self.manager.canvas.yview_moveto(widget_y / bbox[3])
        except Exception as e:
            print(f"Error al asegurar visibilidad: {e}")

    @measure_time
    def update_highlights(self):
        self.clear_all_highlights()
        
        current_type = self.manager.current_selection['type']
        current_index = self.manager.current_selection['index']
        
        highlight_color = '#444444' if self.manager.is_dark_mode else '#cccccc'
        icon_highlight_color = '#666666' if self.manager.is_dark_mode else '#aaaaaa'
        
        try:
            if current_type == 'button':
                buttons = [self.manager.button1, self.manager.button2, self.manager.button3]
                if 0 <= current_index < len(buttons):
                    buttons[current_index].configure(bg=highlight_color)
            
            elif current_type == 'top_button':
                top_buttons = [self.manager.clear_button, self.manager.theme_button, self.manager.close_button]
                if 0 <= current_index < len(top_buttons):
                    top_buttons[current_index].configure(bg=highlight_color)
            
            elif current_type == 'card':
                cards = self.manager.cards_frame.winfo_children()
                if current_index < len(cards):
                    card = cards[current_index]
                    self.highlight_entire_card(card, highlight_color)
                    self.ensure_visible(card)
            
            elif current_type == 'icon':
                card_index = current_index // self.manager.icons_per_card
                icon_position = current_index % self.manager.icons_per_card
                cards = self.manager.cards_frame.winfo_children()
                
                if card_index < len(cards):
                    card = cards[card_index]
                    icons_frame = None
                    
                    for child in card.winfo_children():
                        if isinstance(child, tk.Frame) and child.winfo_children() and isinstance(child.winfo_children()[0], tk.Button):
                            icons_frame = child
                            break
                    
                    if icons_frame and icon_position < len(icons_frame.winfo_children()):
                        icons = icons_frame.winfo_children()
                        if 0 <= icon_position < len(icons):
                            icons[icon_position].configure(bg=icon_highlight_color)
                    self.ensure_visible(card)
                    
        except Exception as e:
            print(f"Error al actualizar highlights: {e}")
        
    def clear_all_highlights(self):
        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        base_color = theme['card_bg']
        
        buttons = [self.manager.button1, self.manager.button2, self.manager.button3,
                   self.manager.clear_button, self.manager.theme_button, self.manager.close_button]
        for button in buttons:
            button.configure(bg=theme['button_bg'])
        
        for card in self.manager.cards_frame.winfo_children():
            card.configure(bg=base_color)
            
            for child in card.winfo_children():
                child.configure(bg=base_color)
                if isinstance(child, tk.Frame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, (tk.Label, tk.Button)):
                            subchild.configure(bg=base_color)
                            
    def highlight_entire_card(self, card, color):
        card.configure(bg=color)
    
        text_frame = card.winfo_children()[0]  
        text_frame.configure(bg=color)
        for subwidget in text_frame.winfo_children():
            if isinstance(subwidget, tk.Label):
                subwidget.configure(bg=color)
        
        theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
        icons_frame = card.winfo_children()[-1]
        icons_frame.configure(bg=theme['card_bg'])
        for icon in icons_frame.winfo_children():
            icon.configure(bg=theme['card_bg'])