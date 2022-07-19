from core.initialize import k_number, k_special, k_tab, k_decimal, k_hash, k_slash
import core.other_func as otf
from db.db_class import Gender
import wx
import wx.adv
import datetime as dt
from decimal import Decimal


class GenderChoice(wx.Choice):
    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, choices=[
            str(Gender(0)),
            str(Gender(1))
        ], **kwargs)
        self.Selection = 0

    def GetGender(self) -> Gender:
        return Gender(self.Selection)

    def SetGender(self, gender: Gender):
        self.SetSelection(gender.value)


class WeightCtrl(wx.SpinCtrlDouble):
    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, **kwargs)
        self.SetDigits(1)
        self.Disable()

    def GetWeight(self) -> Decimal:
        return Decimal(self.GetValue())

    def SetWeight(self, value: Decimal | int):
        super().SetValue(str(value))


class DatePicker(wx.adv.CalendarCtrl):
    """Calendar
    - Used in patient dialog and warehouse new/edit dialog
    - No preset date range
    """

    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, style=wx.adv.CAL_MONDAY_FIRST |
                         wx.adv.CAL_SHOW_SURROUNDING_WEEKS, **kwargs)

    def GetDate(self) -> dt.date:
        return wx.wxdate2pydate(super().GetDate()).date()

    def checked_GetDate(self) -> dt.date | None:
        """Return None if `date` is today"""
        d = self.GetDate()
        if d == dt.date.today():
            return None
        else:
            return d

    def SetDate(self, d: dt.date):
        """SetDate within bound"""
        date: wx.DateTime = wx.pydate2wxdate(d)
        has_range: bool
        lower_bound: wx.DateTime
        upper_bound: wx.DateTime
        has_range, lower_bound, upper_bound = self.GetDateRange()
        if has_range:
            if date.IsLaterThan(upper_bound):
                date = upper_bound
            elif date.IsEarlierThan(lower_bound):
                date = lower_bound
        super().SetDate(date)


class DateTextCtrl(wx.TextCtrl):
    """A TextCtrl with a datetime methods and char validation
    Used in MainView and  patient dialogs"""

    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, **kwargs)
        self.SetHint("DD/MM/YYYY")
        self.format = "%d/%m/%Y"
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        s: str = self.GetValue()
        kc: int = e.KeyCode
        if kc in k_special:
            e.Skip()
        elif kc in k_number + k_slash and len(s) < 10:
            if kc == k_slash:
                if s.count('/') < 2:
                    e.Skip()
            else:
                e.Skip()

    def GetDate(self) -> dt.date:
        val: str = self.GetValue()
        return dt.datetime.strptime(val, self.format).date()

    def SetDate(self, date: dt.date):
        self.ChangeValue(date.strftime(self.format))

    def is_valid(self) -> bool:
        """Check if text value follows format"""
        try:
            val: str = self.GetValue()
            dt.datetime.strptime(val, self.format)
            return True
        except ValueError:
            return False


class AgeCtrl(wx.TextCtrl):
    """Used in MainView and patient dialogs"""

    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, style=wx.TE_READONLY, **kwargs)

    def SetBirthdate(self, bd: dt.date):
        """Change value based on `bd`"""
        self.ChangeValue(otf.bd_to_age(bd))


class NumberTextCtrl(wx.TextCtrl):
    """ A TextCtrl which allows number"""

    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, **kwargs)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def key_list(self):
        return k_number + k_tab + k_special

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in self.key_list():
            e.Skip()


class PhoneTextCtrl(NumberTextCtrl):
    """ A NumberTextCtrl which also allows hash and decimal """

    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, **kwargs)

    def key_list(self):
        return super().key_list() + k_decimal + k_hash


class DoseTextCtrl(NumberTextCtrl):
    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, **kwargs)

    def key_list(self):
        s: str = self.Value
        ret = super().key_list()
        if '/' not in s and '.' not in s:
            ret = ret + k_slash + k_decimal
        return ret
