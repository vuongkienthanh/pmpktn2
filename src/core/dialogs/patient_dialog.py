from db.db_class import Patient, Patient, QueueList, QueueList
from core.generic import DateTextCtrl, DatePicker, AgeCtrl, PhoneTextCtrl, GenderChoice
import core.other_func as otf
from core import mainview
import sqlite3
import wx
import wx.adv as adv


class BasePatientDialog(wx.Dialog):
    def __init__(self, parent: 'mainview.MainView', title):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.mv = parent

        self.name = wx.TextCtrl(self, size=(300, -1), name="Họ tên")
        self.gender = GenderChoice(self, name="Giới tính")
        self.birthdate_text = DateTextCtrl(self, name="Ngày sinh")
        self.birthdate = DatePicker(self, name='')
        self.birthdate.SetDateRange(
            wx.DateTime.Today() - wx.DateSpan(years=100),
            wx.DateTime.Today()
        )
        # self.age = otf.disable_text_ctrl(AgeCtrl(self, name="Tuổi"))
        self.age = AgeCtrl(self, name="Tuổi")
        self.age.Disable()
        self.address = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Địa chỉ")
        self.phone = PhoneTextCtrl(self, name="Điện thoại")
        self.past_history = wx.TextCtrl(
            self, style=wx.TE_MULTILINE, name="Bệnh nền, dị ứng")

        self.mandatory: tuple = (
            self.name,
            self.gender,
            self.birthdate_text,
        )

        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.okbtn = wx.Button(self, id=wx.ID_OK)
        self._setSizer()

        self.birthdate_text.Bind(wx.EVT_TEXT, self.onBirthdateText)
        self.birthdate.Bind(adv.EVT_CALENDAR_SEL_CHANGED, self.onBirthdate)
        self.okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def _setSizer(self):

        def widget(w: wx.Window):
            name: str = w.GetName()
            if w in self.mandatory:
                name += "*"
            return (wx.StaticText(self, label=name), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3), (w, 1, wx.EXPAND | wx.ALL, 3)
        entry = wx.FlexGridSizer(rows=8, cols=2, vgap=5, hgap=2)
        entry.AddGrowableCol(1, 1)
        entry.AddGrowableRow(5, 1)
        entry.AddGrowableRow(7, 1)
        entry.AddMany([
            *widget(self.name),
            *widget(self.gender),
            *widget(self.birthdate_text),
            *widget(self.age),
            *widget(self.birthdate),
            *widget(self.address),
            *widget(self.phone),
            *widget(self.past_history),
        ])
        btn = wx.BoxSizer(wx.HORIZONTAL)
        btn.AddMany([
            (0, 0, 1),
            (self.cancelbtn, 0, wx.ALL ^ wx.RIGHT, 10),
            (self.okbtn, 0, wx.ALL, 10),
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry, 6, wx.ALL | wx.EXPAND, 10),
            (wx.StaticText(self, label="* là bắt buộc"), 0, wx.ALL, 5),
            (btn, 0, wx.EXPAND),
        ])
        self.SetSizerAndFit(sizer)

    def is_valid(self) -> bool:
        name: str = self.name.Value
        if name.strip() == '':
            wx.MessageBox("Chưa nhập tên bệnh nhân", "Lỗi")
            return False
        elif not self.birthdate_text.is_valid():
            wx.MessageBox("Chưa nhập ngày sinh", "Lỗi")
            return False
        else:
            return True

    def onOkBtn(self, e: wx.CommandEvent) -> None: ...

    def onBirthdateText(self, e: wx.CommandEvent):
        s = e.GetString()
        if len(s) == 10 and self.birthdate_text.is_valid():
            date = self.birthdate_text.GetDate()
            self.birthdate.SetDate(date)
            self.age.SetBirthdate(date)
            e.Skip()
        else:
            self.birthdate_text.SetToolTip("Sai ngày sinh")

    def onBirthdate(self, e: adv.CalendarEvent):
        date = self.birthdate.GetDate()
        self.age.SetBirthdate(date)
        self.birthdate_text.SetDate(date)
        e.Skip()


class NewPatientDialog(BasePatientDialog):

    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, title="Bệnh nhân mới")

    def onOkBtn(self, e):
        if self.is_valid():
            try:
                name: str = self.name.Value
                lastrowid = self.mv.con.insert(Patient, {
                    'name': name.strip().upper(),
                    'gender': self.gender.GetGender(),
                    'birthdate': self.birthdate.GetDate(),
                    'address': otf.check_blank(self.address.Value),
                    'phone': otf.check_blank(self.phone.Value),
                    'past_history': otf.check_blank(self.past_history.Value)
                })
                assert lastrowid is not None
                wx.MessageBox("Đã thêm bệnh nhân mới thành công",
                              "Bệnh nhân mới")
                try:
                    if wx.MessageDialog(
                        self,
                        message="Thêm bệnh nhân mới vào danh sách chờ khám?",
                        caption="Danh sách chờ khám",
                        style=wx.OK_DEFAULT | wx.CANCEL
                    ).ShowModal() == wx.ID_OK:
                        self.mv.con.insert(
                            QueueList, {'patient_id': lastrowid})
                        wx.MessageBox(
                            "Thêm vào danh sách chờ thành công", "OK")
                        self.mv.state.queuelist = self.mv.state.get_queuelist()
                except sqlite3.IntegrityError as error:
                    wx.MessageBox(
                        f"Đã có tên trong danh sách chờ.\n{error}", "Lỗi")
                e.Skip()
            except Exception as error:
                wx.MessageBox(
                    f"Lỗi không thêm bệnh nhân mới được\n{error}", "Lỗi")


class EditPatientDialog(BasePatientDialog):

    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, title="Cập nhật thông tin bệnh nhân")
        self.mv = parent
        self.build(self.get_patient())

    def get_patient(self) -> Patient:
        p = self.mv.state.patient
        assert p is not None
        return p

    def build(self, p: Patient):
        self.name.ChangeValue(p.name)
        self.gender.SetGender(p.gender)
        self.birthdate.SetDate(p.birthdate)
        self.age.SetBirthdate(p.birthdate)
        self.birthdate_text.SetDate(p.birthdate)
        self.address.ChangeValue(otf.check_none(p.address))
        self.phone.ChangeValue(otf.check_none(p.phone))
        self.past_history.ChangeValue(otf.check_none(p.past_history))

    def onOkBtn(self, e):
        if self.is_valid():
            p = self.mv.state.patient
            assert p is not None
            name: str = self.name.Value
            p.name = name.strip().upper()
            p.gender = self.gender.GetGender()
            p.birthdate = self.birthdate.GetDate()
            p.address = otf.check_blank(self.address.Value)
            p.phone = otf.check_blank(self.phone.Value)
            p.past_history = otf.check_blank(self.past_history.Value)
            try:
                self.mv.con.update(p)
                wx.MessageBox("Cập nhật thành công", "OK")
                page: wx.ListCtrl = self.mv.patient_book.GetCurrentPage()
                idx: int = page.GetFirstSelected()
                self.mv.state.queuelist = self.mv.state.get_queuelist()
                self.mv.state.todaylist = self.mv.state.get_todaylist()
                page.EnsureVisible(idx)
                page.Select(idx)
                e.Skip()
            except sqlite3.Error as error:
                wx.MessageBox(f"Lỗi không cập nhật được\n{error}", "Lỗi")
