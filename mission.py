import os
import shutil
import tempfile
import zipfile

from dcsdictionary import DcsDictionary


class Mission:
    DICTIONARY_PATH = 'l10n/DEFAULT/dictionary'
    useArray = True
    useRetry = False

    def __init__(self, path):
        self.path = path

    def _unzip(self, dest_folder):
        with zipfile.ZipFile(self.path, 'r') as zip:
            zip.extractall(dest_folder)
            zip.close()

    def _zip(self, source_folder, dest_miz_path):
        if not os.path.exists(os.path.dirname(dest_miz_path)):
            os.mkdir(os.path.dirname(dest_miz_path))
        zipf = zipfile.ZipFile(dest_miz_path, mode='w')
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len(source_folder):])
        zipf.close()

    def save_to_xls(self, filename):
        self.tdd.save_to_xls(self.dd.dict, filename)
            
    def save_to_xls_org(self, filename):
        self.dd.save_to_xls(self.dd.dict, filename)
            
    def load_from_xls(self, filename):
        self.tdd = self.tdd.load_from_xls(self.dd.dict, filename)

    @staticmethod
    def stop_process(value):
        DcsDictionary.b_stop_process = value
            
    def translate(self, dest_miz: str = None, whole: bool = True, from_lang=None, to_lang=None, extra={}):
        self.dest_miz = dest_miz
        self.to_lang = to_lang
        self.use_default = extra['use_default']
        self.prevent_rename = extra['prevent_rename']
        use_custom = extra['use_custom']
        custom_code = extra['custom_code']
        split_size = extra['split_size']
        delay = extra['delay']
        filter1 = extra['filter1']
        pseudo = extra['pseudo']
        # pseudo : set as true when click upload without translate
        bilingual = extra['bilingual']
        lua_detect = extra['lua_detect']

        campaign_mode = False
        if 'campaign_mode' in extra:
            campaign_mode = extra['campaign_mode']
        
        self.to_lang_folder = to_lang
        if use_custom == True:
            if custom_code != '':
                self.to_lang_folder = custom_code.upper()
            else:
                raise (Exception(f'Please enter custom lang code!'))

        if campaign_mode == False and pseudo == False:
            str_msg = 'Yes' if bilingual else 'No'
            print(f"Bilingual text: {str_msg}")
            str_msg = 'Yes' if self.use_default else 'No'
            print(f"Overwrite default: {str_msg}")
            str_msg = 'Yes' if use_custom else 'No'
            print(f"Use custom code: {str_msg}")
            str_msg = 'Yes' if self.prevent_rename else 'No'
            print(f"Prevent rename: {str_msg}")
            str_msg = 'Yes' if lua_detect else 'No'
            print(f"Detect script: {str_msg}")
            print(f"Split size: {split_size}")
            print(f"Delay interval: {delay}")
            if filter1:
                filters = [f.strip() for f in filter1.split(',') if f.strip()]
                if filters:
                    print(f"Translation skip filter: {filters}")
            print(f"")

        if campaign_mode == False:
            if pseudo != True:
                print(f'Translating mission: {self.path}')
        else:
            basename = os.path.basename(self.path)
            print(f'\nTranslating mission: {basename}')
        #print(f'(Split size: {split_size}, Delay interval: {delay})')
            
        tmp = tempfile.mkdtemp()
        self._unzip(tmp)
        dest_trans_path = None
        if self.use_default != True:
            dest_trans_path = os.path.join(tmp, f'l10n/{self.to_lang_folder.upper()}/')
            if os.path.exists(dest_trans_path):
                raise (Exception(f'It seems like this mission already has a "{self.to_lang_folder}" translation!: {self.path}'))
            shutil.copytree(os.path.join(tmp, 'l10n/DEFAULT/'), dest_trans_path)
        self.dd = DcsDictionary.from_file_path(os.path.join(tmp, self.DICTIONARY_PATH))
        self.tmp = tmp

        if pseudo == True:
            self.tdd = self.dd
        else:
            if whole:
                # orginal version: useArray was not supported
                # deepl/ms version: useArray is supported
                try:
                    self.tdd = self.dd.translate_whole(from_lang, to_lang, self.useArray, split_size, delay, filter1, bilingual, lua_detect)
                except Exception as e:
                    if ('Quota Exceeded' in str(e)):
                        raise (e)
                    if self.useRetry:
                        print(e)
                        print('Retrying...')
                        self.tdd = self.dd.translate_item_by_item(from_lang, to_lang)
                    else:
                        raise (e)
            else:
                self.tdd = self.dd.translate_item_by_item(from_lang, to_lang)
            
    def save(self):
        if self.use_default:
            self.tdd.save(os.path.join(self.tmp, f'l10n/DEFAULT/dictionary'))
        else:
            self.tdd.save(os.path.join(self.tmp, f'l10n/{self.to_lang_folder.upper()}/dictionary'))
        dest_miz = self.dest_miz
        if dest_miz is None:
            if self.prevent_rename:
                dir_path = os.path.join(os.path.dirname(self.path), 'trans_%s' % self.to_lang, '')
                if not os.path.exists(os.path.dirname(dir_path)):
                    os.mkdir(os.path.dirname(dir_path))
                dest_miz = os.path.join(os.path.dirname(self.path), 'trans_%s' % self.to_lang, os.path.basename(self.path))
            else:
                dest_miz_name = f'_{self.to_lang}.miz'
                dest_miz = self.path.replace('.miz', dest_miz_name)
        self._zip(self.tmp, dest_miz)
        print('New translated mission generated: {}'.format(dest_miz))
