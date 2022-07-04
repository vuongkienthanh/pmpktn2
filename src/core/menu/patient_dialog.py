from core.initialize import *
from db.db_class import Gender, Patient, QueueList, QueueListWithoutTime
import core.other_func as otf

import datetime as dt
import wx.adv as wxadv
import wx
import sqlite3


class MyDatePicker(wxadv.CalendarCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wxadv.CAL_MONDAY_FIRST |
                         wxadv.CAL_SHOW_SURROUNDING_WEEKS)
        self.SetDateRange(
            wx.DateTime.Today() - wx.DateSpan(years=100),
            wx.DateTime.Today()
        )

    def GetDate(self) -> dt.date:
        return wx.wxdate2pydate(super().GetDate()).date()

    def SetDate(self, date: dt.date) -> None:
        super().SetDate(wx.pydate2wxdate(date))


class BasePatientDialog(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.locale = wx.Locale(wx.LANGUAGE_VIETNAMESE)

        self.name = wx.TextCtrl(self, size=(300, -1))
        self.gender = wx.Choice(self, choices=[
            str(Gender(0)),
            str(Gender(1))
        ])
        self.gender.Selection = 0
        self.birthdate_text = wx.TextCtrl(self)
        self.birthdate_text.SetHint("DD/MM/YYYY")
        self.birthdate = MyDatePicker(self)
        self.age = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.age.Disable()
        self.birthdate_text.Bind(wx.EVT_TEXT, self.onBirthdateText)
        self.birthdate_text.Bind(
            wx.EVT_CHAR, lambda e: otf.only_nums(e, slash=True))
        self.birthdate.Bind(wxadv.EVT_CALENDAR, self.onBirthdate)
        self.address = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.phone = wx.TextCtrl(self)
        self.phone.Bind(wx.EVT_CHAR, lambda e: otf.only_nums(e, decimal=True))
        self.past_history = wx.TextCtrl(
            self, style=wx.TE_MULTILINE)

        self._setSizer()
        self._bindOkBtn()
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onOkBtn(self, e) -> None: ...

    def onClose(self, e):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        e.Skip()

    def onBirthdateText(self, e):
        s = e.GetString()
        if len(s) == 10:
            d, m, y = self.birthdate_text.GetValue().split("/")
            bd = wx.DateTime.FromDMY(int(d), int(m), int(y))
            _, lower, upper = self.birthdate.GetDateRange()
            if bd > upper:
                bd = upper
            if bd < lower:
                bd = lower
            bd = wx.wxdate2pydate(bd).date()
            self.birthdate.SetDate(bd)
            self.age.ChangeValue(otf.bd_to_age(bd))
            e.Skip()

    def onBirthdate(self, e):
        self.age.ChangeValue(otf.bd_to_age(self.birthdate.GetDate()))
        self.birthdate_text.ChangeValue(
            self.birthdate.GetDate().strftime("%d/%m/%Y"))
        e.Skip()

    def get_patient(self):
        return Patient(
            name=self.name.Value.upper(),
            gender=Gender(self.gender.Selection),
            birthdate=self.birthdate.GetDate(),
            address=otf.check_blank(self.address.Value),
            phone=otf.check_blank(self.phone.Value),
            past_history=otf.check_blank(self.past_history.Value)
        )

    def _setSizer(self):

        def static(s):
            return (wx.StaticText(self, label=s), 1, wx.ALIGN_CENTER_VERTICAL)

        def widget(s):
            return (s, 10, wx.EXPAND)
        entry_sizer = wx.FlexGridSizer(rows=8, cols=2, vgap=5, hgap=2)
        entry_sizer.AddGrowableCol(1, 3)
        entry_sizer.AddGrowableRow(5, 3)
        entry_sizer.AddGrowableRow(7, 3)
        entry_sizer.AddMany([
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
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry_sizer, 6, wx.ALL | wx.EXPAND, 10),
            (wx.StaticText(self, label="* là bắt buộc"), 0, wx.EXPAND | wx.ALL, 5),
            (self.CreateStdDialogButtonSizer(
                wx.OK | wx.CANCEL), 1, wx.ALL | wx.EXPAND, 10)
        ])
        self.SetSizerAndFit(sizer)

    def _bindOkBtn(self):
        for i in range(4, 0, -1):
            btn = self.Sizer.Children[2].Sizer.Children[i].Window
            if (btn is not None) and (btn.Id == wx.ID_OK):
                btn.Bind(wx.EVT_BUTTON, self.onOkBtn)


class NewPatientDialog(BasePatientDialog):

    def __init__(self, parent):
        super().__init__(parent, title="Bệnh nhân mới")

    def onOkBtn(self, e):
        if self.name.Value == ''.strip():
            wx.MessageBox("Chưa nhập tên bệnh nhân", "Lỗi")
        elif self.birthdate_text.Value.strip() == '':
            wx.MessageBox("Chưa nhập ngày sinh", "Lỗi")
        else:
            try:
                p = self.get_patient()
                lastrowid, _ = self.Parent.con.insert(p)
                wx.MessageBox("Đã thêm bệnh nhân mới thành công",
                              "Bệnh nhân mới")
                if wx.MessageDialog(
                    self,
                    message="Thêm bệnh nhân mới vào danh sách chờ khám?",
                    caption="Danh sách chờ khám",
                    style=wx.OK_DEFAULT | wx.CANCEL
                ).ShowModal() == wx.ID_OK:
                    self.Parent.con.insert(
                        QueueListWithoutTime(patient_id=lastrowid))
                    wx.MessageBox(
                        "Thêm vào danh sách chờ thành công", "OK")
                    self.Parent.refresh()
                e.Skip()
            except sqlite3.IntegrityError as error:
                wx.MessageBox(
                    f"Đã có tên trong danh sách chờ.\n{error}", "Lỗi")
            except Exception as e:
                wx.MessageBox(f"Lỗi không thêm bệnh nhân mới được\n{e}", "Lỗi")


class EditPatientDialog(BasePatientDialog):

    def __init__(self, parent, p):
        super().__init__(parent, title="Cập nhật thông tin bệnh nhân")
        self.p = p
        self.build()

    def build(self):
        self.name.ChangeValue(self.p.name)
        self.gender.Selection = self.p.gender.value
        self.birthdate.SetDate(self.p.birthdate)
        self.age.ChangeValue(otf.bd_to_age(self.p.birthdate))
        self.birthdate_text.ChangeValue(self.p.birthdate.strftime("%d/%m/%Y"))
        self.address.ChangeValue(self.p.address or '')
        self.phone.ChangeValue(self.p.phone or '')
        self.past_history.ChangeValue(self.p.past_history or '')

    def onOkBtn(self, e):
        patient = self.get_patient()
        patient.add_id(self.p.id)
        try:
            self.Parent.con.update(patient)
            wx.MessageBox("Cập nhật thành công", "OK")
            self.Parent.refresh()
            e.Skip()
        except sqlite3.Error as error:
            wx.MessageBox(f"Lỗi không cập nhật được\n{error}", "Lỗi")
