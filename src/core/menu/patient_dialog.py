from db.db_class import Patient, Patient, QueueList, QueueList
import core.other_func as otf
from core import mainview
from core.widgets import DatePicker, GenderChoice, PhoneTextCtrl, DateTextCtrl, AgeCtrl
import sqlite3
import wx
import wx.adv as adv
from typing import Any


class BasePatientDialog(wx.Dialog):
    def __init__(self, parent:'mainview.MainView', title):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.locale = wx.Locale(wx.LANGUAGE_VIETNAMESE)
        self.mv = parent

        self.name = wx.TextCtrl(self, size=(300, -1))
        self.gender = GenderChoice(self)
        # birthdate group
        self.birthdate_text = DateTextCtrl(self)
        self.birthdate = DatePicker(self)
        self.birthdate.SetDateRange(
            wx.DateTime.Today() - wx.DateSpan(years=100),
            wx.DateTime.Today()
        )
        self.age = otf.disable_text_ctrl(AgeCtrl(self))
        self.birthdate_text.Bind(wx.EVT_TEXT, self.onBirthdateText)
        self.birthdate.Bind(adv.EVT_CALENDAR_SEL_CHANGED, self.onBirthdate)

        self.address = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.phone = PhoneTextCtrl(self)
        self.past_history = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.okbtn = wx.Button(self, id=wx.ID_OK)
        self._setSizer()
        self.okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onOkBtn(self, e) -> None: ...

    def onClose(self, e):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        e.Skip()

    def onBirthdateText(self, e:wx.CommandEvent):
        s = e.GetString()
        if len(s) == 10 and self.birthdate_text.is_valid():
            date = self.birthdate_text.GetDate()
            self.birthdate.SetDate(date)
            self.age.SetBirthdate(date)
            e.Skip()
        else:
            self.birthdate_text.SetToolTip("Sai ngày sinh")

    def onBirthdate(self, e:adv.CalendarEvent):
        date = self.birthdate.GetDate()
        self.age.SetBirthdate(date)
        self.birthdate_text.SetDate(date)
        e.Skip()

    def get_patient(self) -> dict[str, Any]:
        return {
            'name' : self.name.Value.strip().upper(),
            'gender' : self.gender.GetGender(),
            'birthdate' : self.birthdate.GetDate(),
            'address' : otf.check_blank(self.address.Value),
            'phone' : otf.check_blank(self.phone.Value),
            'past_history' : otf.check_blank(self.past_history.Value)
        }
    
    def is_valid(self) -> bool:
        return all([
            self.name.Value.strip() != '',
            self.birthdate_text.is_valid()
        ])
    
    def show_error(self):
        if self.name.Value.strip() == '':
            wx.MessageBox("Chưa nhập tên bệnh nhân", "Lỗi")
        elif self.birthdate_text.Value.strip() == '':
            wx.MessageBox("Chưa nhập ngày sinh", "Lỗi")

    def _setSizer(self):

        def static(s):
            return (wx.StaticText(self, label=s), 1, wx.ALIGN_CENTER_VERTICAL)

        def widget(s):
            return (s, 10, wx.EXPAND)
        entry = wx.FlexGridSizer(rows=8, cols=2, vgap=5, hgap=2)
        entry.AddGrowableCol(1, 1)
        entry.AddGrowableRow(5, 1)
        entry.AddGrowableRow(7, 1)
        entry.AddMany([
            static("Họ tên*"),
            widget(self.name),
            static("Giới*"),
            widget(self.gender),
            static("Ngày sinh*"),
            widget(self.birthdate_text),
            static("Tuổi:"),
            widget(self.age),
            (0, 0, 0, wx.EXPAND),
            widget(self.birthdate),
            static("Địa chỉ"),
            widget(self.address),
            static('Điện thoại'),
            widget(self.phone),
            static('Bệnh nền, dị ứng'),
            widget(self.past_history),
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


class NewPatientDialog(BasePatientDialog):

    def __init__(self, parent:'mainview.MainView'):
        super().__init__(parent, title="Bệnh nhân mới")

    def onOkBtn(self, e):
        if not self.is_valid():
            self.show_error()
        else:
            try:
                p = self.get_patient()
                res = self.mv.con.insert(Patient, p)
                assert res is not None
                lastrowid, _ = res
                wx.MessageBox("Đã thêm bệnh nhân mới thành công",
                              "Bệnh nhân mới")
                if wx.MessageDialog(
                    self,
                    message="Thêm bệnh nhân mới vào danh sách chờ khám?",
                    caption="Danh sách chờ khám",
                    style=wx.OK_DEFAULT | wx.CANCEL
                ).ShowModal() == wx.ID_OK:
                    self.mv.con.insert(
                        QueueList, {'patient_id':lastrowid})
                    wx.MessageBox(
                        "Thêm vào danh sách chờ thành công", "OK")
                    self.mv.state.refresh()
                e.Skip()
            except sqlite3.IntegrityError as error:
                wx.MessageBox(
                    f"Đã có tên trong danh sách chờ.\n{error}", "Lỗi")
            except Exception as error:
                wx.MessageBox(f"Lỗi không thêm bệnh nhân mới được\n{error}", "Lỗi")


class EditPatientDialog(BasePatientDialog):

    def __init__(self, parent:'mainview.MainView', p:Patient):
        super().__init__(parent, title="Cập nhật thông tin bệnh nhân")
        self.p = p
        self.build()

    def build(self):
        self.name.ChangeValue(self.p.name)
        self.gender.SetGender(self.p.gender)
        self.birthdate.SetDate(self.p.birthdate)
        self.age.SetBirthdate(self.p.birthdate)
        self.birthdate_text.SetDate(self.p.birthdate)
        self.address.ChangeValue(otf.check_none(self.p.address ))
        self.phone.ChangeValue(otf.check_none(self.p.phone))
        self.past_history.ChangeValue(otf.check_none(self.p.past_history))

    def onOkBtn(self, e):
        if not self.is_valid():
            self.show_error()
        else:
            patient = self.get_patient()
            patient['id'] =self.p.id

            try:
                self.mv.con.update(Patient(**patient))
                wx.MessageBox("Cập nhật thành công", "OK")
                self.mv.state.refresh()
                e.Skip()
            except sqlite3.Error as error:
                wx.MessageBox(f"Lỗi không cập nhật được\n{error}", "Lỗi")
