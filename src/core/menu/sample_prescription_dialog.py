from core import main_view
from db.db_class import SamplePrescription, LineSamplePrescription
import core.other_func as otf
import wx


class SampleDialog(wx.Dialog):
    def __init__(self, mv: 'main_view.MainView'):
        super().__init__(parent=mv, title="Toa mẫu",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.mv = mv
        self.samplelist = SampleList(self)
        self.itemlist = ItemList(self)
        self.picker = Picker(self)
        self.times = Times(self)
        self.dose = Dose(self)
        self.addsamplebtn = AddSampleButton(self)
        self.minussamplebtn = MinusSampleButton(self)
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
        self.mv = parent.mv
        self.AppendColumn("name".ljust(100, ' '), width=-2)
        self.build()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self) -> None:
        self.DeleteAllItems()
        for sp in self.mv.state.sampleprescriptionlist:
            self.append(sp)

    def append(self, sp: SamplePrescription) -> None:
        self.Append((sp.name,))

    def onSelect(self, e):
        self.parent.minussamplebtn.Enable()
        self.parent.picker.Enable()
        self.parent.dose.Enable()
        self.parent.times.Enable()


    def onDeselect(self, e):
        self.parent.minussamplebtn.Disable()
        self.parent.picker.Disable()
        self.parent.dose.Disable()
        self.parent.times.Disable()






class AddSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Thêm toa")
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e) -> None:
        s = wx.GetTextFromUser("Tên toa mẫu mới", "Thêm toa mẫu")
        if s != '':
            sp = SamplePrescription(name=s)
            res = self.mv.con.insert(sp)
            if res is not None:
                lastrowid, _ = res
                sp.add_id(lastrowid)
                self.mv.state.sampleprescriptionlist.append(sp)
                self.parent.samplelist.append(sp)
            else:
                wx.MessageBox("Lỗi không thêm được toa mẫu mới", "Lỗi")


class MinusSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Xóa toa")
        self.parent = parent
        self.mv = parent.mv
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e) -> None:
        idx = self.parent.samplelist.GetFirstSelected()
        if idx >= 0:
            sp = self.mv.state.sampleprescriptionlist[idx]
            rowcount = self.mv.con.delete(sp)
            if rowcount is not None:
                self.mv.state.sampleprescriptionlist.pop(idx)
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
    
    def check_state(self):
        if self.parent.picker.GetSelection() != wx.NOT_FOUND and \
                self.parent.dose.GetValue() != '' and \
                self.parent.times.GetValue() != '':
            self.Enable()
        else:
            self.Disable()



class MinusDrugButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Xóa thuốc")
        self.Disable()


class ItemList(wx.ListCtrl):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self.mv = parent.mv
        for s in [
            "Tên thuốc".ljust(40, " "),
            "Thành phần".ljust(40, " "),
            "Số cữ",
            "Liều 1 cữ"
        ]:
            self.AppendColumn(s, width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)


    def onSelect(self, e):
        self.parent.minusdrugbtn.Enable()

    def onDeselect(self, e):
        self.parent.minusdrugbtn.Disable()

