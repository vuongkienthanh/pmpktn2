from core import order_book
from db.db_class import Warehouse, LineSamplePrescription
from path_init import plus_bm, minus_bm
from core.dialogs.sample_prescription_dialog import SampleDialog
from core.other_func import get_usage_note_str, calc_quantity
import wx


class SaveDrugButton(wx.BitmapButton):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent,
                         bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        if self.parent.check_all_filled():
            self.parent.drug_list.upsert()
            self.parent.parent.mv.state.warehouse = None
            self.parent.parent.mv.price.FetchPrice()


class DelDrugButton(wx.BitmapButton):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent,
                         bitmap=wx.Bitmap(minus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        self.parent.drug_list.pop()
        self.parent.parent.mv.state.warehouse = None
        self.parent.parent.mv.price.FetchPrice()


class ReuseDrugListButton(wx.Button):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent,
                         label='Lượt khám mới với toa cũ này')
        self.parent = parent
        self.mv = parent.parent.mv
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        lld = self.parent.drug_list._list.copy()
        weight = self.mv.weight.GetWeight()
        self.mv.state.visit = None
        self.mv.weight.SetWeight(weight)
        self.parent.drug_list.rebuild(lld)
        self.mv.updatequantitybtn.update_quantity()


class UseSamplePrescriptionBtn(wx.Button):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, label="Sử dụng toa mẫu")
        self.parent = parent
        self.mv = parent.parent.mv
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        dlg = SampleDialog(self.mv)
        if dlg.ShowModal() == wx.ID_OK:
            idx: int = dlg.samplelist.GetFirstSelected()
            if idx >= 0:
                self.mv.order_book.page0.drug_list.DeleteAllItems()
                sp = self.mv.state.sampleprescriptionlist[idx]
                llsp = self.mv.con.execute(f"""
                    SELECT lsp.drug_id, wh.name, lsp.times, lsp.dose, wh.usage, wh.usage_unit, wh.sale_unit, wh.sale_price
                    FROM (
                        SELECT * FROM {LineSamplePrescription.table_name} 
                        WHERE sample_id = {sp.id}
                    ) AS lsp
                    JOIN {Warehouse.table_name} as wh
                    ON wh.id = lsp.drug_id
                """).fetchall()
                for lsp in llsp:
                    self.mv.order_book.page0.drug_list.append({
                        'drug_id': lsp['drug_id'],
                        'times': lsp['times'],
                        'dose': lsp['dose'],
                        'quantity': calc_quantity(lsp['times'], lsp['dose'], self.mv.days.Value, lsp['sale_unit'], self.mv.config['thuoc_ban_mot_don_vi']),
                        'name': lsp['name'],
                        'note': get_usage_note_str(lsp['usage'], lsp['times'], lsp['dose'], lsp['usage_unit']),
                        'usage': lsp['usage'],
                        'usage_unit': lsp['usage_unit'],
                        'sale_unit': lsp['sale_unit'],
                        'sale_price': lsp['sale_price']
                    })
                    self.mv.price.FetchPrice()
# item = {
#             'drug_id': wh.id,
#             'name': wh.name,
#             'times': int(self.parent.times.Value.strip()),
#             'dose': self.parent.dose.Value.strip(),
#             'quantity': int(self.parent.quantity.Value.strip()),
#             'usage': wh.usage,
#             'usage_unit': wh.usage_unit,
#             'sale_unit': wh.sale_unit,
#             'sale_price': wh.sale_price,
#             'note': self.parent.note.GetValue()
#         }
