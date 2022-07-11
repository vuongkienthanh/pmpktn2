from core import mainview
from db.db_class import *
import core.other_func as otf
import wx
import sqlite3


class SampleDialog(wx.Dialog):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent=parent, title="Toa mẫu",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.mv = parent
        self.samplelist = SampleList(self)
        self.addsamplebtn = AddSampleButton(self)
        self.minussamplebtn = MinusSampleButton(self)
        self.itemlist = ItemList(self)
        self.picker = Picker(self)
        self.times = Times(self)
        self.dose = Dose(self)
        self.adddrugbtn = AddDrugButton(self)
        self.minusdrugbtn = MinusDrugButton(self)
        self.set_sizer()

    def set_sizer(self) -> None:
        def static(s, center=False):
            return (wx.StaticText(self, label=s), 0, wx.ALL | wx.ALIGN_CENTER if center else wx.ALL, 5)

        def widget(w, p=1):
            return (w, p, wx.EXPAND | wx.ALL, 5)

        btn_row1 = wx.BoxSizer(wx.HORIZONTAL)
        btn_row1.AddMany([
            (self.addsamplebtn, 0, wx.ALL, 5),
            (self.minussamplebtn, 0, wx.ALL, 5),
            (0, 0, 1),
        ])
        item_row = wx.BoxSizer(wx.HORIZONTAL)
        item_row.AddMany([
            static("Thuốc", True),
            (self.picker, 1, wx.ALL, 5),
            static("Số cữ", True),
            (self.times, 0, wx.ALL, 5),
            static("Liều", True),
            (self.dose, 0, wx.ALL, 5),
        ])
        btn_row2 = wx.BoxSizer(wx.HORIZONTAL)
        btn_row2.AddMany([
            (self.adddrugbtn, 0, wx.ALL, 5),
            (self.minusdrugbtn, 0, wx.ALL, 5),
            (0, 0, 1),
        ])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            static("Danh sách toa mẫu"),
            widget(self.samplelist),
            (btn_row1, 0, wx.EXPAND),
            static("Nội dung"),
            widget(self.itemlist),
            (item_row, 0, wx.EXPAND),
            (btn_row2, 0, wx.EXPAND),
            (self.CreateStdDialogButtonSizer(wx.OK), 0, wx.EXPAND | wx.ALL, 5)
        ])
        self.SetSizerAndFit(sizer)


class SampleList(wx.ListCtrl):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, style=wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.LC_NO_HEADER)
        self.parent = parent
        self.AppendColumn("name".ljust(100, ' '), width=-2)
        self.build()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self) -> None:
        self.DeleteAllItems()
        for sp in self.parent.mv.state.sampleprescriptionlist:
            self.append(sp)

    def append(self, sp: SamplePrescription) -> None:
        self.Append((sp.name,))

    def onSelect(self, e: wx.ListEvent):
        self.parent.minussamplebtn.Enable()
        self.parent.picker.Enable()
        self.parent.dose.Enable()
        self.parent.times.Enable()
        idx: int = e.GetIndex()
        sp = self.parent.mv.state.sampleprescriptionlist[idx]
        self.parent.itemlist.build(sp.id)

    def onDeselect(self, e):
        self.parent.minussamplebtn.Disable()
        self.parent.itemlist.DeleteAllItems()
        self.parent.picker.Disable()
        self.parent.dose.Disable()
        self.parent.times.Disable()
        self.parent.itemlist.DeleteAllItems()


class AddSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Thêm toa")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e) -> None:
        s = wx.GetTextFromUser("Tên toa mẫu mới", "Thêm toa mẫu")
        if s != '':
            sp = {'name': s}
            res = self.parent.mv.con.insert(SamplePrescription, sp)
            if res is not None:
                lastrowid, _ = res
                sp = SamplePrescription(
                    id=lastrowid,
                    name=s
                )
                self.parent.mv.state.sampleprescriptionlist.append(sp)
                self.parent.samplelist.append(sp)
            else:
                wx.MessageBox("Lỗi không thêm được toa mẫu mới", "Lỗi")


class MinusSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Xóa toa")
        self.parent = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e) -> None:
        idx = self.parent.samplelist.GetFirstSelected()
        if idx >= 0:
            sp = self.parent.mv.state.sampleprescriptionlist[idx]
            rowcount = self.parent.mv.con.delete(SamplePrescription, sp.id)
            if rowcount is not None:
                self.parent.mv.state.sampleprescriptionlist.pop(idx)
                self.parent.samplelist.DeleteItem(idx)
                self.Disable()
            else:
                wx.MessageBox("Lỗi không xóa được toa mẫu", "Lỗi")


class Picker(wx.Choice):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, choices=[
            f"{wh.name}({wh.element})" for wh in parent.mv.state.warehouselist
        ])
        self.Disable()
        self.Bind(wx.EVT_CHOICE, lambda e: parent.adddrugbtn.check_state())


class Dose(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetHint('liều')
        self.Bind(
            wx.EVT_CHAR,
            lambda e: otf.only_nums(e, decimal=True, slash=True)
        )
        self.Disable()
        self.Bind(wx.EVT_TEXT, lambda e: parent.adddrugbtn.check_state())


class Times(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent,)
        self.SetHint('lần')
        self.Bind(wx.EVT_CHAR, otf.only_nums)
        self.Disable()
        self.Bind(wx.EVT_TEXT, lambda e: parent.adddrugbtn.check_state())


class AddDrugButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Thêm thuốc")
        self.parent = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def check_state(self):
        if self.parent.picker.GetSelection() != wx.NOT_FOUND and \
                self.parent.dose.GetValue() != '' and \
                self.parent.times.GetValue() != '':
            self.Enable()
        else:
            self.Disable()

    def onClick(self, e):
        idx: int = self.parent.picker.GetCurrentSelection()
        wh = self.parent.mv.state.warehouselist[idx]
        idx: int = self.parent.samplelist.GetFirstSelected()
        sp = self.parent.mv.state.sampleprescriptionlist[idx]

        lsp = {
            'drug_id': wh.id,
            'sample_id': sp.id,
            'dose': self.parent.dose.GetValue().strip(),
            'times': int(self.parent.times.GetValue().strip()),
        }

        self.parent.mv.con.insert(LineSamplePrescription, lsp)


class MinusDrugButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Xóa thuốc")
        self.parent = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        idx = self.parent.itemlist.GetFirstSelected()
        self.parent.itemlist.DeleteItem(idx)
        llsp_id = self.parent.itemlist._list_id[idx]
        self.parent.mv.con.delete(LineSamplePrescription, llsp_id)
        self.Disable()


class ItemList(wx.ListCtrl):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self._list_id: list[int] = []
        for s in [
            "Tên thuốc".ljust(40, " "),
            "Thành phần".ljust(40, " "),
            "Số cữ",
            "Liều 1 cữ"
        ]:
            self.AppendColumn(s, width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, sp_id: int):
        for lsp in self.parent.mv.con.execute(f"""
            SELECT lsp.id, wh.name, wh.element, lsp.times, lsp.dose
            FROM (
                SELECT * FROM {LineSamplePrescription.table_name} 
                WHERE sample_id = {sp_id}
            ) AS lsp
            JOIN {Warehouse.table_name} as wh
            ON wh.id = lsp.drug_id
        """).fetchall():
            self.append(lsp)

    def append(self, lsp: sqlite3.Row):
        self.Append((lsp['name'], lsp['element'], lsp['times'], lsp['dose']))
        self._list_id.append(lsp['id'])

    def onSelect(self, e):
        self.parent.minusdrugbtn.Enable()

    def onDeselect(self, e):
        self.parent.minusdrugbtn.Disable()
