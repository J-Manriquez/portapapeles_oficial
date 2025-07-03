# functions.py

import base64
import re
import tkinter as tk
import uuid
import win32con # type: ignore
import win32clipboard # type: ignore
import win32gui # type: ignore
import time
import sys
import os
from tkinter import ttk
from bs4 import BeautifulSoup # type: ignore
from utils import measure_time, process_text

# Importaciones para emojis coloridos
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Definir CF_HTML ya que no está en win32con
CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

class Functions:
    def __init__(self, manager):
        self.manager = manager
        self.min_card_height = 40  # Altura mínima en píxeles (2 líneas + 2*2 padding)
        self.max_card_height = 76  # Altura máxima en píxeles (4 líneas + 2*2 padding)
        self.line_height = 18  # Altura estimada de una línea de texto
        self._emoji_cache = {}  # Cache para imágenes de emojis
        
    def create_colored_emoji_image(self, emoji_text, size=16, bg_color=None):
        """Crea una imagen colorida del emoji usando PIL si está disponible"""
        if not PIL_AVAILABLE:
            return None
            
        # Crear clave de cache
        cache_key = f"{emoji_text}_{size}_{bg_color}"
        if cache_key in self._emoji_cache:
            return self._emoji_cache[cache_key]
            
        try:
            # Buscar la fuente de emoji de Windows
            font_paths = [
                "C:/Windows/Fonts/seguiemj.ttf",  # Windows 10/11
                "C:/Windows/Fonts/segoe-ui-emoji.ttf",  # Alternativo
                "seguiemj.ttf"  # En el directorio actual
            ]
            
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, size)
                        break
                    except Exception:
                        continue
                        
            if font is None:
                # Fallback a fuente por defecto
                font = ImageFont.load_default()
                
            # Crear imagen con transparencia
            img_size = size + 4  # Añadir padding
            if bg_color:
                # Convertir color hex a RGB si es necesario
                if isinstance(bg_color, str) and bg_color.startswith('#'):
                    bg_color = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                img = Image.new("RGBA", (img_size, img_size), bg_color + (255,))
            else:
                img = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
                
            draw = ImageDraw.Draw(img)
            
            # Dibujar el emoji con colores embebidos
            draw.text(
                (img_size/2, img_size/2), 
                emoji_text, 
                font=font, 
                anchor="mm",
                embedded_color=True  # Esto es clave para mostrar colores
            )
            
            # Convertir a PhotoImage para Tkinter
            photo_image = ImageTk.PhotoImage(img)
            
            # Guardar en cache
            self._emoji_cache[cache_key] = photo_image
            
            return photo_image
            
        except Exception as e:
            print(f"Error creando emoji colorido: {e}")
            return None


    @measure_time
    def create_card(self, item_id, item_data, index):
        card_width = self.manager.window_width - 4  # Ajuste para el padding
        card_height = max(self.min_card_height, self.calculate_card_height(item_data['text']))

        # Procesamos el texto para mostrarlo de forma limpia
        if isinstance(item_data['text'], dict):
            processed_text = process_text(item_data['text'].get('text', ''), 3)
        else:
            processed_text = process_text(str(item_data['text']), 3)

        # Obtener colores del tema actual
        is_dark = self.manager.is_dark_mode
        theme = self.manager.theme_manager.colors['dark' if is_dark else 'light']
        bg_color = theme['card_bg']

        # Usar los mismos colores de highlight que la navegación si está disponible
        if (hasattr(self.manager, 'navigation') and 
            hasattr(self.manager.navigation, 'current_strategy') and 
            self.manager.navigation.current_strategy is not None and
            hasattr(self.manager.navigation.current_strategy, 'state')):
            highlight_color = self.manager.navigation.current_strategy.state['highlight_colors'][
                'dark' if is_dark else 'light']['normal']
            icon_highlight_color = self.manager.navigation.current_strategy.state['highlight_colors'][
                'dark' if is_dark else 'light']['icon']
        else:
            # Usar colores por defecto del tema
            highlight_color = theme.get('highlight_bg', theme['button_bg'])
            icon_highlight_color = theme.get('highlight_fg', theme['button_fg'])

        card_container = tk.Frame(self.manager.cards_frame, width=card_width, height=card_height, bg=bg_color)
        card_container.pack(fill=tk.BOTH, padx=2, pady=2)
        card_container.pack_propagate(False)

        # Añadir indicador de formato si el elemento tiene formato y está habilitado (lado izquierdo)
        has_format = item_data.get('has_format', False)
        show_format_icon = self.manager.settings.get('show_format_icon', True)
        format_indicator = None
        if has_format and show_format_icon:
            # Intentar crear emoji colorido primero
            emoji_image = self.create_colored_emoji_image("🎨", size=16, bg_color=bg_color)
            
            if emoji_image:
                # Usar imagen colorida del emoji
                format_indicator = tk.Label(card_container, image=emoji_image, bg=bg_color)
                format_indicator.image = emoji_image  # Mantener referencia
            else:
                # Fallback al texto normal si PIL no está disponible
                format_indicator = tk.Label(card_container, text="🎨", 
                                          font=('Segoe UI Emoji', 10), bg=bg_color)
            format_indicator.pack(side=tk.LEFT, padx=(2, 0))

        text_frame = tk.Frame(card_container, bg=bg_color)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        processed_text = process_text(item_data['text'], 3)

        text_label = tk.Label(text_frame, text=processed_text,
                            justify=tk.LEFT, anchor='w', padx=10, pady=5,
                            bg=bg_color,
                            fg=theme['fg'], width=int(24))
        text_label.pack(fill=tk.X, expand=True, side=tk.LEFT)

        # El contenedor de iconos ahora usa el mismo color de fondo que la card
        icons_frame = tk.Frame(card_container, bg=bg_color)
        icons_frame.pack(side=tk.RIGHT, padx=3)

        # Crear botones con los colores del tema
        arrow_button = tk.Button(icons_frame, text="➡️",
                                command=lambda: self.show_select_group_screen(item_id),
                                font=('Segoe UI', 10), bd=0,
                                padx=2, bg=bg_color, fg=theme['fg'])
        arrow_button.pack(side=tk.LEFT)

        pin_text = "📌" if item_data['pinned'] else "📍"
        pin_button = tk.Button(icons_frame, text=pin_text,
                            command=lambda: self.toggle_pin(item_id),
                            font=('Segoe UI', 10), bd=0,
                            padx=2, bg=bg_color, fg=theme['fg'])
        pin_button.pack(side=tk.LEFT)

        delete_button = tk.Button(icons_frame, text="✖️",
                                command=lambda: self.delete_item(item_id),
                                font=('Segoe UI', 10), bd=0,
                                padx=2, bg=bg_color, fg=theme['fg'])
        delete_button.pack(side=tk.LEFT)

        # Funciones de hover
        def on_enter(event):
            try:
                if card_container.winfo_exists():
                    card_container.configure(bg=highlight_color)
                    if text_frame.winfo_exists():
                        text_frame.configure(bg=highlight_color)
                    if text_label.winfo_exists():
                        text_label.configure(bg=highlight_color)
                    if icons_frame.winfo_exists():
                        icons_frame.configure(bg=highlight_color)
                    # Incluir indicador de formato en hover si existe
                    if format_indicator and format_indicator.winfo_exists():
                        # Si es una imagen, recrear con el nuevo color de fondo
                        if hasattr(format_indicator, 'image') and format_indicator.image:
                            new_emoji_image = self.create_colored_emoji_image("🎨", size=16, bg_color=highlight_color)
                            if new_emoji_image:
                                format_indicator.configure(image=new_emoji_image, bg=highlight_color)
                                format_indicator.image = new_emoji_image
                            else:
                                format_indicator.configure(bg=highlight_color)
                        else:
                            format_indicator.configure(bg=highlight_color)
                    for btn in [arrow_button, pin_button, delete_button]:
                        if btn.winfo_exists():
                            btn.configure(bg=highlight_color)
            except tk.TclError:
                # Widget ya no existe, ignorar
                pass

        def on_leave(event):
            try:
                if card_container.winfo_exists():
                    card_container.configure(bg=bg_color)
                    if text_frame.winfo_exists():
                        text_frame.configure(bg=bg_color)
                    if text_label.winfo_exists():
                        text_label.configure(bg=bg_color)
                    if icons_frame.winfo_exists():
                        icons_frame.configure(bg=bg_color)
                    # Restaurar color del indicador de formato si existe
                    if format_indicator and format_indicator.winfo_exists():
                        # Si es una imagen, recrear con el color de fondo original
                        if hasattr(format_indicator, 'image') and format_indicator.image:
                            new_emoji_image = self.create_colored_emoji_image("🎨", size=16, bg_color=bg_color)
                            if new_emoji_image:
                                format_indicator.configure(image=new_emoji_image, bg=bg_color)
                                format_indicator.image = new_emoji_image
                            else:
                                format_indicator.configure(bg=bg_color)
                        else:
                            format_indicator.configure(bg=bg_color)
                    for btn in [arrow_button, pin_button, delete_button]:
                        if btn.winfo_exists():
                            btn.configure(bg=bg_color)
            except tk.TclError:
                # Widget ya no existe, ignorar
                pass

        # Funciones de hover para los iconos individuales
        def on_icon_enter(event, button):
            if button.winfo_exists():
                # Usar el color de highlight para iconos cuando el mouse está sobre ellos
                button.configure(bg=icon_highlight_color)

        def on_icon_leave(event, button):
            if button.winfo_exists():
                # Restaurar al color de highlight normal si la card está resaltada,
                # o al color base si no lo está
                parent_bg = icons_frame.cget('bg')
                button.configure(bg=parent_bg)

        # Vincular eventos hover para la card
        widgets_to_bind = [card_container, text_frame, text_label, icons_frame]
        if format_indicator:
            widgets_to_bind.append(format_indicator)
        for widget in widgets_to_bind:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)

        # Vincular eventos hover para los iconos individuales
        for btn in [arrow_button, pin_button, delete_button]:
            btn.bind('<Enter>', lambda e, b=btn: on_icon_enter(e, b))
            btn.bind('<Leave>', lambda e, b=btn: on_icon_leave(e, b))

        # Agregar bindings para la tarjeta completa
        card_container.bind('<Button-1>', lambda e: self.activate_card(index))
        text_label.bind('<Button-1>', lambda e: self.activate_card(index))

        # Configurar bindings para los iconos
        arrow_button.bind('<Button-1>', lambda e: self.activate_card_icon(index, 0))
        pin_button.bind('<Button-1>', lambda e: self.activate_card_icon(index, 1))
        delete_button.bind('<Button-1>', lambda e: self.activate_card_icon(index, 2))

        return card_container

    def activate_card(self, index: int) -> None:
        """Activa una tarjeta específica"""
        nav = self.manager.navigation.current_strategy
        if nav and hasattr(nav, 'state'):
            nav.state['current_selection'] = {
                'type': 'cards',
                'index': index
            }
            if hasattr(nav, 'activate_selected'):
                nav.activate_selected()

    def activate_card_icon(self, card_index: int, icon_index: int) -> None:
        """Activa un icono específico de una tarjeta"""
        nav = self.manager.navigation.current_strategy
        if nav and hasattr(nav, 'state'):
            nav.state['current_selection'] = {
                'type': 'icons',
                'index': card_index * 3 + icon_index
            }
            if hasattr(nav, 'activate_selected'):
                nav.activate_selected()

    def calculate_card_height(self, text_data):
        if isinstance(text_data, dict):
            text = text_data.get('text', '')
        else:
            text = str(text_data)
        lines = len(text.split('\n'))
        content_height = min(lines * self.line_height, 4 * self.line_height)  # Máximo 4 líneas
        return min(max(content_height + 4, self.min_card_height), self.max_card_height)

    @measure_time
    def refresh_cards(self):
        if not hasattr(self.manager, 'cards_frame') or not self.manager.cards_frame.winfo_exists():
            print("cards_frame no existe o ha sido destruido")
            return

        # Resetear estados de navegación si están disponibles
        if (hasattr(self.manager, 'navigation') and 
            hasattr(self.manager.navigation, 'current_strategy') and 
            self.manager.navigation.current_strategy is not None):
            self.manager.navigation.current_strategy.last_keyboard_selection = None

        # Limpiar todas las tarjetas existentes
        for widget in self.manager.cards_frame.winfo_children():
            widget.destroy()

        # Crear nuevas tarjetas en el orden actual del diccionario
        for index, (item_id, item_data) in enumerate(self.manager.clipboard_items.items()):
            card = self.create_card(item_id, item_data, index)
            card.item_id = item_id
            card.pack(fill=tk.X, padx=2, pady=2)

        # Actualizar la región de desplazamiento
        self.manager.canvas.update_idletasks()
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))
        self.recalculate_card_heights()

        # Asegurarse de que el scroll esté en la parte superior después de actualizar
        self.manager.canvas.yview_moveto(0)

        # Actualizar highlights solo si la navegación está inicializada
        if (hasattr(self.manager, 'navigation') and 
            hasattr(self.manager.navigation, 'current_strategy') and 
            self.manager.navigation.current_strategy is not None):
            self.manager.navigation.update_highlights()

    def update_card(self, card, item_data):
        processed_text = process_text(item_data['text'], 3)
        text_label = card.winfo_children()[0].winfo_children()[0]
        text_label.config(text=processed_text)

        new_height = self.calculate_card_height(processed_text)
        card.config(height=new_height)

        # Actualizar el estado del botón de pin
        pin_button = card.winfo_children()[1].winfo_children()[1]
        pin_text = "📌" if item_data['pinned'] else "📍"
        pin_button.config(text=pin_text)

    def apply_theme_to_card(self, card, theme):
        card.configure(bg=theme['card_bg'])

        for child in card.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=theme['card_bg'])
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        # No aplicar color de texto al emoji de formato
                        if hasattr(subchild, 'image') and subchild.image:
                            # Es un emoji como imagen
                            new_emoji_image = self.create_colored_emoji_image("🎨", size=16, bg_color=theme['card_bg'])
                            if new_emoji_image:
                                subchild.configure(image=new_emoji_image, bg=theme['card_bg'])
                                subchild.image = new_emoji_image
                            else:
                                subchild.configure(bg=theme['card_bg'])
                        elif subchild.cget('text') == '🎨':
                            subchild.configure(bg=theme['card_bg'])
                        else:
                            subchild.configure(bg=theme['card_bg'], fg=theme['fg'])
                    elif isinstance(subchild, tk.Button):
                        subchild.configure(bg=theme['card_bg'], fg=theme['fg'])
            elif isinstance(child, tk.Label):
                # No aplicar color de texto al emoji de formato
                if hasattr(child, 'image') and child.image:
                    # Es un emoji como imagen
                    new_emoji_image = self.create_colored_emoji_image("🎨", size=16, bg_color=theme['card_bg'])
                    if new_emoji_image:
                        child.configure(image=new_emoji_image, bg=theme['card_bg'])
                        child.image = new_emoji_image
                    else:
                        child.configure(bg=theme['card_bg'])
                elif child.cget('text') == '🎨':
                    child.configure(bg=theme['card_bg'])
                else:
                    child.configure(bg=theme['card_bg'], fg=theme['fg'])
            elif isinstance(child, tk.Button):
                child.configure(bg=theme['card_bg'], fg=theme['fg'])

    def toggle_pin(self, item_id):
        if item_id in self.manager.clipboard_items:
            # Actualizar el estado de anclaje
            self.manager.clipboard_items[item_id]['pinned'] = not self.manager.clipboard_items[item_id]['pinned']
            # Actualizar la interfaz
            self.refresh_cards()
            # Guardar los cambios inmediatamente
            self.manager.data_manager.save_data(
                self.manager.group_manager.groups,
                self.manager.clipboard_items,
                self.manager.settings
            )
    def delete_item(self, item_id):
        if item_id in self.manager.clipboard_items and not self.manager.clipboard_items[item_id]['pinned']:
            del self.manager.clipboard_items[item_id]
            self.refresh_cards()
            self.manager.group_manager.save_groups()  # Guardar después de eliminar un item


    def clear_history(self):
        self.manager.clipboard_items = {k: v for k, v in self.manager.clipboard_items.items() if v['pinned']}
        self.refresh_cards()
        self.manager.group_manager.save_groups()  # Guardar después de limpiar el historial
        if self.manager.current_selection['type'] == 'card':
            self.manager.current_selection = {'type': 'button', 'index': 0}
        self.manager.navigation.update_highlights()

    def on_canvas_configure(self, event):
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.manager.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    @measure_time
    def monitor_clipboard(self):
        while True:
            try:
                clipboard_content = self.get_clipboard_text()
                if clipboard_content and clipboard_content != self.manager.current_clipboard:
                    self.manager.current_clipboard = clipboard_content
                    # Verificar si el texto ya existe en los elementos guardados
                    text_to_check = clipboard_content['text']
                    existing_texts = []
                    for item in self.manager.clipboard_items.values():
                        if isinstance(item['text'], dict):
                            existing_texts.append(item['text'].get('text', ''))
                        else:
                            existing_texts.append(str(item['text']))
                    
                    if text_to_check not in existing_texts:
                        new_id = str(uuid.uuid4())
                        # Preservar siempre el formato completo cuando esté disponible
                        has_format = clipboard_content.get('formatted', {}) and any(clipboard_content['formatted'].values())
                        new_item = {
                            'text': clipboard_content,  # Mantener estructura completa con formato
                            'pinned': False,
                            'has_format': has_format,  # Indicador de si tiene formato
                            'with_format': self.manager.paste_with_format
                        }
                        # Usar after para actualizar la GUI en el hilo principal
                        self.manager.root.after(0, self.add_clipboard_item, new_id, new_item)
            except Exception as e:
                print(f"Error en monitor_clipboard: {e}")
            time.sleep(0.5)

    def add_clipboard_item(self, new_id, new_item):
        # Asegúrate de que new_item['text'] siempre sea un diccionario
        if isinstance(new_item['text'], str):
            new_item['text'] = {'text': new_item['text'], 'formatted': {}}
        elif not isinstance(new_item['text'], dict):
            new_item['text'] = {'text': str(new_item['text']), 'formatted': {}}

        # Crear un nuevo diccionario ordenado con el nuevo item al principio
        new_items = {new_id: new_item}
        new_items.update(self.manager.clipboard_items)
        self.manager.clipboard_items = new_items

        # Verificar límite usando el valor de configuración
        max_items = self.manager.settings.get('max_items', 20)
        while len(self.manager.clipboard_items) > max_items:
            # Encontrar el último item no fijado
            unpinned_items = [(k, v) for k, v in self.manager.clipboard_items.items() if not v['pinned']]
            if unpinned_items:
                del self.manager.clipboard_items[unpinned_items[-1][0]]
            else:
                break  # Si no hay items sin fijar, salir del bucle

        # Usar inserción eficiente en lugar de refresh completo
        self.insert_new_card_efficiently(new_id, new_item)
        self.manager.group_manager.save_groups()

    def insert_new_card_efficiently(self, new_id, new_item):
        """Inserta una nueva card de manera eficiente sin recargar todas las cards"""
        try:
            # Verificar que cards_frame existe
            if not hasattr(self.manager, 'cards_frame') or self.manager.cards_frame is None:
                # Si no existe cards_frame, usar refresh_cards como fallback
                self.refresh_cards()
                return

            # Verificar que navigation está inicializado
            if (not hasattr(self.manager, 'navigation') or 
                self.manager.navigation is None or 
                not hasattr(self.manager.navigation, 'current_strategy') or 
                self.manager.navigation.current_strategy is None):
                # Si navigation no está inicializado, usar refresh_cards como fallback
                self.refresh_cards()
                return

            # Crear la nueva card en la parte superior
            card_frame = self.create_card(new_id, new_item, 0)
            
            # Mover la nueva card al principio de la lista
            card_frame.pack_forget()
            card_frame.pack(fill=tk.BOTH, padx=2, pady=2, before=self.manager.cards_frame.winfo_children()[0] if self.manager.cards_frame.winfo_children() else None)
            
            # Aplicar efecto de entrada suave
            self.apply_smooth_entry_effect(card_frame)
            
            # Actualizar la región de scroll
            self.manager.root.after(50, self.update_scroll_region)
            
            # Actualizar highlights si navigation está disponible
            if (hasattr(self.manager, 'navigation') and 
                self.manager.navigation and 
                hasattr(self.manager.navigation, 'current_strategy') and 
                self.manager.navigation.current_strategy):
                self.manager.root.after(100, self.manager.navigation.update_highlights)
                
        except Exception as e:
            print(f"Error en insert_new_card_efficiently: {e}")
            # En caso de error, usar refresh_cards como fallback
            self.refresh_cards()

    def apply_smooth_entry_effect(self, card_frame):
        """Aplica un efecto suave de entrada a una nueva card"""
        try:
            # Efecto de fade-in y scale suave
            original_bg = card_frame.cget('bg')
            
            # Iniciar con transparencia simulada (color más claro)
            light_bg = self.lighten_color(original_bg, 0.3)
            card_frame.configure(bg=light_bg)
            
            # Animar hacia el color original
            steps = 10
            
            def animate_fade(step):
                if step < steps:
                    # Interpolar entre el color claro y el original
                    alpha = step / steps
                    interpolated_color = self.interpolate_color(light_bg, original_bg, alpha)
                    try:
                        card_frame.configure(bg=interpolated_color)
                        # También aplicar a los elementos hijos
                        for child in card_frame.winfo_children():
                            if hasattr(child, 'configure'):
                                child.configure(bg=interpolated_color)
                    except tk.TclError:
                        pass
                    self.manager.root.after(30, lambda: animate_fade(step + 1))
                else:
                    try:
                        card_frame.configure(bg=original_bg)
                        # Restaurar colores originales de los hijos
                        for child in card_frame.winfo_children():
                            if hasattr(child, 'configure'):
                                child.configure(bg=original_bg)
                    except tk.TclError:
                        pass
                        
            animate_fade(0)
        except Exception as e:
            print(f"Error en apply_smooth_entry_effect: {e}")

    def lighten_color(self, color, factor):
        """Aclara un color por un factor dado"""
        try:
            # Convertir color hex a RGB
            if color.startswith('#'):
                color = color[1:]
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # Aclarar cada componente
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color  # Retornar color original si hay error

    def interpolate_color(self, color1, color2, alpha):
        """Interpola entre dos colores"""
        try:
            # Convertir colores hex a RGB
            def hex_to_rgb(color):
                if color.startswith('#'):
                    color = color[1:]
                return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            # Interpolar cada componente
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * alpha)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * alpha)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * alpha)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color2  # Retornar color final si hay error

    def update_scroll_region(self):
        """Actualiza la región de scroll después de añadir una nueva card"""
        try:
            if hasattr(self.manager, 'canvas') and self.manager.canvas:
                self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))
        except Exception as e:
            print(f"Error en update_scroll_region: {e}")

    # @measure_time
    def get_clipboard_text(self):
        try:
            win32clipboard.OpenClipboard()
            formats = []
            format_id = win32clipboard.EnumClipboardFormats(0)
            while format_id:
                formats.append(format_id)
                format_id = win32clipboard.EnumClipboardFormats(format_id)

            text = None
            format_info = {}

            if win32con.CF_UNICODETEXT in formats:
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)

            if win32con.CF_RTF in formats:
                rtf_data = win32clipboard.GetClipboardData(win32con.CF_RTF)
                format_info = self.extract_format_info_from_rtf(rtf_data)
                format_info['rtf_content'] = rtf_data  # Preservar contenido RTF original
            elif CF_HTML in formats:
                html_data = win32clipboard.GetClipboardData(CF_HTML)
                format_info = self.extract_format_info_from_html(html_data)
                format_info['html_content'] = html_data  # Preservar contenido HTML original

            win32clipboard.CloseClipboard()

            if text and text.strip():  # Verificar que el texto no esté vacío
                if format_info:
                    return {'text': text, 'formatted': format_info}
                else:
                    return {'text': text, 'formatted': {}}  # Siempre retornar formato consistente
            return None
        except Exception as e:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass  # Ignorar errores al cerrar si ya está cerrado
            print(f"Error al obtener texto del portapapeles: {e}")
            return None

    def extract_format_info_from_rtf(self, rtf_data):
        format_info = {'rtf': True}

        # Extraer información de fuente
        font_match = re.search(r'\\fonttbl.*?{\\f0\\fnil (.*?);}', rtf_data)
        if font_match:
            format_info['font'] = font_match.group(1)

        # Extraer información de tamaño
        size_match = re.search(r'\\fs(\d+)', rtf_data)
        if size_match:
            format_info['size'] = int(size_match.group(1)) / 2  # RTF usa el doble del tamaño real

        # Extraer información de color
        color_match = re.search(r'\\red(\d+)\\green(\d+)\\blue(\d+)', rtf_data)
        if color_match:
            format_info['color'] = (int(color_match.group(1)), int(color_match.group(2)), int(color_match.group(3)))

        # Extraer información de negrita e itálica
        format_info['bold'] = r'\b' in rtf_data
        format_info['italic'] = r'\i' in rtf_data

        return format_info

    def extract_format_info_from_html(self, html_data):
        format_info = {'html': True}
        soup = BeautifulSoup(html_data, 'html.parser')

        # Buscar el primer elemento con estilo
        styled_element = soup.find(style=True)
        if styled_element:
            style = styled_element['style']

            # Extraer información de fuente
            font_match = re.search(r'font-family:\s*(.*?);', style)
            if font_match:
                format_info['font'] = font_match.group(1)

            # Extraer información de tamaño
            size_match = re.search(r'font-size:\s*(\d+)pt', style)
            if size_match:
                format_info['size'] = int(size_match.group(1))

            # Extraer información de color
            color_match = re.search(r'color:\s*rgb\((\d+),\s*(\d+),\s*(\d+)\)', style)
            if color_match:
                format_info['color'] = (int(color_match.group(1)), int(color_match.group(2)), int(color_match.group(3)))

        # Extraer información de negrita e itálica
        format_info['bold'] = bool(soup.find(['strong', 'b']))
        format_info['italic'] = bool(soup.find(['em', 'i']))

        return format_info

    def exit_app(self):
        self.manager.root.quit()
        sys.exit()

    @measure_time
    def toggle_paste_format(self):
        self.manager.paste_with_format = not self.manager.paste_with_format
        # Mostrar estado actual con icono de refresh
        status_text = "Con formato" if self.manager.paste_with_format else "Sin formato"
        button_text = f"{status_text} 🔄"
        self.manager.button2.config(text=button_text)
        self.manager.navigation.update_highlights()

    @measure_time
    def recalculate_card_heights(self):
        for card in self.manager.cards_frame.winfo_children():
            if hasattr(card, 'item_id'):
                item_data = self.manager.clipboard_items[card.item_id]
                new_height = self.calculate_card_height(item_data['text'])
                card.config(height=new_height)

        self.manager.canvas.update_idletasks()
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))

    def show_select_group_screen(self, item_id):
        """Muestra la pantalla de selección de grupo"""
        self.root.withdraw()  # Ocultar ventana principal

        def after_dialog_shown():
            if hasattr(self, 'select_group_dialog'):
                self.select_group_dialog.focus_force()
                self.navigation.set_strategy('select_group')
                self.select_group_screen_keys.activate()
                self.navigation.initialize_focus()

        # Mostrar el diálogo de selección de grupo
        self.functions.on_arrow_click(item_id)

        # Asegurar que el foco se mantenga después de mostrar la ventana
        self.root.after(100, after_dialog_shown)

    def on_arrow_click(self, item_id):
        self.select_group(item_id)

        # Asegurarse de que el diálogo se ha creado correctamente
        if hasattr(self.manager, 'select_group_dialog') and self.manager.select_group_dialog.winfo_exists():
            dialog = self.manager.select_group_dialog

            # Vincular eventos de teclado
            dialog.bind('<Key>', self.manager.key_handler.handle_key_press)
            dialog.focus_force()
            dialog.grab_set()

            # Configurar la navegación
            self.manager.navigation.set_strategy('select_group')
            self.manager.select_group_screen_keys.activate()

            # Inicializar el foco y los highlights después de que la ventana sea visible
            self.manager.root.after(100, lambda: self.manager.navigation.initialize_focus())

    def select_group(self, item_id):
        # Ocultar la ventana principal
        self.manager.root.withdraw()
        dialog = tk.Toplevel(self.manager.root)
        self.manager.select_group_dialog = dialog  # Guarda una referencia al diálogo

        dialog.title("Seleccionar Grupo")

        window_width = self.manager.settings['width']
        window_height = self.manager.settings['height']

        x = self.manager.window_x
        y = self.manager.window_y

        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

        dialog.configure(bg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)

        # Barra de título personalizada
        title_frame = tk.Frame(dialog, bg=dialog.cget('bg'))
        title_frame.pack(fill=tk.X, padx=5, pady=(0, 4))
        title_label = tk.Label(title_frame, text="Seleccionar Grupo", font=('Segoe UI', 10, 'bold'),
                            bg=dialog.cget('bg'), fg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['fg'])
        title_label.pack(side=tk.LEFT, padx=5)

        # Configurar efecto hover para el botón de cerrar
        def create_close_button_hover():
            close_button = tk.Button(title_frame, text="❌", command=lambda: self.close_dialog(dialog),
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2,
                                bg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['button_bg'],
                        fg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['button_fg'])
            close_button.pack(side=tk.RIGHT)

            def on_enter(e):
                nav = self.manager.navigation.current_strategy
                if nav and hasattr(nav, 'state') and 'highlight_colors' in nav.state:
                    close_button.configure(bg=nav.state['highlight_colors'][
                        'dark' if self.manager.is_dark_mode else 'light']['normal'])
                else:
                    # Fallback color
                    close_button.configure(bg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['hover_bg'])

            def on_leave(e):
                close_button.configure(bg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['button_bg'])

            close_button.bind('<Enter>', on_enter)
            close_button.bind('<Leave>', on_leave)

        create_close_button_hover()

        # Canvas para scroll y contenedor de grupos
        canvas = tk.Canvas(dialog, bg=dialog.cget('bg'), bd=0, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=0)
        # Scrollbar
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        # Frame contenedor dentro del canvas para el scroll
        content_frame = tk.Frame(canvas, bg=dialog.cget('bg'))
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor='nw', width=295)

        # Mostrar mensaje cuando no hay grupos
        if not self.manager.group_manager.groups:
            message_frame = tk.Frame(content_frame,
                                bg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['card_bg'])
            message_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=20)

            message_label = tk.Label(message_frame,
                                text='No hay grupos creados.\nCrea un nuevo grupo en la pantalla de grupos.',
                                font=('Segoe UI', 10),
                                bg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['card_bg'],
                            fg=self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']['fg'],
                                justify=tk.CENTER)
            message_label.pack(expand=True)
        else:
            # Crear botones para cada grupo con efecto hover
            for group_id, group_info in self.manager.group_manager.groups.items():
                # Obtener colores del tema actual
                current_theme = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
                
                group_button = tk.Button(content_frame, text=group_info['name'],
                                    command=lambda gid=group_id: self.add_to_group(item_id, gid, dialog),
                                    bg=current_theme['button_bg'],
                                    fg=current_theme['button_fg'],
                                    activebackground=current_theme['active_bg'],
                                    activeforeground=current_theme['active_fg'],
                                    bd=0, padx=10, pady=5, width=30, anchor='w')
                group_button.pack(fill=tk.X, pady=2)

                # Configurar hover para los botones de grupo
                def create_hover_effect(button):
                    def on_enter(e):
                        # Obtener colores del tema actual dinámicamente
                        current_theme_hover = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
                        button.configure(bg=current_theme_hover['active_bg'])

                    def on_leave(e):
                        # Obtener colores del tema actual dinámicamente
                        current_theme_leave = self.manager.theme_manager.colors['dark' if self.manager.is_dark_mode else 'light']
                        button.configure(bg=current_theme_leave['button_bg'])

                    button.bind('<Enter>', on_enter)
                    button.bind('<Leave>', on_leave)

                create_hover_effect(group_button)

        # Ajustar el ancho del frame contenedor al canvas
        def on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_resize)
        # Configuración de scroll
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content_frame.bind("<Configure>", on_frame_configure)
        # Función para desplazamiento con la rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Hacer la ventana arrastrable
        def start_move(event):
            dialog.x = event.x
            dialog.y = event.y
        def on_move(event):
            deltax = event.x - dialog.x
            deltay = event.y - dialog.y
            x = dialog.winfo_x() + deltax
            y = dialog.winfo_y() + deltay
            dialog.geometry(f"+{x}+{y}")
        title_frame.bind('<Button-1>', start_move)
        title_frame.bind('<B1-Motion>', on_move)

        # Configurar la navegación para la pantalla de selección de grupo
        self.manager.navigation.set_strategy('select_group')
        self.manager.select_group_screen_keys.activate()

        dialog.focus_force()  # Forzar el foco en la ventana de diálogo
        dialog.grab_set()     # Hacer que la ventana sea modal

        # Asegurarse de que el foco se mantenga después de mostrar la ventana
        self.manager.root.after(100, dialog.focus_force)

        # Actualizar la navegación después de que la ventana esté visible
        self.manager.root.after(200, lambda: self.manager.navigation.initialize_focus())

        # # Inicializar el foco y los highlights
        # self.manager.navigation.initialize_focus()

    def close_dialog(self, dialog):
        """Cierra el diálogo y restaura el foco en la pantalla principal"""
        dialog.destroy()
        self.manager.show_main_screen()

        # Asegurar que el foco vuelva a la pantalla principal
        def restore_main_focus():
            self.manager.root.focus_force()
            self.manager.navigation.set_strategy('main')
            self.manager.main_screen_keys.activate()
            self.manager.select_group_screen_keys.deactivate()
            self.manager.navigation.initialize_focus()
            self.manager.navigation.update_highlights()

        # Dar tiempo a que la ventana principal se muestre
        self.manager.root.after(100, restore_main_focus)

    def add_to_group(self, item_id, group_id, dialog):
        self.manager.group_manager.add_item_to_group(item_id, group_id)
        dialog.destroy()
        self.manager.root.deiconify()
        self.manager.navigation.set_strategy('main')  # Volver a la estrategia de navegación principal
        if hasattr(self.manager, 'select_group_dialog'):
            delattr(self.manager, 'select_group_dialog')
