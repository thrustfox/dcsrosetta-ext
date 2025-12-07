import os
import deepl

from paths import get_app_path


class DcsDeepLTranslator:
    TRANSLATOR_KEY_FILE = os.path.join(get_app_path(), 'deepl_key.txt')

    def __init__(self):
        self.key = ''
        self.location = ''
        try:
            self.load_key()
        except:
            self.translator = ''

    def load_key(self):
        with open(self.TRANSLATOR_KEY_FILE) as f:
            self.key = f.read()
        self.translator = deepl.Translator(self.key)
        print('DeepL key loaded')

    def save_key(self, key, location):
        with open(self.TRANSLATOR_KEY_FILE, 'w') as f:
            f.write(key)
        print("DeepL key saved")
        self.load_key()

    def translate(self, desc, from_lang, to_lang):
        
        is_array = isinstance(desc, list)
        
        if from_lang == 'Auto':
            response = self.translator.translate_text(desc, target_lang=to_lang)
        else:
            response = self.translator.translate_text(desc, source_lang=from_lang, target_lang=to_lang)
            
        if is_array:
            return list(map(lambda d: d.text, response))
        else:
            return response.text

    def get_langs(self):
        if not self.translator:
            print('Please set your DeepL key')
            return None
        langs_dict = {}
        codes = None
        try:
            languages = self.translator.get_target_languages()
            codes = list(map(lambda d: d.code, languages))
        except Exception as e:
            print(str(e))
        return codes

    def check_translator(self):
        if not self.translator:
            print('Please set your DeepL key')
            return False
        return True
    
