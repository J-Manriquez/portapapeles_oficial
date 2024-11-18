
import json
import os

class DataManager:
    def __init__(self, file_path='clipboard_data.json'):
        self.file_path = file_path

    def save_data(self, groups, pinned_items, settings):
        data = {
            'groups': groups,
            'pinned_items': self.encode_pinned_items(pinned_items),
            'settings': settings
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"All data saved to {self.file_path}")

    def load_data(self):
        if not os.path.exists(self.file_path):
            return {}, {}, {
                'height': 400,
                'width': 295,
                'hotkey': 'v'
            }
        
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        
        groups = data.get('groups', {})
        pinned_items = self.decode_pinned_items(data.get('pinned_items', {}))
        settings = data.get('settings', {
            'height': 400,
            'width': 295,
            'hotkey': 'v'
        })
        
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