import wx
import webbrowser
import sys
import time
from threading import Thread
from easyconfig import *
from ezframe import EzFrame
from paths import resource_path
import wx.lib.agw.hyperlink as hl
from myerror import MyError

from campaign import Campaign
from dcsdeepl import DcsDeepLTranslator
from dcsms import DcsMsTranslator
from mission import Mission
from paths import resource_path
import version
from dcsdictionary import DcsDictionary
from dcsreplacer import DcsReplacer
from replaceframe import ReplaceFrame

defLangCode = 'EN'

TRANS_MS = 'MS Translator'
TRANS_DEEPL = 'DeepL'

MODE_MIZ = 'mode_miz'
MODE_CMP = 'mode_cmp'

MAIN_W_WD = 820
MAIN_W_HT = 740

CTRL_ID_SAVE = 101
CTRL_ID_REGION = 102
CTRL_ID_BROWSE = 103
CTRL_ID_FROM_LANG = 104
CTRL_ID_TO_LANG = 105
CTRL_ID_USE_DEFAULT = 106
CTRL_ID_USE_CUSTOM = 107
CTRL_ID_CUSTOM_CODE = 108
CTRL_ID_PREVENT_RENAME = 109
CTRL_ID_ADVANCED_MODE = 110
CTRL_ID_TRANSLATE = 111
CTRL_ID_DOWNLOAD = 112
CTRL_ID_UPLOAD = 113
CTRL_ID_MAKE = 114
CTRL_ID_NEW_VERSION = 115
CTRL_ID_GITHUB = 116
CTRL_ID_TRANSLATOR_KEY = 117
CTRL_ID_PATH = 118
CTRL_ID_OUTPUT = 119
CTRL_ID_TRANSLATOR = 120
CTRL_ID_REGION_LABEL = 121
CTRL_ID_NEW_VERSION = 122
CTRL_ID_SPLIT_SIZE = 123
CTRL_ID_DELAY = 124
CTRL_ID_CANCEL = 125
CTRL_ID_FILTER = 126
CTRL_ID_BILINGUAL = 127
CTRL_ID_RRULES = 128
CTRL_ID_TEST = 130

MS_DEFAULT_DELAY = '20'
DEEPL_DEFAULT_DELAY = '1'

configDef = {}
configDef['from_lang'     ] = 'Auto'
configDef['to_lang'       ] = defLangCode
configDef['use_default'   ] = False
configDef['use_custom'    ] = False
configDef['custom_code'   ] = ''
configDef['advanced_mode' ] = False
configDef['prevent_rename'] = False
configDef['translator'    ] = TRANS_MS
configDef['split_size'    ] = '100'
configDef['delay'         ] = MS_DEFAULT_DELAY
configDef['filter'        ] = 'UnitName,GroupName,WptName'
configDef['bilingual'     ] = False

def to_int(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0

class MainWindow(EzFrame):
    state = {
        'download-enabled': False,
        'make-enabled'    : False,
        'download-visible': False,
        'upload-visible'  : False,
        'make-visible'    : False,
        'processing'      : False,
        'initializing'    : True,
        'region-visible'  : False,
        'new-version-visible': False,
    }

    def get_trans_mode(self, values):
        path = values[CTRL_ID_PATH]
        if path.endswith('.miz'):
            return MODE_MIZ
        elif path.endswith('.cmp'):
            return MODE_CMP
        return None

    def set_new_version(self):
        if version.is_outdated():
            self.state['new-version-visible'] = True
        else:
            self.state['new-version-visible'] = False
    
    def update_control(self):
        self.SetEnable(CTRL_ID_SAVE, True)
        self.SetEnable(CTRL_ID_BROWSE, True)
        self.SetVisible(CTRL_ID_DOWNLOAD, self.state['download-visible'])
        self.SetVisible(CTRL_ID_UPLOAD, self.state['upload-visible'  ])
        self.SetVisible(CTRL_ID_MAKE, self.state['make-visible'    ])
        self.SetVisible(CTRL_ID_REGION, self.state['region-visible'])
        self.SetVisible(CTRL_ID_REGION_LABEL, self.state['region-visible'])
        self.SetVisible(CTRL_ID_NEW_VERSION, self.state['new-version-visible'])
        if self.state['initializing'] == True:
            self.SetVisible(CTRL_ID_TRANSLATE, True)
            self.SetEnable(CTRL_ID_TRANSLATE, False)
            self.SetVisible(CTRL_ID_CANCEL, False)
            self.SetEnable(CTRL_ID_DOWNLOAD , False)
            self.SetEnable(CTRL_ID_UPLOAD   , False)
            self.SetEnable(CTRL_ID_MAKE     , False)
        elif self.state['processing'] == True:
            self.SetVisible(CTRL_ID_TRANSLATE, False)
            self.SetEnable(CTRL_ID_TRANSLATE, True)
            self.SetVisible(CTRL_ID_CANCEL, True)
            self.SetEnable(CTRL_ID_DOWNLOAD , False)
            self.SetEnable(CTRL_ID_UPLOAD   , False)
            self.SetEnable(CTRL_ID_MAKE     , False)
        else:
            self.SetVisible(CTRL_ID_TRANSLATE, True)
            self.SetEnable(CTRL_ID_TRANSLATE, True)
            self.SetVisible(CTRL_ID_CANCEL, False)
            self.SetEnable(CTRL_ID_DOWNLOAD , self.state['download-enabled'])
            self.SetEnable(CTRL_ID_UPLOAD   , True)
            self.SetEnable(CTRL_ID_MAKE     , self.state['make-enabled'    ])

    def update_values(self):
        self.UpdateValue(CTRL_ID_FROM_LANG     , configDef['from_lang'     ])
        self.UpdateValue(CTRL_ID_TO_LANG       , configDef['to_lang'       ])
        self.UpdateValue(CTRL_ID_USE_DEFAULT   , configDef['use_default'   ])
        self.UpdateValue(CTRL_ID_USE_CUSTOM    , configDef['use_custom'    ])
        self.UpdateValue(CTRL_ID_CUSTOM_CODE   , configDef['custom_code'   ])
        self.UpdateValue(CTRL_ID_ADVANCED_MODE , configDef['advanced_mode' ])
        self.UpdateValue(CTRL_ID_PREVENT_RENAME, configDef['prevent_rename'])
        self.UpdateValue(CTRL_ID_TRANSLATOR    , configDef['translator'    ])
        self.UpdateValue(CTRL_ID_SPLIT_SIZE    , configDef['split_size'    ])
        self.UpdateValue(CTRL_ID_DELAY         , configDef['delay'         ])
        self.UpdateValue(CTRL_ID_FILTER        , configDef['filter'        ])
        self.UpdateValue(CTRL_ID_BILINGUAL     , configDef['bilingual'     ])

    def save_config(self, values):
        configDef['from_lang'     ] = values[CTRL_ID_FROM_LANG]
        configDef['to_lang'       ] = values[CTRL_ID_TO_LANG]
        configDef['use_default'   ] = values[CTRL_ID_USE_DEFAULT]
        configDef['use_custom'    ] = values[CTRL_ID_USE_CUSTOM]
        configDef['custom_code' ] = values[CTRL_ID_CUSTOM_CODE]
        configDef['advanced_mode' ] = values[CTRL_ID_ADVANCED_MODE]
        configDef['prevent_rename'] = values[CTRL_ID_PREVENT_RENAME]
        configDef['translator'    ] = values[CTRL_ID_TRANSLATOR]
        configDef['split_size'    ] = values[CTRL_ID_SPLIT_SIZE]
        configDef['delay'         ] = values[CTRL_ID_DELAY]
        configDef['filter'        ] = values[CTRL_ID_FILTER]
        configDef['bilingual'     ] = values[CTRL_ID_BILINGUAL]
        self.easyConfig.saveConfig(configDef)

    def set_advanced_mode(self, enabled):
        if enabled:
            self.state['download-visible'] = True
            self.state['upload-visible'  ] = True
            self.state['make-visible'    ] = True
            self.state['download-enabled'] = False
            self.state['make-enabled'    ] = False
        else:
            self.state['download-visible'] = False
            self.state['upload-visible'  ] = False
            self.state['make-visible'    ] = False
    
    def on_init(self):
        #DcsDictionary.set_translator(DcsMsTranslator())
        DcsDictionary.set_translator(self.getTranslator())
        print('Initializing...')
        self.UpdateValue(CTRL_ID_TRANSLATOR_KEY, DcsDictionary.translator.key)
        self.UpdateValue(CTRL_ID_REGION, DcsDictionary.translator.location)
        self.langs_dict = DcsDictionary.translator.get_langs()
        if self.langs_dict:
            self.update_langs()
            self.state['initializing'      ] = False
            print('Ready')
        self.update_control()

    def on_deinit(self):
        self.exiting = True
        values = self.GetValues()
        self.save_config(values)
        replacer = DcsDictionary.replacer
        if replacer != None:
            replacer.save_data()
        self.Destroy()
        
    def on_char(self, event):
        keycode = event.GetKeyCode()
        # number(0~9), back-space, Delete, arrow key allowed
        if chr(keycode).isdigit() or keycode in (wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_LEFT, wx.WXK_RIGHT):
            event.Skip()
        # ignore others
        else:
            return
        
    def __init__(self, parent, id, title):
        EzFrame.__init__(self, parent, id, title, size = (MAIN_W_WD, MAIN_W_HT))

        icon_path = 'rosetta.ico'
        self.SetIcon(wx.Icon(resource_path(icon_path), wx.BITMAP_TYPE_ICO))

        self.transMs = None
        self.transDeepL = None
        self.exiting = False
        
        panel = self.GetPanel()
        #panel.SetBackgroundColour(wx.Colour(255, 200, 200))
        emptyList = []
        translatorList = [TRANS_MS, TRANS_DEEPL]

        link1 = hl.HyperLinkCtrl(panel, CTRL_ID_NEW_VERSION, "NEW VERSION AVAILABLE!",
                                URL="https://github.com/thrustfox/dcsrosetta-ext/releases")
        link1.SetColours("BLUE", "PURPLE", "RED")  # normal, visited, click color
        link1.SetBold(True)
        link1.EnableRollover(True)
        
        link2 = hl.HyperLinkCtrl(panel, -1, "DCS Rosetta on GitHub",
                                URL="https://github.com/thrustfox/dcsrosetta-ext")
        link2.SetColours("BLUE", "PURPLE", "RED")  # normal, visited, click color
        link2.SetBold(True)
        link2.EnableRollover(True)

        textctrl_path = wx.TextCtrl(panel, CTRL_ID_PATH, size=(-1, -1))
        textctrl_split_size = wx.TextCtrl(panel, CTRL_ID_SPLIT_SIZE, size=(70, -1))
        textctrl_delay = wx.TextCtrl(panel, CTRL_ID_DELAY, size=(70, -1))
        
        self.SetLayout(
            [
                ['Translator:', wx.ComboBox(panel, CTRL_ID_TRANSLATOR, choices=translatorList, style=wx.CB_READONLY), wx.StaticText(panel, CTRL_ID_REGION_LABEL, label='Region:'), wx.TextCtrl(panel, CTRL_ID_REGION, size=(160, -1))],
                ['Translator key:', wx.TextCtrl(panel, CTRL_ID_TRANSLATOR_KEY, size=(-1, -1)), wx.Button(panel, CTRL_ID_SAVE, 'Save')],
                ['Mission or campaign file:', textctrl_path, wx.Button(panel, CTRL_ID_BROWSE, 'Browse')],
                ['Original language:', wx.ComboBox(panel, CTRL_ID_FROM_LANG, choices=emptyList, style=wx.CB_READONLY), 'Translated language:', wx.ComboBox(panel, CTRL_ID_TO_LANG, choices=emptyList, style=wx.CB_READONLY), wx.CheckBox(panel, CTRL_ID_BILINGUAL, "Bilingual text")],
                [wx.CheckBox(panel, CTRL_ID_USE_DEFAULT, "Overwrite default"), wx.CheckBox(panel, CTRL_ID_USE_CUSTOM, "Use custom code"), wx.TextCtrl(panel, CTRL_ID_CUSTOM_CODE, size=(100, -1)), wx.CheckBox(panel, CTRL_ID_PREVENT_RENAME, "Prevent rename"), wx.CheckBox(panel, CTRL_ID_ADVANCED_MODE, "Advanced mode")],
                ['Split size:', textctrl_split_size, 'Delay interval(s):', textctrl_delay, 'ID Filter:', wx.TextCtrl(panel, CTRL_ID_FILTER, size=(500, -1))],
                [wx.Button(panel, CTRL_ID_TRANSLATE, "Translate"), wx.Button(panel, CTRL_ID_CANCEL, "Stop"), wx.Button(panel, CTRL_ID_DOWNLOAD, "Review"), wx.Button(panel, CTRL_ID_UPLOAD, "Upload review"), wx.Button(panel, CTRL_ID_MAKE, "Make .miz/.cmp"), '', wx.Button(panel, CTRL_ID_RRULES, 'R. Rules')],
                [wx.TextCtrl(panel, CTRL_ID_OUTPUT, size=(-1, -1), style=wx.TE_MULTILINE | wx.TE_READONLY)],
                ["%s" % version.get_version().split("\n")[0], link1, link2],
            ],
            stretchCols = [(1, 1), (2, 1), (5, 5), (6, 5), (7, 0)], stretchRow = 7
        )
        self.SetOnEvent(self.OnEvent)
        textctrl_split_size.Bind(wx.EVT_CHAR, self.on_char)
        textctrl_delay.Bind(wx.EVT_CHAR, self.on_char)
        
        ctrl = self.GetControl(CTRL_ID_OUTPUT)
        self.SetStdoutCtrl(ctrl)
        
        self.easyConfig = EasyConfig()
        self.easyConfig.setFileName('dcsrosetta.ini')
        self.easyConfig.loadConfig(configDef)
        
        self.set_advanced_mode(configDef['advanced_mode'])
        if configDef['translator'] == TRANS_MS:
            self.state['region-visible'] = True
        elif configDef['translator'] == TRANS_DEEPL:
            self.state['region-visible'] = False
        self.set_new_version()
        
        self.update_values()
        self.Bind(wx.EVT_CLOSE, self.on_close)  # bind close event
        self.update_control()

        DcsDictionary.set_replacer(DcsReplacer())

        Thread(group=None, target=self.on_init, kwargs=None).start()
        self.miz = None

    def on_close(self, event):
        if self.state['processing'] == True:
            if wx.MessageBox('Translation in progress. Force to exit?', 'Info', wx.YES_NO | wx.NO_DEFAULT|  wx.ICON_WARNING) == wx.NO:
                return
            
        Campaign.stop_process(True)
        Mission.stop_process(True)
        self.on_deinit()
        
    def _get_langs_kwargs(self, values):
        return {
            'from_lang': values[CTRL_ID_FROM_LANG],
            'to_lang': values[CTRL_ID_TO_LANG],
            'use_default': values[CTRL_ID_USE_DEFAULT],
            'use_custom': values[CTRL_ID_USE_CUSTOM],
            'custom_code': values[CTRL_ID_CUSTOM_CODE],
            'advanced_mode': values[CTRL_ID_ADVANCED_MODE],
            'mode': self.get_trans_mode(values),
            'prevent_rename': values[CTRL_ID_PREVENT_RENAME],
            'split_size': to_int(values[CTRL_ID_SPLIT_SIZE]),
            'delay': to_int(values[CTRL_ID_DELAY]),
            'filter1': values[CTRL_ID_FILTER],
            'bilingual': values[CTRL_ID_BILINGUAL],
        }

    def print_err(self, e, code):
        if isinstance(e, MyError):
            code = e.code

        str1 = str(e)
        base_code = None
        if configDef['translator'] == TRANS_MS:
            base_code = 100
        elif configDef['translator'] == TRANS_DEEPL:
            base_code = 200
        code = base_code + code
        
        print(f'Error({code}): {str1}')
    
    def on_translate(self, mode = None, dest_miz: str = None, whole: bool = True, from_lang=None, to_lang=None, use_default=False, use_custom=False, custom_code='', advanced_mode = False, prevent_rename = None, split_size = 0, delay = 0, filter1='', bilingual=False):
        to_continue = False
        extra = {
            'use_default': use_default,
            'use_custom': use_custom,
            'custom_code': custom_code,
            'advanced_mode': advanced_mode,
            'prevent_rename': prevent_rename,
            'split_size': split_size,
            'delay': delay,
            'filter1': filter1,
            'pseudo': False,
            'bilingual': bilingual,
        }
        if mode == MODE_MIZ:
            try:
                Mission.stop_process(False)
                self.miz.translate(dest_miz, whole, from_lang, to_lang, extra)
                to_continue = True
            except Exception as e:
                self.print_err(e, 1)
        elif mode == MODE_CMP:
            try:
                Campaign.stop_process(False)
                Mission.stop_process(False)
                self.cmp.translate(from_lang, to_lang, extra)
                to_continue = True
            except Exception as e:
                self.print_err(e, 2)

        self.state['processing'      ] = False
        if to_continue:
            print('Translation complete!')
            self.state['download-enabled'] = True
            self.state['make-enabled'    ] = True
        else:
            self.state['download-enabled'] = False
            self.state['make-enabled'    ] = False
        if self.exiting == False:
            self.update_control()
    
    def on_save(self, mode = None, dest_miz: str = None, whole: bool = True, from_lang=None, to_lang=None, use_default=False, use_custom=False, custom_code='', advanced_mode = False, prevent_rename = None, split_size = 0, delay = 0, filter1='', bilingual=False):
        if mode == MODE_MIZ:
            try:
                self.miz.save()
            except Exception as e:
                self.print_err(e, 3)
        elif mode == MODE_CMP:
            try:
                self.cmp.save()
            except Exception as e:
                self.print_err(e, 4)
            
        self.state['processing'] = False
        self.update_control()
    
    def on_onepass(self, mode = None, dest_miz: str = None, whole: bool = True, from_lang=None, to_lang=None, use_default=False, use_custom=False, custom_code='', advanced_mode = False, prevent_rename = None, split_size = 0, delay = 0, filter1='', bilingual=False):
        extra = {
            'use_default': use_default,
            'use_custom': use_custom,
            'custom_code': custom_code,
            'advanced_mode': advanced_mode,
            'prevent_rename': prevent_rename,
            'split_size': split_size,
            'delay': delay,
            'filter1': filter1,
            'pseudo': False,
            'bilingual': bilingual,
        }
        if mode == MODE_MIZ:
            try:
                Mission.stop_process(False)
                self.miz.translate(dest_miz, whole, from_lang, to_lang, extra)
                self.miz.save()
            except Exception as e:
                self.print_err(e, 5)
        elif mode == MODE_CMP:
            try:
                Campaign.stop_process(False)
                Mission.stop_process(False)
                self.cmp.translate(from_lang, to_lang, extra)
                self.cmp.save()
            except Exception as e:
                self.print_err(e, 6)
            
        self.state['processing'] = False
        if self.exiting == False:
            self.update_control()

    def on_download(self, values):
        path = values[CTRL_ID_PATH]
        if path.endswith('.miz'):
            default_path = self.miz.path.replace('.miz', '.xlsx')

            dialog = wx.FileDialog(self, "Save As", "", default_path, "Excel Workbook (*.xlsx)|*.xlsx", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            
            filename = dialog.GetPath()
            if filename:
                try:
                    self.miz.save_to_xls(filename)
                    print('Review file downloaded')
                except Exception as e:
                    self.print_err(e, 7)
        elif path.endswith('.cmp'):
            default_path = self.cmp.path.replace('.cmp', '.xlsx')

            dialog = wx.FileDialog(self, "Save As", "", default_path, "Excel Workbook (*.xlsx)|*.xlsx", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            
            filename = dialog.GetPath()
            if filename:
                try:
                    self.cmp.save_to_xls(filename)
                    print('Review file downloaded')
                except Exception as e:
                    self.print_err(e, 8)
        else:
            self.print_err(Exception(f'Please select mission or campaign file!'), 14)
        
    def on_upload(self, values):
        path = values[CTRL_ID_PATH]
        from_lang = values[CTRL_ID_FROM_LANG]
        to_lang = values[CTRL_ID_TO_LANG]

        extra = {
            'use_default': values[CTRL_ID_USE_DEFAULT],
            'use_custom': values[CTRL_ID_USE_CUSTOM],
            'custom_code': values[CTRL_ID_CUSTOM_CODE],
            'advanced_mode': values[CTRL_ID_ADVANCED_MODE],
            'prevent_rename': values[CTRL_ID_PREVENT_RENAME],
            'split_size': to_int(values[CTRL_ID_SPLIT_SIZE]),
            'delay': to_int(values[CTRL_ID_DELAY]),
            'filter1': values[CTRL_ID_FILTER],
            'pseudo': True,
            'bilingual': values[CTRL_ID_BILINGUAL],
        }
        
        if path.endswith('.miz'):
            dialog = wx.FileDialog(self, "Select a file to upload", "", "", "Excel Workbook (*.xlsx)|*.xlsx", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            
            filename = dialog.GetPath()
            if filename:
                try:
                    if self.miz == None:
                        miz = Mission(path)
                        self.miz = miz
                        self.miz.translate(None, True, from_lang, to_lang, extra)
                    
                    self.miz.load_from_xls(filename)
                    print('Review file uploaded')
                    self.state['make-enabled'    ] = True
                    self.update_control()
                except Exception as e:
                    self.print_err(e, 9)
        elif path.endswith('.cmp'):
            dialog = wx.FileDialog(self, "Select a file to upload", "", "", "Excel Workbook (*.xlsx)|*.xlsx", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            
            filename = dialog.GetPath()
            if filename:
                try:
                    if self.cmp == None:
                        cmp = Campaign(path)
                        self.cmp = cmp
                        self.cmp.translate(from_lang, to_lang, extra)

                    self.cmp.load_from_xls(filename)
                    print('Review file uploaded')
                    self.state['make-enabled'    ] = True
                    self.update_control()
                except Exception as e:
                    self.print_err(e, 10)
        else:
            self.print_err(Exception(f'Please select mission or campaign file!'), 15)

    def on_browse(self):
        dialog = wx.FileDialog(self, "Select a file to translate", "", "", "DCS (*.miz;*.cmp)|*.miz;*.cmp", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetPath()
            if filename:
                self.UpdateValue(CTRL_ID_PATH, filename)
                self.state['download-enabled'] = False
                self.state['make-enabled'    ] = False
                self.update_control()
                self.miz = None
                self.cmp = None

        dialog.Destroy()

    def OnEvent(self, key):
        #print('OnEvent ' + str(key))
        
        values = self.GetValues()
        if key == CTRL_ID_SAVE:
            try:
                self.save_translator_key(values[CTRL_ID_TRANSLATOR_KEY], values[CTRL_ID_REGION])
            except Exception as e:
                self.print_err(e, 11)
                return
            wx.MessageBox('You need to restart if you change the key!', 'Info', wx.OK | wx.ICON_INFORMATION)
            Campaign.stop_process(True)
            Mission.stop_process(True)
            self.on_deinit()
        elif key == CTRL_ID_FROM_LANG:
            self.change_languages(values[CTRL_ID_FROM_LANG])
        elif key == CTRL_ID_BROWSE:
            self.on_browse()
        elif key == CTRL_ID_DOWNLOAD:
            self.on_download(values)
        elif key == CTRL_ID_UPLOAD:
            self.on_upload(values)
        elif key == CTRL_ID_MAKE:
            print('')
            try:
                if self.get_trans_mode(values) == MODE_MIZ or self.get_trans_mode(values) == MODE_CMP:
                    self.state['processing'] = True
                    self.update_control()
                    Thread(group=None, target=self.on_save, kwargs=self._get_langs_kwargs(values)).start()
                else:
                    raise (Exception(f'Please select mission or campaign file!'))
            except Exception as e:
                self.print_err(e, 12)
        elif key == CTRL_ID_ADVANCED_MODE:
            self.set_advanced_mode(values[CTRL_ID_ADVANCED_MODE])
            self.update_control()
        elif key == CTRL_ID_TRANSLATE:
            if not DcsDictionary.translator.check_translator():
                return
            print('')
            try:
                path = values[CTRL_ID_PATH]
                if path.endswith('.miz'):
                    miz = Mission(path)
                    self.miz = miz
                    if values[CTRL_ID_ADVANCED_MODE] == True:
                        self.state['processing'] = True
                        self.update_control()
                        Thread(group=None, target=self.on_translate, kwargs=self._get_langs_kwargs(values)).start()
                    else:
                        self.state['processing'] = True
                        self.update_control()
                        Thread(group=None, target=self.on_onepass, kwargs=self._get_langs_kwargs(values)).start()
                elif path.endswith('.cmp'):
                    cmp = Campaign(path)
                    self.cmp = cmp
                    if values[CTRL_ID_ADVANCED_MODE] == True:
                        self.state['processing'] = True
                        self.update_control()
                        Thread(group=None, target=self.on_translate, kwargs=self._get_langs_kwargs(values)).start()
                    else:
                        self.state['processing'] = True
                        self.update_control()
                        Thread(group=None, target=self.on_onepass, kwargs=self._get_langs_kwargs(values)).start()
                else:
                    raise (Exception(f'Please select mission or campaign file!'))
            except Exception as e:
                # exception from thread will NOT caught here
                self.print_err(e, 13)
        elif key == CTRL_ID_GITHUB:
            webbrowser.open('https://github.com/thrustfox/dcsrosetta-ext')
        elif key == CTRL_ID_NEW_VERSION:
            webbrowser.open('https://github.com/thrustfox/dcsrosetta-ext/releases')
        elif key == CTRL_ID_TEST:
            print(values)
        elif key == CTRL_ID_TRANSLATOR:
            self.change_translator(values)
        elif key == CTRL_ID_CANCEL:
            print('Stopping...')
            Campaign.stop_process(True)
            Mission.stop_process(True)
        elif key == CTRL_ID_RRULES:
            dialog = ReplaceFrame(self, DcsDictionary.get_replacer_data_text(), 'Replacement Rules')
            if dialog.ShowModal() == wx.ID_OK:
                replacer = DcsDictionary.replacer
                if replacer != None:
                    replacer.from_text(dialog.GetData())
                    print('')
                    print('Rules updated!')
            
            return
            
    def update_langs(self):
        self.UpdateValues(CTRL_ID_FROM_LANG, ['Auto'] + list(self.langs_dict))
        self.UpdateValues(CTRL_ID_TO_LANG, list(self.langs_dict))
        self.UpdateValue(CTRL_ID_FROM_LANG, configDef['from_lang'])
        self.UpdateValue(CTRL_ID_TO_LANG, configDef['to_lang'])

    def empty_langs(self):
        self.UpdateValues(CTRL_ID_FROM_LANG, ['Auto'])
        self.UpdateValues(CTRL_ID_TO_LANG, [])

    def save_translator_key(self, key, region):
        DcsDictionary.translator.save_key(key, region)
        #self.langs_dict = DcsDictionary.translator.get_langs()
        #self.update_langs()

    def change_languages(self, from_lang):
        pass

    def change_translator(self, values):
        self.state['initializing'    ] = True
        self.state['download-enabled'] = False
        self.state['make-enabled'    ] = False
        translator = values[CTRL_ID_TRANSLATOR]
        if translator == TRANS_MS:
            self.state['region-visible'    ] = True
            self.UpdateValue(CTRL_ID_DELAY         , MS_DEFAULT_DELAY)
        elif translator == TRANS_DEEPL:
            self.state['region-visible'    ] = False
            self.UpdateValue(CTRL_ID_DELAY         , DEEPL_DEFAULT_DELAY)
        self.update_control()
        self.empty_langs()
        Thread(group=None, target=self.on_init, kwargs=None).start()
    
    def getTranslator(self):
        values = self.GetValues()
        translator = values[CTRL_ID_TRANSLATOR]
        if translator == TRANS_MS:
            if self.transMs == None:
                self.transMs = DcsMsTranslator()
            configDef['translator'] = translator
            return self.transMs
        elif translator == TRANS_DEEPL:
            if self.transDeepL == None:
                self.transDeepL = DcsDeepLTranslator()
            configDef['translator'] = translator
            return self.transDeepL
        return None

    
if __name__ == '__main__':
    try:
        app = wx.App(False)
        frame = MainWindow(None, -1, u"DCS Rosetta Jikji")
        frame.Show(1)
        app.MainLoop()
    except Exception as e:
        old_stdout = sys.stdout
        log_file = open("message.log", "w")
        sys.stdout = log_file
        print(e)
        sys.stdout = old_stdout
        log_file.close()
