from core.initialize import *
import wx


class DrugPopup(wx.ComboPopup):

    def __init__(self):
        super().__init__()
        self._list = []

    def Create(self, parent):
        self.lc = wx.ListCtrl(
            parent,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SIMPLE_BORDER
        )
        self.lc.AppendColumn('Thuốc'.ljust(30, ' '), width=-2)
        self.lc.AppendColumn('Thành phần'.ljust(30, ' '), width=-2)
        self.lc.AppendColumn('Số lượng')
        self.lc.AppendColumn('Đơn vị')
        self.lc.AppendColumn('Đơn giá')
        self.lc.AppendColumn('Cách dùng')
        self.lc.AppendColumn('Hạn sử dụng', width=-2)
        self.lc.Bind(wx.EVT_MOTION, self.OnMotion)
        self.lc.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.lc.Bind(wx.EVT_CHAR, self.onChar)
        return True

    def GetControl(self):
        return self.lc

    def Init(self):
        self.curitem = -1

    def SetStringValue(self, val):
        self.Init()
        if self.lc.ItemCount > 0:
            self.curitem += 1
            self.lc.Select(self.curitem)

    def GetStringValue(self):
        return ""

    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return super().GetAdjustedSize(*popup_size)

    def fetch_list(self, s):
        s = s.casefold()
        self._list = list(filter(
            lambda item: (s in item.name.casefold()) or (
                s in item.element.casefold()),
            self.GetComboCtrl().Parent.Parent.Parent.state.warehouselist
        ))

    def build(self):
        for index, item in enumerate(self._list):
            self.append_ui(item)
            self.check_min_quantity(item, index)

    def append_ui(self, item):
        def check_blank(val): return str(val) if val else ''
        self.lc.Append([check_blank(getattr(item, field)) for field in [
            'name', 'element', 'quantity', 'usage_unit', 'sale_price', 'usage', 'expire_date'
        ]])

    def check_min_quantity(self, item, index):
        if item.quantity <= self.ComboCtrl.Parent.Parent.Parent.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"]:
            self.lc.SetItemTextColour(index, wx.Colour(252, 3, 57))

    def OnPopup(self):
        self.lc.DeleteAllItems()
        self.fetch_list(self.GetComboCtrl().GetValue())
        self.build()

    def OnMotion(self, e):
        index, flags = self.lc.HitTest(e.GetPosition())
        if index >= 0:
            self.lc.Select(index)
            self.curitem = index

    def OnLeftDown(self, e):
        self.Dismiss()
        self.GetComboCtrl(
        ).Parent.Parent.Parent.state.warehouse = self._list[self.curitem]

    def onChar(self, e):
        c = e.GetKeyCode()
        if c == wx.WXK_DOWN:
            self.KeyDown()
        elif c == wx.WXK_UP:
            self.KeyUp()
        elif c == wx.WXK_ESCAPE:
            self.KeyESC()
        elif c == wx.WXK_RETURN:
            self.KeyReturn()

    def KeyDown(self):
        if self.lc.ItemCount > 0:
            if self.curitem < (self.lc.ItemCount - 1):
                self.curitem += 1
            self.lc.Select(self.curitem)
            self.lc.EnsureVisible(self.curitem)

    def KeyUp(self):
        if self.lc.ItemCount > 0:
            if self.curitem > 0:
                self.curitem -= 1
            self.lc.Select(self.curitem)
            self.lc.EnsureVisible(self.curitem)

    def KeyReturn(self):
        if self.lc.ItemCount > 0:
            self.OnLeftDown(None)

    def KeyESC(self):
        self.Dismiss()
        self.ComboCtrl.Parent.Parent.Parent.state.warehouse = None
        self.ComboCtrl.Parent.Parent.Parent.state.linedrug = None


class DrugPicker(wx.ComboCtrl):

    def __init__(self, parent):
        super().__init__(parent)
        self.SetPopupControl(DrugPopup())
        self.Bind(wx.EVT_CHAR, self.onChar)
        self.Bind(wx.EVT_TEXT, self.onText)
        self.SetHint("Enter để search thuốc")

    def onChar(self, e):
        if e.GetKeyCode() == wx.WXK_RETURN:
            self.Popup()
        else:
            e.Skip()

    def onText(self, e):
        if self.GetValue() == '':
            self.Parent.Parent.Parent.state.warehouse = None

        else:
            e.Skip()
