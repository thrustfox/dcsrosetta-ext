import os
import time

from dcsdictionary import DcsDictionary
from mission import Mission


class CmpDictionary(DcsDictionary):
    def __init__(self):
        super()
        self.field_filter = lambda f: f.key.s.startswith('description') or f.key.s == 'file'
        self.desc = ''
        self.trans_desc = ''

    def translate(self, from_lang, to_lang, bilingual, pseudo):
        """Translates the cmp file description"""
        # TODO Do like in the miz dict
        # PROBLEM dict <-> lua_str works only 1 level
        if pseudo != True:
            print('Translating campaign description...')
        self.desc = self.dict['description']
        if pseudo == True:
            pass
        else:
            trans_desc = self.translator.translate(self.desc, from_lang, to_lang)
            trans_desc = self.replacer.replace_item(trans_desc)
            if bilingual == True:
                self.trans_desc = trans_desc + DcsDictionary.bilingualStartSym + self.desc.rstrip() + DcsDictionary.bilingualEndSym
            else:
                self.trans_desc = trans_desc
                

    def save(self, dest_path, from_lang, to_lang, use_default, use_custom, custom_code, advanced_mode): 
        to_lang_folder = to_lang
        if use_custom == True and custom_code != '':
            to_lang_folder = custom_code.upper()

        # raise exception if translation already exists
        if use_default != True:
            if '["description_{}"]'.format(to_lang_folder.upper()) in self.lua_str:
                raise (Exception(f'It seems like this campaign already has a "{to_lang_folder}" translation!'))

        lua_desc = '["description"] = "{}",'.format(self.desc_org)
        trans_desc = DcsDictionary.fix_string(self.trans_desc)

        new_lua_str = ''
        if use_default == True:
            new_lua_str = self.lua_str.replace(lua_desc, '["description"] = "{}",'.format(trans_desc))

            # delete EN resource
            if '["description_EN"]' in self.lua_str:
                temp_str = self.desc_en_org
                new_lua_str = new_lua_str.replace('["description_EN"] = "{}",'.format(temp_str), '')
        else:
            new_lua_str = self.lua_str.replace(lua_desc,
                                                lua_desc + '\n    ["description_{}"] = "{}",'.format(
                                                to_lang_folder.upper(),
                                                    trans_desc))
        super().save(dest_path, new_lua_str)

    def get_mizs(self):
        mizs = []
        for l in self.lua_str.splitlines():
            if '["file"]' in l:
                mizs.append(l.split('"')[3])
        mizs.sort()
        return mizs

    def save_to_xls(self, filename):
        self.dict = {
            'description': self.trans_desc
        }
        org_dict = {
            'description': self.desc
        }
        super().save_to_xls(org_dict, filename)
            
    def load_from_xls(self, filename):
        tdd = super().load_from_xls(filename)
        self.trans_desc = tdd.dict['description']


class Campaign:
    b_stop_process = False
    
    def __init__(self, path: str):
        self.path = path
        self.cmp_dict = CmpDictionary.from_file_path(path)

    @staticmethod
    def stop_process(value):
        Campaign.b_stop_process = value
        
    def translate(self, from_lang=None, to_lang=None, extra={}):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.use_default = extra['use_default']
        self.use_custom = extra['use_custom']
        self.custom_code = extra['custom_code']
        self.advanced_mode = extra['advanced_mode']
        if self.use_custom == True and self.custom_code == '':
            raise (Exception(f'Please enter custom lang code!'))
        self.split_size = extra['split_size']
        self.delay = extra['delay']
        self.filter1 = extra['filter1']
        pseudo = extra['pseudo']
        # pseudo : set as true when click upload without translate
        self.bilingual = extra['bilingual']

        if pseudo == True:
            self.cmp_dict.translate(from_lang, to_lang, self.bilingual, True)
        else:
            self.cmp_dict.translate(from_lang, to_lang, self.bilingual, False)

    def save(self):
        dir_path = os.path.join(os.path.dirname(self.path), 'trans_%s' % self.to_lang, '')
        if not os.path.exists(os.path.dirname(dir_path)):
            os.mkdir(os.path.dirname(dir_path))
        self.cmp_dict.save(os.path.join(dir_path, os.path.basename(self.path)), self.from_lang, self.to_lang, self.use_default, self.use_custom, self.custom_code, self.advanced_mode)

        if self.advanced_mode != True:
        
            print('Translating campaign missions...')
            i = 0
            Campaign.b_stop_process = False
            for miz_name in self.cmp_dict.get_mizs():
                miz_path = os.path.join(os.path.dirname(self.path), miz_name)
                if not os.path.exists(miz_path):
                    print("Miz file not exist: %s" % miz_path)
                    continue
                miz = Mission(miz_path)
                if i > 0 and self.delay:
                    print(f'Sleeping {self.delay}s...')
                    time.sleep(self.delay)
                try:
                    if Campaign.b_stop_process == True:
                        raise (Exception('Translation canceled!'))
                    extra = {
                        'use_default': self.use_default,
                        'use_custom': self.use_custom,
                        'custom_code': self.custom_code,
                        'prevent_rename': False,
                        'split_size': self.split_size,
                        'delay': self.delay,
                        'campaign_mode': True,
                        'filter1': self.filter1,
                        'pseudo': False,
                        'bilingual': self.bilingual,
                    }
                    miz.translate(os.path.join(dir_path, miz_name), True, self.from_lang, self.to_lang, extra)
                    miz.save()
                except Exception as e:
                    if ('Quota Exceeded' in str(e)):
                        raise (e)
                    if ('Translation canceled' in str(e)):
                        raise (e)
                    print(str(e))
                i = i + 1
    
        print('New translated campaign generated: {}'.format(dir_path))

    def save_to_xls(self, filename):
        self.cmp_dict.save_to_xls(filename)
            
    def load_from_xls(self, filename):
        self.cmp_dict.load_from_xls(filename)
