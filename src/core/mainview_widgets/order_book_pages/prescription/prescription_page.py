from tabnanny import check
from core.initialize import *
import platform

from db.db_class import Linedrug
if platform.system() in ['Linux', 'Darwin']:
    from core.mainview_widgets.order_book_pages.prescription.linux_drug_picker import DrugPicker
else:
    ...
from core.mainview_widgets.order_book_pages.prescription.drug_list import DrugList
from core.mainview_widgets.order_book_pages.prescription.widgets import *

import wx


class PrescriptionPage(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
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
            self.Parent.Parent.state.warehouse is not None,
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
