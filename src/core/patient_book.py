from core.initialize import left
from core import mainview
from db.db_class import Patient, Visit
import wx
import sqlite3


class PatientBook(wx.Notebook):
    """ Container for patient lists """

    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, size=(left,-1))
        self.mv = parent
        self.page0 = QueuingPatientList(self)
        self.page1 = TodayPatientList(self)
        self.AddPage(page=self.page0,
                     text='Danh sách chờ khám', select=True)
        self.AddPage(page=self.page1,
                     text='Danh sách đã khám hôm nay')
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onChanging)

    def onChanging(self, e: wx.BookCtrlEvent):
        """ Deselect before page changed """
        old: int = e.GetOldSelection()
        assert old != wx.NOT_FOUND
        oldpage: wx.ListCtrl = self.GetPage(old)
        item: int = oldpage.GetFirstSelected()
        oldpage.Select(item, 0)


class PatientListCtrl(wx.ListCtrl):
    """Base class for patient listctrl"""

    def __init__(self, parent: PatientBook):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn('Mã BN')
        self.AppendColumn('Họ tên'.ljust(40), width=-2)
        self.AppendColumn('Giới')
        self.AppendColumn('Ngày sinh'.ljust(12), width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick)

    def build(self, _list: list[sqlite3.Row]):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: list[sqlite3.Row]):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: sqlite3.Row): ...
    def onSelect(self, e: wx.ListEvent): ...
    def onDeselect(self, e: wx.ListEvent): ...

    def onDoubleClick(self, e: wx.ListEvent):
        from core.dialogs.patient_dialog import EditPatientDialog
        EditPatientDialog(self.mv).ShowModal()


class QueuingPatientList(PatientListCtrl):
    """First page, set `state.patient` when selected"""

    def __init__(self, parent: PatientBook):
        super().__init__(parent)
        self.AppendColumn('Giờ đăng ký'.ljust(20), width=-2)

    def append_ui(self, row: sqlite3.Row):
        self.Append([
            row['pid'],
            row['name'],
            str(row['gender']),
            row['birthdate'].strftime("%d/%m/%Y"),
            row['added_datetime'].strftime("%d/%m/%Y %H:%M")
        ])

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        pid: int = self.mv.state.queuelist[idx]['pid']
        self.mv.state.patient = self.mv.con.select(Patient, pid)

    def onDeselect(self, e: wx.ListEvent):
        self.mv.state.patient = None


class TodayPatientList(PatientListCtrl):
    """Second page, set `state.patient` and `state.visit` when selected"""

    def __init__(self, parent: PatientBook):
        super().__init__(parent)
        self.AppendColumn('Giờ khám')

    def append_ui(self, row: sqlite3.Row):
        self.Append([
            row['pid'],
            row['name'],
            str(row['gender']),
            row['birthdate'].strftime("%d/%m/%Y"),
            row['exam_datetime'].strftime("%d/%m/%Y %H:%M")
        ])

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        pid: int = self.mv.state.todaylist[idx]['pid']
        self.mv.state.patient = self.mv.con.select(Patient, pid)
        vid: int = self.mv.state.todaylist[idx]['vid']
        self.mv.state.visit = self.mv.con.select(Visit, vid)

    def onDeselect(self, e: wx.ListEvent):
        self.mv.state.patient = None
        self.mv.state.visit = None


class VisitList(wx.ListCtrl):
    """Set `state.visit` when selected"""

    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.mv = parent
        self.AppendColumn('Mã lượt khám')
        self.AppendColumn('Ngày giờ khám')
        self.AppendColumn('Chẩn đoán')
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, lv: list[sqlite3.Row]):
        for row in lv:
            self.append_ui(row)

    def rebuild(self, lv: list[sqlite3.Row]):
        self.DeleteAllItems()
        self.build(lv)

    def append_ui(self, row: sqlite3.Row):
        self.Append([
            row['vid'],
            row['exam_datetime'].strftime("%d/%m/%Y %H:%M"),
            row['diagnosis']
        ])

    def onSelect(self, e: wx.ListEvent):
        vid = self.mv.state.visitlist[e.Index]['vid']
        self.mv.state.visit = self.mv.con.select(Visit, vid)

    def onDeselect(self, e: wx.ListEvent):
        self.mv.state.visit = None
