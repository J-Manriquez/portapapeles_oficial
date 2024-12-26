import json
import os
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, file_path=None):
        # Obtener la ruta del directorio AppData
        appdata_path = os.path.join(os.environ['APPDATA'], 'ClipboardManager')

        # Crear el directorio si no existe
        if not os.path.exists(appdata_path):
            try:
                os.makedirs(appdata_path)
            except Exception as e:
                logger.error(f"Error creating directory: {e}")

        # Si no se proporciona una ruta, usar la ruta por defecto en AppData
        self.file_path = file_path or os.path.join(appdata_path, 'clipboard_data.json')

        # Guardar la ruta en un archivo de configuración
        self.config_path = os.path.join(appdata_path, 'config.json')

        # Cargar la ruta guardada si existe
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    saved_path = config.get('file_path')
                    if saved_path and os.path.exists(saved_path):
                        self.file_path = saved_path
            except Exception as e:
                logger.error(f"Error loading config: {e}")

        self.default_settings = {
            'height': 400,
            'width': 295,
            'hotkey': 'v',
            'back_key': 'backspace',
            'groups_key': 'g',
            'new_group_key': 'n',
            'max_items': 20,
            'restart_key': 'r',
            'exit_key': 'e',
            'is_dark_mode': True,
        }

        # Crear el archivo si no existe
        if not os.path.exists(self.file_path):
            self.save_data({}, {}, self.default_settings)

    def save_data(self, groups, pinned_items, settings):
        try:
            data = {
                'groups': groups,
                'pinned_items': self.encode_pinned_items(pinned_items),
                'settings': settings
            }

            # Asegurarse de que el directorio existe
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

            # Guardar los datos
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            # Guardar la ruta en el archivo de configuración
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({'file_path': self.file_path}, f, indent=4, ensure_ascii=False)

            logger.info(f"Data saved to {self.file_path}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def update_file_path(self, new_path):
        """Actualiza la ruta del archivo y guarda la configuración"""
        self.file_path = new_path
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({'file_path': self.file_path}, f, indent=4, ensure_ascii=False)
            logger.info(f"File path updated to {new_path}")
        except Exception as e:
            logger.error(f"Error updating file path: {e}")

    def load_data(self):
        if not os.path.exists(self.file_path):
            return {}, {}, self.default_settings

        with open(self.file_path, 'r') as f:
            data = json.load(f)

        groups = data.get('groups', {})
        pinned_items = self.decode_pinned_items(data.get('pinned_items', {}))
        settings = data.get('settings', {
            'height': 400,
            'width': 295,
            'hotkey': 'v',
            'back_key': 'backspace',
            'groups_key': 'g',
            'new_group_key': 'n',
            'max_items': 20,
            'restart_key': 'r',
            'exit_key': 'e',
            'is_dark_mode': True,
        })

        # Combinar configuraciones guardadas con valores predeterminados
        settings = {**self.default_settings, **data.get('settings', {})}

        return groups, pinned_items, settings

    def decode_pinned_items(self, encoded_items):
        decoded_items = {}
        for item_id, item_data in encoded_items.items():
            decoded_item = item_data.copy()
            if isinstance(item_data['text'], dict) and 'format' in item_data['text']:
                decoded_item['text'] = self.decode_formatted_text(item_data['text'])
            decoded_items[item_id] = decoded_item
        return decoded_items

    def encode_pinned_items(self, pinned_items):
        encoded_items = {}
        for item_id, item_data in pinned_items.items():
            encoded_item = item_data.copy()
            if isinstance(item_data['text'], dict):
                encoded_item['text'] = self.encode_formatted_text(item_data['text'])
            else:
                # Si el texto no es un diccionario, lo tratamos como texto simple
                encoded_item['text'] = self.encode_formatted_text({'text': item_data['text'], 'formatted': {}})
            encoded_items[item_id] = encoded_item
        return encoded_items

    def encode_formatted_text(self, text_data):
        if isinstance(text_data, str):
            # Si text_data es una cadena, la tratamos como texto simple
            return {
                'text': text_data,
                'format': {}
            }
        elif isinstance(text_data, dict):
            # Si text_data es un diccionario, asumimos que tiene la estructura esperada
            text = text_data.get('text', '')
            formatted = text_data.get('formatted', {})

            if isinstance(formatted, dict):
                return {
                    'text': text,
                    'format': {
                        'font': formatted.get('font'),
                        'size': formatted.get('size'),
                        'color': formatted.get('color'),
                        'bold': formatted.get('bold'),
                        'italic': formatted.get('italic'),
                        'rtf': formatted.get('rtf'),
                        'html': formatted.get('html'),
                        'underline': formatted.get('underline'),
                        'strikethrough': formatted.get('strikethrough'),
                        'superscript': formatted.get('superscript'),
                        'subscript': formatted.get('subscript'),
                        'background_color': formatted.get('background_color'),
                        'alignment': formatted.get('alignment'),
                    }
                }
            else:
                # Si 'formatted' no es un diccionario, devolvemos un formato vacío
                return {
                    'text': text,
                    'format': {}
                }
        else:
            # Para cualquier otro tipo, convertimos a string y devolvemos sin formato
            return {
                'text': str(text_data),
                'format': {}
            }

    def decode_formatted_text(self, encoded_text):
        return {
            'text': encoded_text['text'],
            'formatted': encoded_text['format']
        }
