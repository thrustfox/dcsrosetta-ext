import os
from myerror import MyError

from paths import get_app_path


class DcsReplacer:
    REPLACE_FILE = os.path.join(get_app_path(), 'replace.txt')
    COMMENT_CHAR = '--'

    def __init__(self):
        self.loaded_data = {}
        self.load_data()

    def load_data(self):
        self.data_text = ''
        try:
            with open(self.REPLACE_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    self.data_text += line
                    line = line.rstrip()
                    if line and not line.startswith(self.COMMENT_CHAR):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            if key and key != value:
                                self.loaded_data[key] = value
        except:
            self.loaded_data = {}
        #print(self.loaded_data)
        
    def from_text(self, text):
        lines = text.splitlines()
        self.loaded_data = {}
        for line in lines:
            line = line.rstrip()
            if line and not line.startswith(self.COMMENT_CHAR):
                if ':' in line:
                    key, value = line.split(':', 1)
                    if key and key != value:
                        self.loaded_data[key] = value
        self.data_text = text
        #print(self.loaded_data)

    def save_data(self):
        with open(self.REPLACE_FILE, 'w', encoding='utf-8') as f:
            f.write(self.data_text)

    def replace_item(self, item):
        new_item = item
        for key, value in self.loaded_data.items():
            if new_item and key and key in new_item:
                new_item = new_item.replace(key, value)
        return new_item
        
    def replace_items(self, items):
        new_items = []
        for item in items:
            new_item = self.replace_item(item)
            new_items.append(new_item)
            
        return new_items

    def get_data_text(self):
        return self.data_text
    
