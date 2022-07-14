from db.db_class import *
import core.other_func as otf
from core.mainview_books import order_book
from core.initialize import k_number, k_special, k_tab
from path_init import plus_bm, minus_bm

import wx
import wx.adv
from typing import Any
from collections.abc import Mapping
import sqlite3

# Generic


class DrugList(wx.ListCtrl):

    def __init__(self, parent: 'order_book.PrescriptionPage'):
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
                'drug_id': item['drug_id'],
                'times': item['times'],
                'dose': item['dose'],
                'quantity': item['quantity'],
                'note': item['note']
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

    def rebuild(self, lld: list[sqlite3.Row]):
        self.DeleteAllItems()
        self._list.clear()
        self.build(lld)

    def build(self, lld: list[sqlite3.Row]):
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
    def __init__(self, parent: 'order_book.PrescriptionPage'):
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
        if e.KeyCode in k_number+k_tab+k_special:
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
    def __init__(self, parent: 'order_book.PrescriptionPage'):
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
    def __init__(self, parent: "order_book.PrescriptionPage"):
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

    def onClick(self, e:wx.CommandEvent):
        self.parent.drug_list.remove()
        self.parent.parent.mv.state.warehouse = None
        self.parent.parent.mv.price.SetPrice()


class ReuseDrugListButton(wx.Button):
    def __init__(self, parent):
        super().__init__(parent,
                         label='Lượt khám mới với toa cũ này')
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        mv = self.Parent.Parent.Parent
        lld = self.Parent.drug_list._list.copy()
        weight = mv.weight.GetValue()
        mv.state.visit = None
        mv.weight.SetValue(weight)
        self.Parent.drug_list.rebuild(lld)
        self.Parent.Parent.Parent.updatequantitybtn.onClick(None)
