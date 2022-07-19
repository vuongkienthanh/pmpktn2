from db.db_class import Warehouse
from core import order_book
from core.initialize import popup_size
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
        self.lc.AppendColumn('Thuốc'.ljust(30), width=-2)
        self.lc.AppendColumn('Thành phần'.ljust(30), width=-2)
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

    def fetch_list(self, s: str):
        s = s.casefold()
        cc: DrugPicker = self.GetComboCtrl()
        self._list = list(filter(
            lambda item: (s in item.name.casefold()) or (
                s in item.element.casefold()),
            cc.parent.parent.mv.state.warehouselist
        ))

    def build(self):
        for index, item in enumerate(self._list):
            self.append_ui(item)
            self.check_min_quantity(item, index)

    def append_ui(self, item: Warehouse):
        if item.expire_date is None:
            expire_date = ''
        else:
            expire_date = item.expire_date.strftime("%d/%m/%Y")
        self.lc.Append([
            item.name,
            item.element,
            str(item.quantity),
            item.usage_unit,
            int(item.sale_price),
            item.usage,
            expire_date
        ])

    def check_min_quantity(self, item, index):
        if item.quantity <= self.ComboCtrl.Parent.Parent.Parent.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"]:
            self.lc.SetItemTextColour(index, wx.Colour(252, 3, 57))

    def OnPopup(self):
        self.lc.DeleteAllItems()
        cc: DrugPicker = self.GetComboCtrl()
        s: str = cc.Value
        self.fetch_list(s.strip())
        self.build()

    def OnMotion(self, e):
        index, flags = self.lc.HitTest(e.GetPosition())
        if index >= 0:
            self.lc.Select(index)
            self.curitem = index

    def OnLeftDown(self, e):
        self.Dismiss()
        cc: DrugPicker = self.GetComboCtrl()
        cc.parent.parent.mv.state.warehouse = self._list[self.curitem]

    def onChar(self, e: wx.KeyEvent):
        c = e.KeyCode
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
        cc: DrugPicker = self.GetComboCtrl()
        cc.parent.parent.mv.state.warehouse = None


class DrugPicker(wx.ComboCtrl):

    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent)
        self.parent = parent
        self.SetPopupControl(DrugPopup())
        self.Bind(wx.EVT_CHAR, self.onChar)
        self.Bind(wx.EVT_TEXT, self.onText)
        self.SetHint("Enter để search thuốc")

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode == wx.WXK_RETURN:
            self.Popup()
        else:
            e.Skip()

    def onText(self, e: wx.CommandEvent):
        if self.GetValue() == '':
            self.parent.parent.mv.state.warehouse = None
        else:
            e.Skip()
