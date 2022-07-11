import wx
import datetime as dt
from fractions import Fraction
from typing import Any, TypeVar
import decimal

def bd_to_age(bd: dt.date):
    today = dt.date.today()
    delta = (today - bd).days
    if delta <= 60:
        age = f'{delta} ngày tuổi'
    elif delta <= (30 * 24):
        age = f'{int(delta / 30)} tháng tuổi'
    else:
        age = f'{today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))} tuổi'
    return age


def only_nums(e:wx.KeyEvent, decimal=False, tab=True, slash=False):
    # print(e.KeyCode)
    # back, del, home, end, left,right
    s =  e.GetEventObject().GetValue()
    special = [8, 314, 316, 127, 313, 312]
    if decimal:
        if '/' not in s and '.' not in s:
            special.append(46)
    if tab:
        special.append(9)
    if slash:
        if '.' not in s and '/' not in s:
            special.append(47)
    if e.KeyCode in list(range(48, 58)) + special:
        e.Skip()


def get_usage_note_str(usage, times, dose, usage_unit):
    return f"{usage} ngày {times} lần, lần {dose} {usage_unit}"


def check_blank(val: str):
    return None if val.strip() == '' else val.strip()


def check_none(val: Any|None):
    return str(val) if val else ''


def calc_quantity(times, dose, days, sale_unit, list_of_unit):
    def calc(times, dose, days):
        if '/' in dose:
            numer, denom = [int(i) for i in dose.split('/')]
            dose = Fraction(numer, denom)
            return round(times * dose * days)
        else:
            return round(times * float(dose) * days)
    try:
        if sale_unit is not None:
            if sale_unit.casefold() in [item.casefold() for item in list_of_unit]:
                return 1
            else:
                return calc(times, dose, days)
        else:
            return calc(times, dose, days)
    except Exception as e:
        print(e)
        return None


TC = TypeVar('TC', bound=wx.TextCtrl)


def disable_text_ctrl(w: TC) -> TC:
    w.Disable()
    w.SetBackgroundColour(wx.Colour(168, 168, 168))
    w.SetForegroundColour(wx.Colour(0, 0, 0))
    return w


def check_mainview_filled(diagnosis: str, weight: decimal.Decimal) -> bool:
    if diagnosis.strip() == '':
        wx.MessageBox("Chưa nhập chẩn đoán", "Lỗi")
        return False
    elif weight == 0:
        wx.MessageBox(f"Cân nặng = 0", "Lỗi")
        return False
    else:
        return True