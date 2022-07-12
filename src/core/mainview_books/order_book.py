from core import mainview 

from core.initialize import *
from core.mainview_books.prescription.widgets import DrugList, Times, Dose, Quantity, Note, SaveDrugButton, DelDrugButton, ReuseDrugListButton

import platform
if platform.system() in ['Linux', 'Darwin']:
    from core.mainview_books.prescription.linux_drug_picker import DrugPicker
else:
    ...
import wx


import wx


class OrderBook(wx.Notebook):

    def __init__(self, parent:'mainview.MainView'):
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
        self.drug_picker = DrugPicker(self)
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
