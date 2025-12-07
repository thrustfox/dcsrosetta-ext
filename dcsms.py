import os
import requests
from myerror import MyError

from paths import get_app_path


class DcsMsTranslator:
    TRANSLATOR_KEY_FILE = os.path.join(get_app_path(), 'mstranslator_key.txt')
    URL = "https://api.cognitive.microsofttranslator.com/translate"

    def __init__(self):
        self.key = ''
        self.location = ''
        try:
            self.load_key()
        except:
            self.translator = ''

    def load_key(self):
        with open(self.TRANSLATOR_KEY_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                self.key = lines[0].strip()
                self.location = lines[1].strip()
        print('MS Azure key loaded')

    def save_key(self, key, location):
        with open(self.TRANSLATOR_KEY_FILE, 'w') as f:
            f.write(key + '\n')
            f.write(location + '\n')
        print("MS Azure key saved")
        self.load_key()

    def translate(self, desc, from_lang, to_lang):
        # desc: accept both array and single
        
        is_array = isinstance(desc, list)
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.location,
            "Content-Type": "application/json"
        }
        params = {}
        if from_lang == 'Auto':
            params = {
                "api-version": "3.0",
                "to": to_lang
            }
        else:
            params = {
                "api-version": "3.0",
                "from": from_lang,
                "to": to_lang
            }
        body = None
        if is_array:
            body = [{"text": text} for text in desc]
        else:
            body = [{"Text": desc}]
        
        response = None
        try:
            response = requests.post(self.URL, headers=headers, params=params, json=body)
            response.raise_for_status()  # raise exception on HTTP error
            #print(list(map(lambda d: d["translations"][0]["text"], response.json())))
            if is_array:
                return list(map(lambda d: d["translations"][0]["text"], response.json()))
            else:
                return response.json()[0]["translations"][0]["text"]
        
        except (IndexError, KeyError) as e:
            raise (MyError('Response format invalid!', 20))
        except requests.exceptions.RequestException as e:
            if response is not None:
                status_code = response.status_code
                error_message = response.json().get("error", {}).get("message", f"Unknown error occurred [{response.status_code}]")
                raise (MyError(error_message, 21))
            else:
                error_message = f"Request error - {e}"
                raise (MyError(error_message, 22))
        
    def get_supported_languages(self):
        URL = "https://api.cognitive.microsofttranslator.com/languages"
        headers = {
            "Ocp-Apim-Subscription-Key": self.key
        }
        params = {
            "api-version": "3.0",
            "scope": "translation"
        }
        response = None
        try:
            response = requests.get(URL, headers=headers, params=params)
            response.raise_for_status()  # raise exception on HTTP error
            return response.json()["translation"]
        except (IndexError, KeyError) as e:
            raise (MyError('Response format invalid!', 23))
        except requests.exceptions.RequestException as e:
            if response is not None:
                status_code = response.status_code
                error_message = response.json().get("error", {}).get("message", f"Unknown error occurred [{response.status_code}]")
                raise (MyError(error_message, 24))
            else:
                error_message = f"Request error - {e}"
                raise (MyError(error_message, 25))
    
    def get_langs(self):
        if not self.key or not self.location:
            print('Please set your MS Azure key & region')
            return None

        codes = None
        try:
            languages = self.get_supported_languages()
            if languages != None:
                codes = list(map(lambda d: d.upper(), languages.keys()))
        except Exception as e:
            print('Cannot get languages!')
        return codes

    def check_translator(self):
        if not self.key or not self.location:
            print('Please set your MS Azure key & region')
            return False
        return True
    
