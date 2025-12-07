import wx

MAIN_W_WD = 700
MAIN_W_HT = 500

class ReplaceFrame(wx.Dialog):
    def __init__(self, parent, initData = '', title="Resizable Dialog"):
        super().__init__(parent, title=title,
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.data = initData
        self.InitUI()
        self.SetSize((MAIN_W_WD, MAIN_W_HT))
        self.Centre()

    def InitUI(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        main_sizer.Add(self.text_ctrl, proportion=1,
                       flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        self.text_ctrl.SetValue(self.data)

        main_sizer.AddSpacer(10)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()

        apply_btn = wx.Button(self, label="Apply")
        close_btn = wx.Button(self, id=wx.ID_CANCEL, label="Cancel")

        button_sizer.Add(apply_btn, flag=wx.RIGHT, border=5)
        button_sizer.Add(close_btn)

        main_sizer.Add(button_sizer,
                       flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.SetSizer(main_sizer)
        apply_btn.Bind(wx.EVT_BUTTON, self.OnApply)

    def GetData(self):
        return self.data
        
    def OnApply(self, event):
        self.data = self.text_ctrl.GetValue()
        self.EndModal(wx.ID_OK)

