from core.initialize import k_number, k_special, k_tab, k_decimal, k_hash, k_slash
import core.other_func as otf
from db.db_class import *
import wx
import wx.adv
import datetime as dt
from itertools import cycle


class DatePicker(wx.adv.CalendarCtrl):
    """ Calendar
    - Used in patient dialog and warehouse new/edit dialog
    - No preset date range
    """

    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, style=wx.adv.CAL_MONDAY_FIRST |
                         wx.adv.CAL_SHOW_SURROUNDING_WEEKS, **kwargs)

    def GetDate(self) -> dt.date:
        return wx.wxdate2pydate(super().GetDate()).date()

    def checked_GetDate(self) -> dt.date | None:
        """ Return None if `date` is today """
        d = self.GetDate()
        if d == dt.date.today():
            return None
        else:
            return d

    def SetDate(self, d: dt.date):
        """ SetDate within bound """
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
    """ A TextCtrl with a datetime methods and char validation """

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
        """ Check if text value follows format """
        try:
            val: str = self.GetValue()
            dt.datetime.strptime(val, self.format)
            return True
        except ValueError:
            return False


class AgeCtrl(wx.TextCtrl):
    def __init__(self, parent: wx.Window, **kwargs):
        super().__init__(parent, style=wx.TE_READONLY, **kwargs)

    def SetBirthdate(self, bd: dt.date):
        """ Change value based on `bd` """
        self.ChangeValue(otf.bd_to_age(bd))


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


class Follow(wx.ComboBox):
    """A Combobox which is able to return None if conditions met"""

    def __init__(self, parent: wx.Window, choice_dict: dict[str, str], **kwargs):
        super().__init__(
            parent,
            style=wx.CB_DROPDOWN,
            choices=[f"{i}: {j}" for i, j in choice_dict.items()],
            **kwargs
        )
        self.choice_dict = choice_dict
        self.SetSelection(0)

    def SetFollow(self, val: str | None):
        if val is None:
            self.SetValue('')
        elif val in self.choice_dict.keys():
            self.SetValue(f"{val}: {self.choice_dict[val]}")
        else:
            self.SetValue(val)

    def GetFollow(self) -> str | None:
        val: str = self.GetValue().strip()
        k, v = tuple(val.split(":", 1))
        if val == '':
            return None
        elif (k, v) in self.choice_dict.items():
            return k
        else:
            return val


class PriceTextCtrl(wx.TextCtrl):
    """A TextCtrl with proper Vietnamese currency format with default set according to config"""

    def __init__(self, parent: wx.Window, initial: int, **kwargs):
        super().__init__(parent, **kwargs)
        self.initial = initial
        self.clear()

    def add(self, price: int):
        self.ChangeValue(self.num_to_str(price + self.initial))

    def num_to_str(self, price: int) -> str:
        """Return proper currency format str from int"""
        s = str(price)
        res = ''
        for char, cyc in zip(s[::-1], cycle(range(3))):
            res += char
            if cyc == 2:
                res += '.'
        else:
            if res[-1] == '.':
                res = res[:-1]
        return res[::-1]

    def clear(self):
        self.ChangeValue(self.num_to_str(self.initial))

    def update_initial(self, new_initial: int):
        self.initial = new_initial
