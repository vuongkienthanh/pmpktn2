from path_init import plus_bm, minus_bm
from core.initialize import popup_size, k_number, k_special, k_tab
from db.db_class import Warehouse
from core import mainview
import core.other_func as otf

import wx
import wx.adv
from typing import Any
import sqlite3
import platform


class OrderBook(wx.Notebook):

    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent)
        self.mv = parent
        self.page0 = PrescriptionPage(self)
        self.AddPage(page=self.page0,
                     text='Toa thuốc', select=True)


class PrescriptionPage(wx.Panel):

    def __init__(self, parent: OrderBook):
        super().__init__(parent)
        self.parent = parent
        self._createWidgets()
        self._setSizer()

    def _createWidgets(self):
        if platform.system() in ['Linux', 'Darwin']:
            self.drug_picker = LinuxDrugPicker(self)
        self.times = Times(self)
        self.dose = Dose(self)
        self.quantity = Quantity(self)
        self.usage_unit = wx.StaticText(
            self,
            label='{Đơn vị}')
        self.sale_unit = wx.StaticText(
            self,
            label='{Đơn vị}')
        self.note = Note(self)
        self.drug_list = DrugList(self)
        self.save_drug_btn = SaveDrugButton(self)
        self.del_drug_btn = DelDrugButton(self)
        self.reuse_druglist_btn = ReuseDrugListButton(self)

    def _setSizer(self):
        def static(label):
            return (wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER | wx.RIGHT, 2)

        def widget(w, p=1):
            return (w, p, wx.RIGHT, 2)

        drug_row = wx.BoxSizer(wx.HORIZONTAL)
        drug_row.AddMany([
            static('Thuốc'),
            widget(self.drug_picker, 4),
            widget(self.times),
            static("lần, lần"),
            widget(self.dose),
            (self.usage_unit, 0, wx.ALIGN_CENTER | wx.RIGHT, 2),
            static(u"\u21D2   Tổng cộng:"),
            widget(self.quantity),
            (self.sale_unit, 0, wx.ALIGN_CENTER | wx.RIGHT, 2),
            widget(self.save_drug_btn, 0),
            widget(self.del_drug_btn, 0)
        ])

        usage_row = wx.BoxSizer(wx.HORIZONTAL)
        usage_row.AddMany([
            static('Cách dùng:'),
            widget(self.note)
        ])

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddMany([
            widget(self.reuse_druglist_btn, 0)
        ])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(drug_row, 0, wx.EXPAND)
        sizer.Add(usage_row, 0, wx.EXPAND)
        sizer.Add(self.drug_list, 1, wx.EXPAND | wx.TOP, 3)
        sizer.Add(btn_row, 0, wx.EXPAND | wx.TOP, 3)
        self.SetSizer(sizer)

    def check_wh_do_ti_filled(self):
        return all([
            self.parent.mv.state.warehouse is not None,
            self.dose.Value.strip() != '',
            self.times.Value.strip() != '',
        ])

    def check_all_filled(self):
        return all([
            self.Parent.Parent.state.warehouse is not None,
            self.dose.Value.strip() != '',
            self.times.Value.strip() != '',
            self.quantity.Value.strip() != '',
        ])


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


class LinuxDrugPicker(wx.ComboCtrl):

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


# Generic


class DrugList(wx.ListCtrl):

    def __init__(self, parent: PrescriptionPage):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.SetBackgroundColour(wx.Colour(220, 220, 220))
        self.parent = parent
        self.mv = parent.parent.mv
        self._list: list[dict[str, Any]] = []
        self.AppendColumn('STT')
        self.AppendColumn('Thuốc'.ljust(30, ' '), width=-2)
        self.AppendColumn('Số cữ')
        self.AppendColumn('Liều')
        self.AppendColumn('Tổng cộng', width=-2)
        self.AppendColumn('Cách dùng'.ljust(50, ' '), width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def append(self, item: dict[str, Any] | sqlite3.Row):
        def append_list(item: dict[str, Any] | sqlite3.Row):
            self._list.append({
                f: item[f] for f in
                ('drug_id', 'times', 'dose', 'quantity', 'name',
                 'note', 'usage', 'usage_unit', 'sale_unit')
            })

        def append_ui(item: dict[str, Any] | sqlite3.Row):
            sale_unit = item['sale_unit'] or item['usage_unit']
            note = item['note'] or otf.get_usage_note_str(
                usage=item['usage'],
                times=item['times'],
                dose=item['dose'],
                usage_unit=item['usage_unit'])
            self.Append([
                self.ItemCount + 1,
                item['name'],
                str(item['times']),
                item['dose'] + ' ' + item['usage_unit'],
                str(item['quantity']) + ' ' + sale_unit,
                note
            ])
        append_list(item)
        append_ui(item)

    def update(self, index: int, item: dict[str, Any]):
        def update_list(index: int, item: dict[str, Any]):
            self._list[index]['times'] = item['times']
            self._list[index]['dose'] = item['dose']
            self._list[index]['quantity'] = item['quantity']
            self._list[index]['note'] = item['note']

        def update_ui(index: int, item: dict[str, Any]):
            sale_unit = item['sale_unit'] or item['usage_unit']
            note = item['note'] or otf.get_usage_note_str(
                usage=item['usage'],
                times=item['times'],
                dose=item['dose'],
                usage_unit=item['usage_unit'])

            self.SetItem(index, 2, str(item['times']))
            self.SetItem(index, 3, item['dose'] + ' ' + item['usage_unit'])
            self.SetItem(index, 4, str(item['quantity']) + ' ' + sale_unit)
            self.SetItem(index, 5, note)
        update_list(index, item)
        update_ui(index, item)

    def rebuild(self, lld: list[sqlite3.Row] | list[dict[str, Any]]):
        self.DeleteAllItems()
        self._list.clear()
        self.build(lld)

    def build(self, lld: list[sqlite3.Row] | list[dict[str, Any]]):
        for item in lld:
            self.append(item)

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        selected = self._list[idx]
        state = self.mv.state
        state.warehouse = state.get_wh_by_id(selected['drug_id'])
        self.parent.times.ChangeValue(str(selected['times']))
        self.parent.dose.ChangeValue(selected['dose'])
        self.parent.quantity.ChangeValue(str(selected['quantity']))
        self.parent.note.SetValue(selected['note'])

    def onDeselect(self, e: wx.ListEvent):
        state = self.mv.state
        state.warehouse = None

    def upsert(self):
        state = self.mv.state
        wh = state.warehouse
        assert wh is not None
        item = {
            'drug_id': wh.id,
            'name': wh.name,
            'times': int(self.parent.times.Value.strip()),
            'dose': self.parent.dose.Value.strip(),
            'quantity': int(self.parent.quantity.Value.strip()),
            'usage': wh.usage,
            'usage_unit': wh.usage_unit,
            'sale_unit': wh.sale_unit,
            'note': self.parent.note.GetValue()
        }
        try:
            # update
            index: int = [item['drug_id'] for item in self._list].index(wh.id)
            self.update(index, item)
        except ValueError:
            # insert
            self.append(item)

    def remove(self):
        index = self.GetFirstSelected()
        if index != -1:
            self._list.pop(index)
            self.DeleteItem(index)
            for i in range(self.ItemCount):
                self.SetItem(i, 0, str(i + 1))


class Times(wx.TextCtrl):
    def __init__(self, parent: PrescriptionPage):
        super().__init__(parent)
        self.parent = parent
        self.SetHint('lần')
        self.Bind(wx.EVT_CHAR, self.onChar)
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.set()
            self.parent.note.AutoNote()

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in k_number + k_special + k_tab:
            e.Skip()


class Dose(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.SetHint('liều')
        self.Bind(
            wx.EVT_CHAR,
            lambda e: otf.only_nums(e, decimal=True, slash=True)
        )
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.set()
            self.parent.note.SetNote()


class Quantity(wx.TextCtrl):

    def __init__(self, parent):
        super().__init__(parent)
        self.SetHint('Enter')
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in k_number + k_tab + k_special:
            e.Skip()

    def set(self):
        mv = self.Parent.Parent.Parent
        times = int(self.Parent.times.GetValue())
        dose = self.Parent.dose.GetValue()
        days = mv.days.GetValue()
        wh = mv.state.warehouse
        res = otf.calc_quantity(times, dose, days, wh.sale_unit,
                                self.Parent.Parent.Parent.config['thuoc_ban_mot_don_vi'])
        if res is not None:
            self.SetValue(str(res))
        else:
            self.SetValue('')


class Note(wx.TextCtrl):
    def __init__(self, parent: PrescriptionPage):
        super().__init__(parent)
        self.parent = parent
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if self.parent.check_all_filled():
                self.parent.drug_list.upsert()
                self.parent.parent.mv.state.warehouse = None
                self.parent.parent.mv.price.SetPrice()
        elif e.KeyCode == k_tab:
            pass
        else:
            e.Skip()

    def AutoNote(self):
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        self.ChangeValue(otf.get_usage_note_str(
            usage=wh.usage,
            times=self.parent.times.GetValue(),
            dose=self.parent.dose.GetValue(),
            usage_unit=wh.usage_unit
        ))

    def GetNote(self):
        s = self.Value.strip()
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        if s == otf.get_usage_note_str(
                usage=wh.usage,
                times=self.parent.times.Value,
                dose=self.parent.dose.Value,
                usage_unit=wh.usage_unit
        ) or s == '':
            return None
        else:
            return s

    def SetValue(self, s):
        if s == '' or s is None:
            wh = self.parent.parent.mv.state.warehouse
            assert wh is not None
            s = otf.get_usage_note_str(
                usage=wh.usage,
                times=self.parent.times.Value,
                dose=self.parent.dose.Value,
                usage_unit=wh.usage_unit
            )
        super().SetValue(s)


class SaveDrugButton(wx.BitmapButton):
    def __init__(self, parent: PrescriptionPage):
        super().__init__(parent,
                         bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        if self.parent.check_all_filled():
            self.parent.drug_list.upsert()
            self.parent.parent.mv.state.warehouse = None
            self.parent.parent.mv.price.SetPrice()


class DelDrugButton(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent,
                         bitmap=wx.Bitmap(minus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        self.parent.drug_list.remove()
        self.parent.parent.mv.state.warehouse = None
        self.parent.parent.mv.price.SetPrice()


class ReuseDrugListButton(wx.Button):
    def __init__(self, parent: PrescriptionPage):
        super().__init__(parent,
                         label='Lượt khám mới với toa cũ này')
        self.parent = parent
        self.mv = parent.parent.mv
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        lld = self.parent.drug_list._list.copy()
        weight = self.mv.weight.GetValue()
        self.mv.state.visit = None
        self.mv.weight.SetValue(weight)
        self.parent.drug_list.rebuild(lld)
        self.mv.updatequantitybtn.onClick(None)
