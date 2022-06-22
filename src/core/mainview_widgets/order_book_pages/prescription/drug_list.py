from core.initialize import *
import core.other_func as otf
from db.db_class import Linedrug
import wx


class DrugList(wx.ListCtrl):

    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.SetBackgroundColour(wx.Colour(220, 220, 220))
        self._list = []
        self.AppendColumn('STT')
        self.AppendColumn('Thuốc'.ljust(30, ' '), width=-2)
        self.AppendColumn('Số cữ')
        self.AppendColumn('Liều')
        self.AppendColumn('Tổng cộng', width=-2)
        self.AppendColumn('Cách dùng'.ljust(50, ' '), width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def append_list(self, item):
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

    def append_ui(self, item):
        sale_unit = item['sale_unit'] or item['usage_unit']
        note = item['note'] or otf.get_note_str(
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

    def append(self, item):
        self.append_list(item)
        self.append_ui(item)

    def update_list(self, index, item):
        self._list[index]['drug_id'] = item['drug_id']
        self._list[index]['name'] = item['name']
        self._list[index]['times'] = item['times']
        self._list[index]['dose'] = item['dose']
        self._list[index]['quantity'] = item['quantity']
        self._list[index]['usage'] = item['usage']
        self._list[index]['sale_unit'] = item['sale_unit']
        self._list[index]['usage_unit'] = item['usage_unit']
        self._list[index]['note'] = item['note']

    def update_ui(self, index, item):
        sale_unit = item['sale_unit'] or item['usage_unit']
        note = item['note'] or otf.get_note_str(
            usage=item['usage'],
            times=item['times'],
            dose=item['dose'],
            usage_unit=item['usage_unit'])

        self.SetItem(index, 2, str(item['times']))
        self.SetItem(index, 3, item['dose'] + ' ' + item['usage_unit'])
        self.SetItem(index, 4, str(item['quantity']) + ' ' + sale_unit)
        self.SetItem(index, 5, note)

    def update(self, index, item):
        self.update_list(index, item)
        self.update_ui(index, item)

    def rebuild(self, lld):
        self.DeleteAllItems()
        self._list.clear()
        self.build(lld)

    def build(self, lld):
        for item in lld:
            self.append(item)

    def onSelect(self, e):
        selected = self._list[e.Index]
        state = self.Parent.Parent.Parent.state
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
