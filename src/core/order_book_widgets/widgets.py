from core import order_book
from core.initialize import k_tab, k_number, k_special, size, tsize
import core.other_func as otf
from core.generic import NumberTextCtrl, DoseTextCtrl
from typing import Any
import wx
import sqlite3


class DrugList(wx.ListCtrl):

    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.SetBackgroundColour(wx.Colour(220, 220, 220))
        self.parent = parent
        self.mv = parent.parent.mv
        self._list: list[dict[str, Any]] = []
        self.AppendColumn('STT')
        self.AppendColumn('Thuốc', width=size(0.1))
        self.AppendColumn('Số cữ', width=size(0.03))
        self.AppendColumn('Liều', width=size(0.03))
        self.AppendColumn('Tổng cộng', width=size(0.05))
        self.AppendColumn('Cách dùng', width=size(0.15))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def clear(self):
        self.DeleteAllItems()
        self._list.clear()

    def build(self, lld: list[sqlite3.Row] | list[dict[str, Any]]):
        for item in lld:
            self.append(item)

    def rebuild(self, lld: list[sqlite3.Row] | list[dict[str, Any]]):
        self.clear()
        self.build(lld)

    def append(self, item: dict[str, Any] | sqlite3.Row):
        def append_list(item: dict[str, Any] | sqlite3.Row):
            self._list.append({
                f: item[f] for f in
                ('drug_id', 'times', 'dose', 'quantity', 'name',
                 'note', 'usage', 'usage_unit', 'sale_unit', 'sale_price')
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
        self.mv.state.warehouse = None

    def upsert(self):
        wh = self.mv.state.warehouse
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
            'sale_price': wh.sale_price,
            'note': self.parent.note.GetValue()
        }
        try:
            # update
            index: int = [item['drug_id'] for item in self._list].index(wh.id)
            self.update(index, item)
        except ValueError:
            # insert
            self.append(item)

    def pop(self):
        index = self.GetFirstSelected()
        if index != -1:
            self._list.pop(index)
            self.DeleteItem(index)
            for i in range(self.ItemCount):
                self.SetItem(i, 0, str(i + 1))


class Times(NumberTextCtrl):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, size=tsize(0.03))
        self.parent = parent
        self.SetHint('lần')
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()


class Dose(DoseTextCtrl):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, size=tsize(0.03))
        self.parent = parent
        self.SetHint('liều')
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()


class Quantity(NumberTextCtrl):

    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, size=tsize(0.03))
        self.parent = parent
        self.SetHint('Enter')
        self.Bind(wx.EVT_CHAR, self.onChar)

    def FetchQuantity(self):
        mv = self.parent.parent.mv
        times = int(self.parent.times.GetValue())
        dose = self.parent.dose.GetValue()
        days = mv.days.GetValue()
        wh = mv.state.warehouse
        assert wh is not None
        res = otf.calc_quantity(times, dose, days, wh.sale_unit,
                                mv.config['thuoc_ban_mot_don_vi'])
        if res is not None:
            self.SetValue(str(res))
        else:
            self.SetValue('')

    def onChar(self, e: wx.KeyEvent):
        kc = e.KeyCode
        if kc in k_tab:
            self.parent.note.SetFocus()
            self.parent.note.SetInsertionPointEnd()
        elif kc in k_special + k_number:
            e.Skip()


class Note(wx.TextCtrl):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if self.parent.check_all_filled():
                self.parent.drug_list.upsert()
                self.parent.parent.mv.state.warehouse = None
                self.parent.parent.mv.price.FetchPrice()
                self.parent.drug_picker.SetFocus()
        elif e.KeyCode == k_tab:
            pass
        else:
            e.Skip()

    def FetchNote(self):
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        self.ChangeValue(otf.get_usage_note_str(
            usage=wh.usage,
            times=self.parent.times.GetValue(),
            dose=self.parent.dose.GetValue(),
            usage_unit=wh.usage_unit
        ))

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

    def GetValue(self) -> str | None:
        _s: str = super().GetValue()
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        s = _s.strip()
        if s == '' or s == otf.get_usage_note_str(
            usage=wh.usage,
            times=self.parent.times.Value,
            dose=self.parent.dose.Value,
            usage_unit=wh.usage_unit
        ):
            return None
        else:
            return s
