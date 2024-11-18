# data_manager.py

import json
import os
import base64


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
   #printf"All data saved to {self.file_path}")

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

    def encode_pinned_items(self, pinned_items):
        encoded_items = {}
        for item_id, item_data in pinned_items.items():
            encoded_item = item_data.copy()
            if isinstance(item_data['text'], dict) and 'formatted' in item_data['text']:
                formatted_data = item_data['text']['formatted']
                if isinstance(formatted_data, str):
                    # Si ya es una cadena, la codificamos directamente
                    encoded_item['text']['formatted'] = base64.b64encode(formatted_data.encode('utf-8')).decode('utf-8')
                elif isinstance(formatted_data, bytes):
                    # Si ya es bytes, la codificamos directamente
                    encoded_item['text']['formatted'] = base64.b64encode(formatted_data).decode('utf-8')
                else:
                    # Si no es ni str ni bytes, convertimos a str y luego codificamos
                    encoded_item['text']['formatted'] = base64.b64encode(str(formatted_data).encode('utf-8')).decode('utf-8')
            encoded_items[item_id] = encoded_item
        return encoded_items

    def decode_pinned_items(self, encoded_items):
        decoded_items = {}
        for item_id, item_data in encoded_items.items():
            decoded_item = item_data.copy()
            if isinstance(item_data['text'], dict) and 'formatted' in item_data['text']:
                decoded_item['text']['formatted'] = base64.b64decode(item_data['text']['formatted'].encode('utf-8'))
            decoded_items[item_id] = decoded_item
        return decoded_items