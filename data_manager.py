# data_manager.py

import json
import os

class DataManager:
    def __init__(self, file_path='clipboard_data.json'):
        self.file_path = file_path

    def save_data(self, groups, pinned_items, settings):
        data = {
            'groups': groups,
            'pinned_items': pinned_items,
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
        for group in groups.values():
            if 'items' in group:
                group['items'] = [item if isinstance(item, dict) else {'id': item, 'text': 'Unknown'} for item in group['items']]
        
        settings = data.get('settings', {
            'height': 400,
            'width': 295,
            'hotkey': 'v'
        })
        
        return groups, data.get('pinned_items', {}), settings