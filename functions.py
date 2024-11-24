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
from tkinter import ttk
from bs4 import BeautifulSoup
from utils import measure_time, process_text

# Definir CF_HTML ya que no está en win32con
CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

class Functions:
    def __init__(self, manager):
        self.manager = manager
        self.min_card_height = 40  # Altura mínima en píxeles (2 líneas + 2*2 padding)
        self.max_card_height = 76  # Altura máxima en píxeles (4 líneas + 2*2 padding)
        self.line_height = 18  # Altura estimada de una línea de texto


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
        
        # Usar los mismos colores de highlight que la navegación
        highlight_color = self.manager.navigation.current_strategy.state['highlight_colors'][
            'dark' if is_dark else 'light']['normal']
        icon_highlight_color = self.manager.navigation.current_strategy.state['highlight_colors'][
            'dark' if is_dark else 'light']['icon']

        card_container = tk.Frame(self.manager.cards_frame, width=card_width, height=card_height, bg=bg_color)
        card_container.pack(fill=tk.BOTH, padx=2, pady=2)
        card_container.pack_propagate(False)

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
            card_container.configure(bg=highlight_color)
            text_frame.configure(bg=highlight_color)
            text_label.configure(bg=highlight_color)
            icons_frame.configure(bg=highlight_color)
            for btn in [arrow_button, pin_button, delete_button]:
                btn.configure(bg=highlight_color)

        def on_leave(event):
            card_container.configure(bg=bg_color)
            text_frame.configure(bg=bg_color)
            text_label.configure(bg=bg_color)
            icons_frame.configure(bg=bg_color)
            for btn in [arrow_button, pin_button, delete_button]:
                btn.configure(bg=bg_color)

        # Funciones de hover para los iconos individuales
        def on_icon_enter(event, button):
            # Usar el color de highlight para iconos cuando el mouse está sobre ellos
            button.configure(bg=icon_highlight_color)

        def on_icon_leave(event, button):
            # Restaurar al color de highlight normal si la card está resaltada,
            # o al color base si no lo está
            parent_bg = icons_frame.cget('bg')
            button.configure(bg=parent_bg)

        # Vincular eventos hover para la card
        for widget in [card_container, text_frame, text_label, icons_frame]:
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
        self.manager.navigation.current_strategy.state['current_selection'] = {
            'type': 'cards',
            'index': index
        }
        self.manager.navigation.current_strategy.activate_selected()

    def activate_card_icon(self, card_index: int, icon_index: int) -> None:
        """Activa un icono específico de una tarjeta"""
        self.manager.navigation.current_strategy.state['current_selection'] = {
            'type': 'icons',
            'index': card_index * 3 + icon_index
        }
        self.manager.navigation.current_strategy.activate_selected()
        
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
        # Eliminar tarjetas obsoletas
        existing_cards = {child.item_id: child for child in self.manager.cards_frame.winfo_children() if hasattr(child, 'item_id')}
        
        for item_id in list(existing_cards.keys()):
            if item_id not in self.manager.clipboard_items:
                existing_cards[item_id].destroy()
                del existing_cards[item_id]

        # Actualizar o crear nuevas tarjetas
        for index, (item_id, item_data) in enumerate(self.manager.clipboard_items.items()):
            if item_id in existing_cards:
                card = existing_cards[item_id]
                self.update_card(card, item_data)
            else:
                card = self.create_card(item_id, item_data, index)
                card.item_id = item_id

            card.pack(fill=tk.X, padx=2, pady=2)

        # Actualizar la región de desplazamiento
        self.manager.canvas.update_idletasks()
        self.manager.canvas.configure(scrollregion=self.manager.canvas.bbox("all"))
        self.recalculate_card_heights()
        # Asegurarse de que el scroll esté en la parte superior después de actualizar
        self.manager.canvas.yview_moveto(0)
        

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
                    if isinstance(subchild, (tk.Label, tk.Button)):
                        subchild.configure(bg=theme['card_bg'], fg=theme['fg'])
            elif isinstance(child, (tk.Label, tk.Button)):
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
                    if clipboard_content['text'] not in [item['text'].get('text', '') if isinstance(item['text'], dict) else item['text'] for item in self.manager.clipboard_items.values()]:
                        new_id = str(uuid.uuid4())
                        new_item = {
                            'text': clipboard_content,
                            'pinned': False,
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

        self.manager.clipboard_items[new_id] = new_item
        if len(self.manager.clipboard_items) > 20:
            unpinned_items = [k for k, v in self.manager.clipboard_items.items() if not v['pinned']]
            if unpinned_items:
                del self.manager.clipboard_items[unpinned_items[-1]]
        self.refresh_cards()
        self.manager.group_manager.save_groups()

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
            elif CF_HTML in formats:
                html_data = win32clipboard.GetClipboardData(CF_HTML)
                format_info = self.extract_format_info_from_html(html_data)
            
            win32clipboard.CloseClipboard()
            
            if text:
                if format_info:
                    return {'text': text, 'formatted': format_info}
                else:
                    return text  # Retorna solo el texto si no hay información de formato
            return None
        except Exception as e:
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
        new_text = "Con formato" if self.manager.paste_with_format else "Sin formato"
        self.manager.button2.config(text=new_text)
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
            
        dialog.configure(bg=self.manager.theme_manager.colors['dark']['bg'])
        dialog.overrideredirect(True)
        dialog.attributes('-topmost', True)
        
        # Barra de título personalizada
        title_frame = tk.Frame(dialog, bg=dialog.cget('bg'))
        title_frame.pack(fill=tk.X, padx=5, pady=(0, 4))
        title_label = tk.Label(title_frame, text="Seleccionar Grupo", font=('Segoe UI', 10, 'bold'),
                            bg=dialog.cget('bg'), fg=self.manager.theme_manager.colors['dark']['fg'])
        title_label.pack(side=tk.LEFT, padx=5)
        
        # Configurar efecto hover para el botón de cerrar
        def create_close_button_hover():
            close_button = tk.Button(title_frame, text="❌", command=lambda: self.close_dialog(dialog),
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=10, width=5, height=2,
                                bg=self.manager.theme_manager.colors['dark']['button_bg'],
                                fg=self.manager.theme_manager.colors['dark']['button_fg'])
            close_button.pack(side=tk.RIGHT)
            
            def on_enter(e):
                close_button.configure(bg=self.manager.navigation.current_strategy.state['highlight_colors'][
                    'dark' if self.manager.is_dark_mode else 'light']['normal'])
            
            def on_leave(e):
                close_button.configure(bg=self.manager.theme_manager.colors['dark']['button_bg'])
            
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
                                bg=self.manager.theme_manager.colors['dark']['card_bg'])
            message_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=20)
            
            message_label = tk.Label(message_frame, 
                                text='No hay grupos creados.\nCrea un nuevo grupo en la pantalla de grupos.',
                                font=('Segoe UI', 10),
                                bg=self.manager.theme_manager.colors['dark']['card_bg'],
                                fg=self.manager.theme_manager.colors['dark']['fg'],
                                justify=tk.CENTER)
            message_label.pack(expand=True)
        else:
            # Crear botones para cada grupo con efecto hover
            for group_id, group_info in self.manager.group_manager.groups.items():
                group_button = tk.Button(content_frame, text=group_info['name'],
                                    command=lambda gid=group_id: self.add_to_group(item_id, gid, dialog),
                                    bg=self.manager.theme_manager.colors['dark']['button_bg'],
                                    fg=self.manager.theme_manager.colors['dark']['button_fg'],
                                    activebackground=self.manager.theme_manager.colors['dark']['active_bg'],
                                    activeforeground=self.manager.theme_manager.colors['dark']['active_fg'],
                                    bd=0, padx=10, pady=5, width=30, anchor='w')
                group_button.pack(fill=tk.X, pady=2)
                
                # Configurar hover para los botones de grupo
                def create_hover_effect(button):
                    def on_enter(e):
                        button.configure(bg=self.manager.navigation.current_strategy.state['highlight_colors'][
                            'dark' if self.manager.is_dark_mode else 'light']['normal'])
                    
                    def on_leave(e):
                        button.configure(bg=self.manager.theme_manager.colors['dark']['button_bg'])
                    
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
