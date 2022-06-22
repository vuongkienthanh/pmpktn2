from core.initialize import *
from core.menu.patient_dialog import EditPatientDialog
from db.db_class import Patient, QueueList, QueueListWithoutTime
import wx
import sqlite3


class SearchPatientList(wx.ListCtrl):

    def __init__(self, parent, num_of_lines):
        super().__init__(
            parent,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
            size=(-1, 26 * num_of_lines)
        )
        self.AppendColumn('Mã BN', width=-2)
        self.AppendColumn('Họ tên'.ljust(40, ' '), width=-2)
        self.AppendColumn('Giới', width=-2)
        self.AppendColumn('Ngày sinh'.ljust(10, ' '), width=-2)
        self.num_of_lines = num_of_lines
        self.page_index = 0
        self.saved_pages = []
        self.temp_page = []
        self.cur_page = []
        self._done = False
        self.pid = None

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def onSelect(self, e):
        index = e.GetIndex()
        self.pid = int(self.GetItemText(index, 0))
        e.Skip()

    def onDeselect(self, e):
        self.pid = None
        e.Skip()

    def append_ui(self, row):
        self.Append([
            row['pid'],
            row['name'],
            str(row['gender']),
            row['birthdate'].strftime("%d/%m/%Y")
        ])

    def new_page(self):
        self.saved_pages.append(self.cur_page)
        self.cur_page = []
        self.page_index += 1
        self.DeleteAllItems()

    def append(self, row):
        if len(self.cur_page) == self.num_of_lines:
            self.new_page()
        self.cur_page.append(row)
        self.append_ui(row)

    def is_first(self) -> bool:
        return self.page_index == 0

    def is_last(self) -> bool:
        return self.page_index == len(self.saved_pages)

    def prev(self):
        if self.is_last():
            self.temp_page = self.cur_page.copy()
        if not self.is_first():
            self.DeleteAllItems()
            self.page_index -= 1
            self.cur_page = self.saved_pages[self.page_index]
            for row in self.cur_page:
                self.append_ui(row)

    def next(self):
        if not self.is_last():
            self.DeleteAllItems()
            self.page_index += 1
            if self.is_last():
                self.cur_page = self.temp_page
            else:
                self.cur_page = self.saved_pages[self.page_index]
            for row in self.cur_page:
                self.append_ui(row)

    def is_done(self):
        return self._done

    def done(self):
        self._done = True

    def clear(self):
        self.page_index = 0
        self.saved_pages = []
        self.cur_page = []
        self._done = False
        self.pid = None
        self.DeleteAllItems()


class FindPatientDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Tìm bệnh nhân")
        self.cur = None
        self.num_of_lines = 15
        self.search = wx.SearchCtrl(self)
        self.search.SetHint("Tên bệnh nhân")
        self.listctrl = SearchPatientList(self, self.num_of_lines)

        self.prevbtn = wx.Button(self, label="<<Trước")
        self.nextbtn = wx.Button(self, label="Sau>>")
        self.prevbtn.Disable()
        self.nextbtn.Disable()

        self.allbtn = wx.Button(self, label="Danh sách toàn bộ bệnh nhân")
        self.addqueuebtn = wx.Button(self, label="Thêm vào danh sách chờ")
        self.editbtn = wx.Button(self, label="Cập nhật")
        self.delbtn = wx.Button(self, label="Xóa")
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()

        self._bind()
        self._setSizer()

    def _bind(self):
        self.Bind(wx.EVT_SEARCH, self.onSearch, self.search)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect, self.listctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect, self.listctrl)
        self.Bind(wx.EVT_BUTTON, self.onAll, self.allbtn)
        self.Bind(wx.EVT_BUTTON, self.onNext, self.nextbtn)
        self.Bind(wx.EVT_BUTTON, self.onPrev, self.prevbtn)
        self.Bind(wx.EVT_BUTTON, self.onAddqueue, self.addqueuebtn)
        self.Bind(wx.EVT_BUTTON, self.onEdit, self.editbtn)
        self.Bind(wx.EVT_BUTTON, self.onDelete, self.delbtn)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onSearch(self, e):
        self.rebuild(e.GetString())

    def rebuild(self, s: str):
        self.listctrl.clear()
        self.cur = self.Parent.con.select_patients_wth_name(s)
        self.build()
        self.next_prev_status_check()

    def build(self):
        if self.cur is not None:
            for _ in range(self.num_of_lines):
                row = self.cur.fetchone()
                if row is not None:
                    self.listctrl.append(row)
                else:
                    self.listctrl.done()
                    break

    def clear(self):
        self.search.ChangeValue('')
        self.listctrl.clear()
        self.prevbtn.Disable()
        self.nextbtn.Disable()
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()

    def next_prev_status_check(self):
        if self.listctrl.is_first():
            self.prevbtn.Disable()
        else:
            self.prevbtn.Enable()

        if self.listctrl.is_last():
            if self.listctrl.is_done():
                self.nextbtn.Disable()
            else:
                self.nextbtn.Enable()
        else:
            self.nextbtn.Enable()

    def onSelect(self, e):
        self.addqueuebtn.Enable()
        self.editbtn.Enable()
        self.delbtn.Enable()
        e.Skip()

    def onDeselect(self, e):
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()
        e.Skip()

    def onAll(self, e):
        self.listctrl.clear()
        self.cur = self.Parent.con.execute("""
            SELECT id AS pid, name, gender, birthdate
            FROM patients
        """)
        self.build()
        self.next_prev_status_check()

    def onNext(self, e):
        if (not self.listctrl.is_done()) and self.listctrl.is_last():
            self.build()
        else:
            self.listctrl.next()
        self.next_prev_status_check()

    def onPrev(self, e):
        self.listctrl.prev()
        self.next_prev_status_check()

    def onAddqueue(self, e):
        pid = self.listctrl.pid
        if pid:
            try:
                self.Parent.con.insert(QueueListWithoutTime(patient_id=pid))
                wx.MessageBox("Thêm vào danh sách chờ thành công", "OK")
                self.Parent.refresh()
            except sqlite3.IntegrityError as error:
                wx.MessageBox("Đã có tên trong danh sách chờ.\n" +
                              str(error), "Lỗi", parent=self)
            finally:
                item = self.listctrl.GetFirstSelected()
                self.listctrl.Select(item, 0)
                self.search.SetFocus()

    def onEdit(self, e):
        pid = self.listctrl.pid
        p = self.Parent.con.select(Patient, pid)
        if p:
            if EditPatientDialog(self.Parent, p).ShowModal() == wx.ID_OK:
                self.clear()
            item = self.listctrl.GetFirstSelected()
            self.listctrl.Select(item, 0)
            self.search.SetFocus()

    def onDelete(self, e):
        pid = self.listctrl.pid
        if pid:
            try:
                self.Parent.con.delete(Patient, pid)
                wx.MessageBox("Xóa thành công", "OK")
                self.Parent.refresh()
                self.clear()
            except sqlite3.Error as error:
                wx.MessageBox("Lỗi không xóa được\n"+str(error),  "Lỗi")
            finally:
                self.search.SetFocus()

    def onClose(self, e):
        if self.cur is not None:
            self.cur.close()
        e.Skip()

    def _setSizer(self):
        def create_tuple(w): return (w, 0, wx.EXPAND | wx.ALL, 3)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.search, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(wx.StaticText(self, label="Danh sách bệnh nhân"),
                  0, wx.EXPAND | wx.ALL ^ wx.BOTTOM, 10)
        sizer.Add(self.listctrl, 1, wx.EXPAND | wx.ALL, 10)

        navi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        navi_sizer.AddStretchSpacer()
        navi_sizer.Add(self.allbtn, 0, wx.EXPAND | wx.ALL, 3)
        navi_sizer.AddStretchSpacer()
        navi_sizer.AddMany([
            create_tuple(self.prevbtn),
            create_tuple(self.nextbtn)
        ])
        navi_sizer.AddStretchSpacer()
        sizer.Add(navi_sizer, 0, wx.EXPAND)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        btn_sizer.AddMany([
            create_tuple(self.addqueuebtn),
            create_tuple(self.editbtn),
            create_tuple(self.delbtn),
            create_tuple(self.cancelbtn),
        ])

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(sizer)
