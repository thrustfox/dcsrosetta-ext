import wx
import sys

class RedirectText:
    def __init__(self, text_ctrl):
        self.output = text_ctrl

    def write(self, string):
        self.output.AppendText(string)

    def flush(self):
        pass
        
class EzFrame(wx.Frame):
    DEFAULT_GAP_H = 10
    DEFAULT_GAP_V = 10
    
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.onEvent = None
        self.values = {}
        self.gapH = self.DEFAULT_GAP_H
        self.gapV = self.DEFAULT_GAP_V
        self.marginH = self.DEFAULT_GAP_H
        self.marginV = self.DEFAULT_GAP_V
        self.redirectedCtrlId = -1

        self.panel = wx.Panel(self)

    def SetGapH(self, value):
        self.gapH = value

    def SetGapV(self, value):
        self.gapV = value

    def SetMarginH(self, value):
        self.marginH = value

    def SetMarginV(self, value):
        self.marginV = value
        
    def SetPanel(self, panel):
        # safe to use before setLayout
        if self.panel != None:
            self.panel.Destroy()
            
        self.panel = panel
        
    def GetPanel(self):
        if self.panel == None:
            return self
        
        return self.panel

    def getStretchMap(self, stretchCols):
        if stretchCols == None:
            return {}
        
        info = {}
        if not isinstance(stretchCols, list):
            raise (Exception('stretchCols should be list of tuple!'))

        for data in stretchCols:
            if not isinstance(data, tuple):
                raise (Exception('stretchCols should be list of tuple!'))
            info[data[0]] = data[1]
        return info
    
    def SetLayout(self, layout, stretchCols = None, stretchRow = -1):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.mapIdToKey = {}
        self.mapKeyToCtrl = {}

        parent = self.GetPanel()
        stretchMap = self.getStretchMap(stretchCols)
        
        for indexV, row in enumerate(layout):
            if self.gapV > 0:
                vbox.AddSpacer(self.marginV if indexV == 0 else self.gapV)
                    
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            for indexH, ctrl in enumerate(row):
                spacer = None
                if self.gapH > 0:
                    spacer = hbox.AddSpacer(self.marginH if indexH == 0 else self.gapH)
                
                if isinstance(ctrl, str):
                    ctrl = wx.StaticText(parent, label=ctrl)
                elif isinstance(ctrl, tuple):
                    ctrl = wx.StaticText(parent, label=ctrl[0], size=(ctrl[1], -1))

                flagH = wx.ALIGN_CENTER
                if indexV == stretchRow:
                   flagH = wx.EXPAND | wx.ALL

                if indexV in stretchMap and stretchMap[indexV] == indexH:
                    hbox.Add(ctrl, proportion=1, flag=flagH)
                else:
                    hbox.Add(ctrl, 0, flagH)
                
                key = None
                if (ctrl.GetId() < int(wx.ID_AUTO_LOWEST) or ctrl.GetId() > int(wx.ID_AUTO_HIGHEST) or
                    isinstance(ctrl, wx.ComboBox) or
                    isinstance(ctrl, wx.TextCtrl) or
                    False):
                    key = ctrl.GetId()
                else:
                    key = ctrl.GetLabel()
                self.mapIdToKey[ctrl.GetId()] = key
                self.mapKeyToCtrl[key] = {
                    'className' : str(type(ctrl)),
                    'ctrl': ctrl,
                    'spacer': spacer,
                }

                if isinstance(ctrl, wx.Button):
                    self.Bind(wx.EVT_BUTTON, self.OnEventInner, ctrl)
                elif isinstance(ctrl, wx.CheckBox):
                    self.values[key] = ctrl.GetValue()
                    self.Bind(wx.EVT_CHECKBOX, self.OnEventInner, ctrl)
                elif isinstance(ctrl, wx.RadioButton):
                    self.values[key] = ctrl.GetValue()
                    self.Bind(wx.EVT_RADIOBUTTON, self.OnEventInner, ctrl)
                elif isinstance(ctrl, wx.ComboBox):
                    self.values[key] = ctrl.GetValue()
                    self.Bind(wx.EVT_COMBOBOX, self.OnEventInner, ctrl) # select event only for combo control
                    #self.Bind(wx.EVT_TEXT, self.OnEventInner, ctrl) # both select, text event
                    #self.Bind(wx.EVT_TEXT_ENTER, self.OnEventInner, ctrl) # only enter event. no need to set style = wx.TE_PROCESS_ENTER
                elif isinstance(ctrl, wx.TextCtrl):
                    self.values[key] = ctrl.GetValue()
                    self.Bind(wx.EVT_TEXT, self.OnEventInner, ctrl)
                    self.Bind(wx.EVT_TEXT_ENTER, self.OnEventInner, ctrl)
                    #self.Bind(wx.EVT_TEXT_MAXLEN, self.OnEventInner, ctrl)  # in case of setting style = wx.TE_PROCESS_ENTER
                    
            if self.gapH > 0:
                hbox.AddSpacer(self.marginH if indexH == 0 else self.gapH)
            if indexV == stretchRow:
                vbox.Add(hbox, proportion=1, flag=wx.EXPAND | wx.ALL)
            else:
                vbox.Add(hbox, 0, wx.EXPAND | wx.ALL)

        if self.gapV > 0:
            vbox.AddSpacer(self.marginV if indexV == 0 else self.gapV)
            
        #print(self.mapIdToKey)
        #print(self.values)
        parent.SetSizer(vbox, True)
        self.Layout()

    def SetOnEvent(self, handler):
        self.onEvent = handler

    def GetKey(self, targetId):
        return self.mapIdToKey[targetId]

    def UpdateRadios(self):
        for key in self.mapIdToKey.values():
            target = self.mapKeyToCtrl[key]
            if target:
                ctrl = target['ctrl']
                if isinstance(ctrl, wx.RadioButton):
                    self.values[key] = ctrl.GetValue()
            
    def OnEventInner(self, event):
        #print('OnEventInner')
        targetId = event.GetId()
        #print(targetId)
        if targetId == self.redirectedCtrlId:
            return

        key = self.mapIdToKey[targetId]
        target = self.mapKeyToCtrl[key]
        if target:
            className = target['className']
            ctrl = target['ctrl']
            if isinstance(ctrl, wx.Button):
                pass
            elif isinstance(ctrl, wx.CheckBox):
                self.values[key] = ctrl.GetValue()
            elif isinstance(ctrl, wx.RadioButton):
                self.UpdateRadios()
            elif isinstance(ctrl, wx.ComboBox):
                self.values[key] = ctrl.GetValue()
            elif isinstance(ctrl, wx.TextCtrl):
                self.values[key] = ctrl.GetValue()
            else:
                #print('unknown class!')
                pass

            if self.onEvent:
                self.onEvent(key)
        else:
            #print('not found!')
            pass

    def UpdateValues(self, key, values):
        target = self.mapKeyToCtrl[key]
        if target:
            ctrl = target['ctrl']
            if ctrl and isinstance(ctrl, wx.ComboBox):
                ctrl.Clear()
                ctrl.SetItems(values)
        
    def UpdateValue(self, key, value):
        target = self.mapKeyToCtrl[key]
        if target:
            ctrl = target['ctrl']
            if isinstance(ctrl, wx.CheckBox):
                ctrl.SetValue(value)
                self.values[key] = value
            elif isinstance(ctrl, wx.RadioButton):
                ctrl.SetValue(value)
                self.UpdateRadios()
            elif isinstance(ctrl, wx.ComboBox):
                ctrl.SetValue(value)
                self.values[key] = value
            elif isinstance(ctrl, wx.TextCtrl):
                ctrl.SetValue(value)
                self.values[key] = value
            #print(self.values)
            
    def SetEnable(self, key, value):
        target = self.mapKeyToCtrl[key]
        if target:
            ctrl = target['ctrl']
            if ctrl:
                ctrl.Enable(value)
            
    def SetVisible(self, key, value, layout = True):
        target = self.mapKeyToCtrl[key]
        if target:
            ctrl = target['ctrl']
            spacer = target['spacer']
            if value:
                ctrl and ctrl.Show(1)
                spacer and spacer.Show(1)
            else:
                ctrl and ctrl.Show(0)
                spacer and spacer.Show(0)
        
        if layout:
            self.GetPanel().Layout()

    def GetControl(self, key):
        target = self.mapKeyToCtrl[key]
        if target:
            ctrl = target['ctrl']
            return ctrl
        return None
            
    def SetStdoutCtrl(self, ctrl):
        self.redirectedCtrlId = ctrl.GetId()
        sys.stdout = RedirectText(ctrl)

    def GetValues(self):
        return self.values
