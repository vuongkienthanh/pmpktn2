from core.initialize import k_number, k_special, k_decimal, k_hash, k_slash
import core.other_func as otf
from db.db_class import *
from core.printing.printer import PrintOut, printdata
from path_init import weight_bm

import wx
import wx.adv
import datetime as dt
from decimal import Decimal
import decimal
from itertools import cycle
from typing import TypeVar

TC = TypeVar('TC', bound=wx.TextCtrl)


def disable_text_ctrl(w: TC) -> TC:
    w.Disable()
    w.SetBackgroundColour(wx.Colour(168, 168, 168))
    w.SetForegroundColour(wx.Colour(0, 0, 0))
    return w


class DatePicker(wx.adv.CalendarCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.adv.CAL_MONDAY_FIRST |
                         wx.adv.CAL_SHOW_SURROUNDING_WEEKS)

    def GetDate(self) -> dt.date:
        return wx.wxdate2pydate(super().GetDate()).date()

    def SetDate(self, date: dt.date) -> None:
        has_range, lower_bound, upper_bound = self.GetDateRange()
        if has_range:
            lower_bound = wx.wxdate2pydate(lower_bound).date()
            upper_bound = wx.wxdate2pydate(upper_bound).date()
            if date > upper_bound:
                date = upper_bound
            elif date < lower_bound:
                date = lower_bound
        super().SetDate(wx.pydate2wxdate(date))


class DateTextCtrl(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetHint("DD/MM/YYYY")
        self.format = "%d/%m/%Y"
        self.bg = self.GetBackgroundColour()
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        s = e.GetEventObject().GetValue()
        if e.KeyCode in k_special:
            e.Skip()
        elif e.KeyCode in k_number + k_slash and len(s) < 10:
            if e.KeyCode == 47:
                if s.count('/') < 2:
                    e.Skip()
            else:
                e.Skip()

    def GetDate(self) -> dt.date:
        return dt.datetime.strptime(self.GetValue(), self.format).date()

    def ChangeDate(self, date: dt.date):
        self.ChangeValue(date.strftime(self.format))

    def is_valid(self) -> bool:
        try:
            dt.datetime.strptime(self.GetValue(), self.format)
            return True
        except ValueError:
            return False


class AgeCtrl(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TE_READONLY)
        self.Disable()

    def SetBirthdate(self, bd: dt.date):
        today = dt.date.today()
        delta = (today - bd).days
        if delta <= 60:
            age = f'{delta} ngày tuổi'
        elif delta <= (30 * 24):
            age = f'{int(delta / 30)} tháng tuổi'
        else:
            age = f'{today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))} tuổi'
        self.SetValue(age)


class GenderChoice(wx.Choice):
    def __init__(self, parent):
        super().__init__(parent, choices=[
            str(Gender(0)),
            str(Gender(1))
        ])
        self.Selection = 0

    def GetGender(self) -> Gender:
        return Gender(self.Selection)

    def SetGender(self, gender: Gender):
        self.SetSelection(gender.value)


class PhoneTextCtrl(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in k_number + k_special + k_decimal + k_hash:
            e.Skip()


class NumTextCtrl(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in k_number:
            e.Skip()


class WeightCtrl(wx.SpinCtrlDouble):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetDigits(1)
        self.Disable()

    def GetValue(self):
        if super().GetValue() == 0:
            raise decimal.InvalidOperation("Cân nặng bằng 0")
        return Decimal(super().GetValue())

    def SetValue(self, value: Decimal | int):
        super().SetValue(str(value))


class DaysCtrl(wx.SpinCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"])
        self.SetRange(0, 200)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin)
        self.Disable()

    def onSpin(self, e):
        self.Parent.recheck.SetValue(e.GetPosition())


class RecheckCtrl(wx.SpinCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"])
        self.SetRange(0, 200)
        self.Disable()


class NoRecheck(wx.Button):
    def __init__(self, parent):
        super().__init__(parent, label="Không tái khám")
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        self.Parent.recheck.SetValue(0)


class UpdateQuantityBtn(wx.Button):
    def __init__(self, parent):
        super().__init__(parent, label="Cập nhật lại số lượng thuốc trong toa theo ngày")
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        drug_list = self.Parent.order_book.GetPage(0).drug_list
        for idx, item in enumerate(drug_list._list):
            q = otf.calc_quantity(
                times=item['times'],
                dose=item['dose'],
                days=self.Parent.days.GetValue(),
                sale_unit=item['sale_unit'],
                list_of_unit=self.Parent.config['thuoc_ban_mot_don_vi']
            )
            item['quantity'] = q
            drug_list.SetItem(
                idx, 4, f"{q} {item['sale_unit'] or item['usage_unit']}")
        self.Parent.price.set_price()


class PriceCtrl(wx.TextCtrl):

    def set_price(self):
        lld = ((item['drug_id'], item['quantity'])
               for item in self.Parent.order_book.GetPage(0).drug_list._list)
        price = 0
        for id, quantity in lld:
            wh = self.Parent.state.get_wh_by_id(id)
            price += wh.sale_price * quantity

        price += self.Parent.config['cong_kham_benh']
        self.SetValue(price)

    def SetValue(self, p: int):
        s = str(p)
        res = ''
        for c, j in zip(s[::-1], cycle(range(3))):
            res += c
            if j == 2:
                res += '.'
        else:
            if res[-1] == '.':
                res = res[:-1]
        super().SetValue(res[::-1])


class Follow(wx.ComboBox):
    def __init__(self, parent):
        super().__init__(
            parent,
            style=wx.CB_DROPDOWN,
            choices=[f"{i}: {j}" for i,
                     j in parent.config['loi_dan_do'].items()]
        )

    def SetValue(self, val):
        if val is None:
            super().SetValue('')
        elif val in self.Parent.config['loi_dan_do'].keys():
            super().SetValue(f"{val}: {self.Parent.config['loi_dan_do'][val]}")
        else:
            super().SetValue(val)

    def GetValue(self):
        val = super().GetValue()
        if val == '':
            return None
        elif tuple(val.split(":")) in self.Parent.config['loi_dan_do'].items():
            return val.split(":")[0]
        else:
            return val


class GetWeightBtn(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent, bitmap=wx.Bitmap(weight_bm))
        self.SetToolTip("Lấy cân nặng mới nhất")
        self.Bind(wx.EVT_BUTTON, self.onGetWeight)

    def onGetWeight(self, e):
        mv = self.Parent
        if mv.state.patient and (self.Parent.visit_list.GetItemCount() > 0):
            mv.weight.SetValue(mv.con.execute(f"""
                SELECT weight
                FROM visits
                WHERE (patient_id) = {mv.state.patient.id}
                ORDER BY exam_datetime DESC
                LIMIT 1
            """).fetchone()['weight'])


class NewVisitBtn(wx.Button):
    def __init__(self, parent):
        super().__init__(parent, label="Lượt khám mới")
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        idx = self.Parent.visit_list.GetFirstSelected()
        self.Parent.visit_list.Select(idx, 0)


class SaveBtn(wx.Button):
    def __init__(self, parent):
        super().__init__(parent, label="Lưu")
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        if self.Parent.state.visit:
            self.update_visit()
        else:
            self.insert_visit()

    def insert_visit(self):
        try:
            diagnosis = self.Parent.diagnosis.GetValue().strip()
            if diagnosis == '':
                raise ValueError
            p = self.Parent.state.patient
            p.past_history = self.Parent.past_history.GetValue().strip()
            v = Visit(
                diagnosis=diagnosis,
                weight=self.Parent.weight.GetValue(),
                days=self.Parent.days.GetValue(),
                recheck=self.Parent.recheck.GetValue(),
                patient_id=p.id,
                vnote=otf.check_blank(self.Parent.vnote.GetValue()),
                follow=self.Parent.follow.GetValue()
            )
            with self.Parent.con as con:
                con.execute(f"""
                    UPDATE patients SET past_history = ?
                    WHERE id = {p.id}
                """, (p.past_history,))
                vid = con.execute(f"""
                    INSERT INTO visits ({Visit.fields_as_str()})
                    VALUES ({Visit.fields_as_qmarks()})
                """, v.into_sql_args()).lastrowid
                insert_ld = []
                for item in self.Parent.order_book.GetPage(0).drug_list._list:
                    insert_ld.append(LineDrug(
                        drug_id=item['drug_id'],
                        dose=item['dose'],
                        times=item['times'],
                        quantity=item['quantity'],
                        visit_id=vid,
                        note=item['note'],
                    ))

                con.executemany(f"""
                    INSERT INTO linedrugs ({LineDrug.fields_as_str()})
                    VALUES ({LineDrug.fields_as_qmarks()})
                """, (ld.into_sql_args() for ld in insert_ld))
            wx.MessageBox("Lưu lượt khám mới thành công", "Lưu lượt khám mới")
            if wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO) == wx.YES:
                printout = PrintOut(self.Parent)
                wx.Printer(wx.PrintDialogData(printdata)
                           ).Print(self, printout, False)
            self.Parent.refresh()
        except ValueError as e:
            wx.MessageBox("Chưa nhập chẩn đoán", "Lỗi")
        except decimal.InvalidOperation as e:
            wx.MessageBox(f"Nhập sai cân nặng\n{e}", "Lỗi")
        except sqlite3.IntegrityError as e:
            for a in e.args:
                if a == "CHECK constraint failed: shortage":
                    wx.MessageBox("Lỗi hết thuốc trong kho", "Lỗi")
                else:
                    wx.MessageBox(f"Lỗi không lưu lượt khám được\n{e}", "Lỗi")
        except Exception as e:
            wx.MessageBox(f"Lỗi không lưu lượt khám được\n{e}", "Lỗi")

    def update_visit(self):
        try:
            diagnosis = self.Parent.diagnosis.GetValue().strip()
            if diagnosis == '':
                raise ValueError
            p = self.Parent.state.patient
            p.past_history = self.Parent.past_history.GetValue().strip()
            v = self.Parent.state.visit
            v.diagnosis = diagnosis
            v.weight = self.Parent.weight.GetValue()
            v.days = self.Parent.days.GetValue()
            v.recheck = self.Parent.recheck.GetValue()
            v.vnote = otf.check_blank(self.Parent.vnote.GetValue())
            v.follow = self.Parent.follow.GetValue()
            update_ld = []
            update_id = []
            update_drug_id = []
            insert_ld = []
            delete_ld = []
            drug_list = self.Parent.order_book.GetPage(0).drug_list._list
            lld = self.Parent.state.linedruglist
            # update same drug_id
            for i in drug_list:
                for j in lld:
                    if i['drug_id'] == j['drug_id']:
                        update_ld.append((
                            i['dose'],
                            i['times'],
                            i['quantity'],
                            i['note'],
                            j['id'],
                        ))
                        update_id.append(j['id'])
                        update_drug_id.append(j['drug_id'])
            # delete those in lld but not in update
            for j in lld:
                if j['id'] not in update_id:
                    delete_ld.append((j['id'],))
            # insert those in drug_list but not in update
            for i in drug_list:
                if i['drug_id'] not in update_drug_id:
                    insert_ld.append(LineDrug(
                        drug_id=i['drug_id'],
                        dose=i['dose'],
                        times=i['times'],
                        quantity=i['quantity'],
                        visit_id=v.id,
                        note=i['note'],
                    ))

            with self.Parent.con as con:
                con.execute(f"""
                    UPDATE patients SET past_history = ?
                    WHERE id = {p.id}
                """, (p.past_history,))
                con.execute(f"""
                    UPDATE visits SET ({Visit.fields_as_str()})
                    = ({Visit.fields_as_qmarks()})
                    WHERE id = {v.id}
                """, v.into_sql_args())
                con.executemany("""
                    UPDATE linedrugs
                    SET (dose, times, quantity, note) = (?,?,?,?)
                    WHERE id=?
                """, update_ld)
                con.executemany(
                    "DELETE FROM linedrugs WHERE id = ?",
                    delete_ld)
                con.executemany(f"""
                    INSERT INTO linedrugs ({LineDrug.fields_as_str()})
                    VALUES ({LineDrug.fields_as_qmarks()})
                """, (ld.into_sql_args() for ld in insert_ld))

            wx.MessageBox("Cập nhật lượt khám thành công",
                          "Cập nhật lượt khám")
            if wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO) == wx.YES:
                printout = PrintOut(self.Parent)
                wx.Printer(wx.PrintDialogData(printdata)
                           ).Print(self, printout, False)
            self.Parent.refresh()
        except ValueError as e:
            wx.MessageBox("Chưa nhập chẩn đoán", "Lỗi")
        except decimal.InvalidOperation as e:
            wx.MessageBox(f"Nhập sai cân nặng\n{e}", "Lỗi")
        except sqlite3.IntegrityError as e:
            for a in e.args:
                if a == "CHECK constraint failed: shortage":
                    wx.MessageBox("Lỗi hết thuốc trong kho", "Lỗi")
                else:
                    wx.MessageBox(f"Lỗi không lưu lượt khám được\n{e}", "Lỗi")
        except Exception as e:
            wx.MessageBox(f"Lỗi không lưu lượt khám được\n{e}", "Lỗi")
