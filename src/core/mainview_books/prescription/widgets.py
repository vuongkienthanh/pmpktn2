from db.db_class import *
import core.other_func as otf
from core.mainview_books import order_book
from core.initialize import k_number, k_special, k_tab
from path_init import  plus_bm, minus_bm

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
        self.mv = parent.parent
        self._list: list[dict[str, Any]] = []
        self.AppendColumn('STT')
        self.AppendColumn('Thuốc'.ljust(30, ' '), width=-2)
        self.AppendColumn('Số cữ')
        self.AppendColumn('Liều')
        self.AppendColumn('Tổng cộng', width=-2)
        self.AppendColumn('Cách dùng'.ljust(50, ' '), width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def append(self, item: Mapping[str,Any]):
        def append_list(item:Mapping[str,Any]):
            self._list.append({
                'drug_id': item['drug_id'],
                'name': item['name'],
                'times': item['times'],
                'dose': item['dose'],
                'quantity': item['quantity'],
                'usage': item['usage'],
                'usage_unit': item['usage_unit'],
                'sale_unit': item['sale_unit'],
                'note': item['note']
            })

        def append_ui(item:Mapping[str,Any]):
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

    def update(self, index, item):
        def update_list(index, item):
            self._list[index]['drug_id'] = item['drug_id']
            self._list[index]['name'] = item['name']
            self._list[index]['times'] = item['times']
            self._list[index]['dose'] = item['dose']
            self._list[index]['quantity'] = item['quantity']
            self._list[index]['usage'] = item['usage']
            self._list[index]['sale_unit'] = item['sale_unit']
            self._list[index]['usage_unit'] = item['usage_unit']
            self._list[index]['note'] = item['note']

        def update_ui(index, item):
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

    def onSelect(self, e):
        selected = self._list[e.Index]
        state = self.parent.parent.mv.state
        state.warehouse = state.get_wh_by_id(selected['drug_id'])
        pg = self.Parent
        pg.times.ChangeValue(str(selected['times']))
        pg.dose.ChangeValue(selected['dose'])
        pg.quantity.ChangeValue(str(selected['quantity']))
        pg.note.SetValue(selected['note'])

    def onDeselect(self, e):
        state = self.Parent.Parent.Parent.state
        state.warehouse = None
        pg = self.Parent
        pg.times.ChangeValue('')
        pg.dose.ChangeValue('')
        pg.quantity.ChangeValue('')
        pg.note.ChangeValue('')

    def upsert(self):
        state = self.Parent.Parent.Parent.state
        item = {
            'drug_id': state.warehouse.id,
            'name': state.warehouse.name,
            'times': int(self.Parent.times.Value.strip()),
            'dose': self.Parent.dose.Value.strip(),
            'quantity': int(self.Parent.quantity.Value.strip()),
            'usage': state.warehouse.usage,
            'usage_unit': state.warehouse.usage_unit,
            'sale_unit': state.warehouse.sale_unit,
            'note': self.Parent.note.GetValue()
        }
        try:
            # update
            index = [item['drug_id']
                     for item in self._list].index(state.warehouse.id)
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
        self.SetHint('lần')
        self.Bind(wx.EVT_CHAR, self.onChar)
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.Parent.check_wh_do_ti_filled():
            self.Parent.quantity.set()
            self.Parent.note.set()

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in k_number + k_special + k_tab:
            e.Skip()


class Dose(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetHint('liều')
        self.Bind(
            wx.EVT_CHAR,
            lambda e: otf.only_nums(e, decimal=True, slash=True)
        )
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.Parent.check_wh_do_ti_filled():
            self.Parent.quantity.set()
            self.Parent.note.set()


class Quantity(wx.TextCtrl):

    def __init__(self, parent):
        super().__init__(parent)
        self.SetHint('Enter')
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e:wx.KeyEvent):
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
    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self,e:wx.KeyEvent ):
        if e.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.Parent.save_drug_btn.onClick(None)
        else:
            e.Skip()
    def set(self):
        self.ChangeValue(otf.get_usage_note_str(
            usage=self.Parent.Parent.Parent.state.warehouse.usage,
            times=self.Parent.times.GetValue(),
            dose=self.Parent.dose.GetValue(),
            usage_unit=self.Parent.Parent.Parent.state.warehouse.usage_unit
        ))

    def GetValue(self):
        s = super().GetValue().strip()
        pg = self.Parent
        wh = self.Parent.Parent.Parent.state.warehouse
        if s == otf.get_usage_note_str(
                usage=wh.usage,
                times=pg.times.Value,
                dose=pg.dose.Value,
                usage_unit=wh.usage_unit):
            return None
        elif s == '':
            return None
        else:
            return s

    def SetValue(self, s):
        if s == '' or s is None:
            pg = self.Parent
            wh = self.Parent.Parent.Parent.state.warehouse
            s = otf.get_usage_note_str(
                usage=wh.usage,
                times=pg.times.Value,
                dose=pg.dose.Value,
                usage_unit=wh.usage_unit)
        super().SetValue(s)


class SaveDrugButton(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent,
                         bitmap=wx.Bitmap(plus_bm))
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        if self.Parent.check_all_filled():
            self.Parent.drug_list.upsert()
            self.Parent.Parent.Parent.state.warehouse = None
            self.Parent.Parent.Parent.price.SetPrice()


class DelDrugButton(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent,
                         bitmap=wx.Bitmap(minus_bm))
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        self.Parent.drug_list.remove()
        self.Parent.Parent.Parent.state.warehouse = None
        self.Parent.Parent.Parent.price.SetPrice()


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
