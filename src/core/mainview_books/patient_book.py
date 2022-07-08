from core.initialize import *
from core import mainview
from core.menu.patient_dialog import EditPatientDialog
from db.db_class import Patient, Visit
import sqlite3
import wx


class PatientBook(wx.Notebook):

    def __init__(self, parent:'mainview.MainView'):
        super().__init__(parent)
        self.mv = parent
        self.page0 = QueuingPatientList(self)
        self.page1 = TodayPatientList(self)
        self.AddPage(page=self.page0,
                     text='Danh sách chờ khám', select=True)
        self.AddPage(page=self.page1,
                     text='Danh sách đã khám hôm nay')
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onChanging)

    def onChanging(self, e):
        old = e.GetOldSelection()
        if old != wx.NOT_FOUND:
            item = self.GetPage(old).GetFirstSelected()
            self.GetPage(old).Select(item, 0)


class PatientListCtrl(wx.ListCtrl):

    def __init__(self, parent: PatientBook) -> None:
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.AppendColumn('Mã BN', width=-1)
        self.AppendColumn('Họ tên'.ljust(40, ' '), width=-2)
        self.AppendColumn('Giới', width=-2)
        self.AppendColumn('Ngày sinh'.ljust(10, ' '), width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick)

    def build(self, _list: list[sqlite3.Row]) -> None:
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: list[sqlite3.Row]) -> None:
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item): ...
    def onSelect(self, e): ...
    def onDeselect(self, e): ...
    def onDoubleClick(self,e):
        EditPatientDialog(self.Parent.Parent, self.Parent.Parent.state.patient).ShowModal()


class QueuingPatientList(PatientListCtrl):

    def __init__(self, parent:PatientBook):
        super().__init__(parent)
        self.AppendColumn('Giờ đăng ký'.ljust(20, ' '), width=-2)

    def append_ui(self, row: sqlite3.Row) -> None:
        self.Append([
            row['pid'],
            row['name'],
            str(row['gender']),
            row['birthdate'].strftime("%d/%m/%Y"),
            row['added_datetime'].strftime("%d/%m/%Y %H:%M")
        ])

    def onSelect(self, e: wx.ListEvent) -> None:
        mv = self.Parent.Parent
        pid = mv.state.queuelist[e.Index]['pid']
        mv.state.patient = mv.con.select(Patient, pid)

    def onDeselect(self, e: wx.ListEvent) -> None:
        self.Parent.Parent.state.patient = None


class TodayPatientList(PatientListCtrl):

    def __init__(self, parent:PatientBook):
        super().__init__(parent)
        self.mv = parent.mv
        self.AppendColumn('Giờ khám'.ljust(20, ' '), width=-2)

    def append_ui(self, row: sqlite3.Row) -> None:
        self.Append([
            row['pid'],
            row['name'],
            str(row['gender']),
            row['birthdate'].strftime("%d/%m/%Y"),
            row['exam_datetime'].strftime("%d/%m/%Y %H:%M")
        ])

    def onSelect(self, e: wx.ListEvent):
        pid = self.mv.state.todaylist[e.Index]['pid']
        self.mv.state.patient = self.mv.con.select(Patient, pid)
        vid = self.mv.state.todaylist[e.Index]['vid']
        self.mv.state.visit = self.mv.con.select(Visit, vid)
        

    def onDeselect(self, e: wx.ListEvent):
        self.mv.state.patient = None
        self.mv.state.visit = None
