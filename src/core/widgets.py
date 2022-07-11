from db.db_class import *
import core.other_func as otf
from core import mainview
from core.mainview_books.order_book_pages.prescription import page
from core.initialize import k_number, k_special, k_decimal, k_hash, k_slash
from core.printing.printer import PrintOut, printdata
from path_init import weight_bm

import wx
import wx.adv
import datetime as dt
from itertools import cycle
from typing import Any
import sqlite3

# Generic


class DatePicker(wx.adv.CalendarCtrl):
    def __init__(self, parent: wx.Window):
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
    def __init__(self, parent: wx.Window):
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

    def SetDate(self, date: dt.date):
        self.ChangeValue(date.strftime(self.format))

    def is_valid(self) -> bool:
        try:
            dt.datetime.strptime(self.GetValue(), self.format)
            return True
        except ValueError:
            return False


class AgeCtrl(wx.TextCtrl):
    def __init__(self, parent: wx.Window):
        super().__init__(parent, style=wx.TE_READONLY)

    def SetBirthdate(self, bd: dt.date):
        self.SetValue(otf.bd_to_age(bd))


class GenderChoice(wx.Choice):
    def __init__(self, parent: wx.Window):
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
    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in k_number + k_special + k_decimal + k_hash:
            e.Skip()


class NumTextCtrl(wx.TextCtrl):
    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in k_number:
            e.Skip()


class WeightCtrl(wx.SpinCtrlDouble):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent)
        self.SetDigits(1)
        self.Disable()

    def GetWeight(self) -> Decimal:
        return Decimal(self.GetValue())

    def SetWeight(self, value: Decimal | int):
        super().SetValue(str(value))


class GetWeightBtn(wx.BitmapButton):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, bitmap=wx.Bitmap(weight_bm))
        self.mv = parent
        self.SetToolTip("Lấy cân nặng mới nhất")
        self.Bind(wx.EVT_BUTTON, self.onGetWeight)

    def onGetWeight(self, e):
        if self.mv.state.patient and (self.mv.visit_list.GetItemCount() > 0):
            self.mv.weight.SetWeight(self.mv.con.execute(f"""
                SELECT weight
                FROM visits
                WHERE (patient_id) = {self.mv.state.patient.id}
                ORDER BY exam_datetime DESC
                LIMIT 1
            """).fetchone()['weight'])


class DaysCtrl(wx.SpinCtrl):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"])
        self.mv = parent
        self.SetRange(0, 100)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin)
        self.Disable()

    def onSpin(self, e: wx.SpinEvent):
        self.mv.recheck.SetValue(e.GetPosition())


class RecheckCtrl(wx.SpinCtrl):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"])
        self.SetRange(0, 100)
        self.Disable()


class NoRecheck(wx.Button):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, label="Không tái khám")
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        self.mv.recheck.SetValue(0)


class UpdateQuantityBtn(wx.Button):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, label="Cập nhật lại số lượng thuốc trong toa theo ngày")
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        drug_list = self.mv.order_book.page0.drug_list
        for idx, item in enumerate(drug_list._list):
            q = otf.calc_quantity(
                times=item['times'],
                dose=item['dose'],
                days=self.mv.days.GetValue(),
                sale_unit=item['sale_unit'],
                list_of_unit=self.mv.config['thuoc_ban_mot_don_vi']
            )
            item['quantity'] = q
            drug_list.SetItem(
                idx, 4, f"{q} {item['sale_unit'] or item['usage_unit']}")
        self.mv.price.SetPrice()


class PriceCtrl(wx.TextCtrl):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent)
        self.mv = parent

    def SetPrice(self):
        lld = ((item['drug_id'], item['quantity'])
               for item in self.mv.order_book.page0.drug_list._list)
        price = 0
        for id, quantity in lld:
            wh = self.mv.state.get_wh_by_id(id)
            if wh:
                price += wh.sale_price * quantity

        price += self.mv.config['cong_kham_benh']
        s = str(price)
        res = ''
        for char, cyc in zip(s[::-1], cycle(range(3))):
            res += char
            if cyc == 2:
                res += '.'
        else:
            if res[-1] == '.':
                res = res[:-1]
            self.SetValue(res[::-1])


class Follow(wx.ComboBox):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(
            parent,
            style=wx.CB_DROPDOWN,
            choices=[f"{i}: {j}" for i,
                     j in parent.config['loi_dan_do'].items()]
        )
        self.mv = parent
        self.SetSelection(0)

    def SetFollow(self, val: str | None):
        if val is None:
            self.SetValue('')
        elif val in self.mv.config['loi_dan_do'].keys():
            self.SetValue(f"{val}: {self.mv.config['loi_dan_do'][val]}")
        else:
            self.SetValue(val)

    def GetFollow(self) -> str | None:
        val = self.GetValue().strip()
        if val == '':
            return None
        elif tuple(val.split(":", 1)) in self.mv.config['loi_dan_do'].items():
            return val.split(":", 1)[0]
        else:
            return val


class NewVisitBtn(wx.Button):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, label="Lượt khám mới")
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        idx = self.mv.visit_list.GetFirstSelected()
        self.mv.visit_list.Select(idx, 0)


class SaveBtn(wx.Button):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, label="Lưu")
        self.mv = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        if self.mv.state.visit:
            self.update_visit()
        else:
            self.insert_visit()

    def insert_visit(self):

        diagnosis: str = self.mv.diagnosis.GetValue().strip()
        weight = self.mv.weight.GetWeight()
        if otf.check_mainview_filled(diagnosis, weight):
            p = self.mv.state.patient
            assert p is not None
            past_history = otf.check_blank(self.mv.past_history.GetValue())
            v = {
                'diagnosis': diagnosis,
                'weight': weight,
                'days': self.mv.days.GetValue(),
                'recheck': self.mv.recheck.GetValue(),
                'patient_id': p.id,
                'vnote': otf.check_blank(self.mv.vnote.GetValue()),
                'follow': self.mv.follow.GetFollow(),
            }
            try:
                with self.mv.con as con:
                    con.execute(f"""
                        UPDATE {Patient.table_name} SET past_history = ?
                        WHERE id = {p.id}
                    """, (past_history,))
                    vid = con.execute(f"""
                        INSERT INTO {Visit.table_name} ({Visit.commna_joined_fields()})
                        VALUES ({Visit.named_style_fields()})
                    """, v).lastrowid
                    assert vid is not None
                    insert_ld = []
                    for item in self.mv.order_book.page0.drug_list._list:
                        insert_ld.append({
                            'drug_id': item['drug_id'],
                            'dose': item['dose'],
                            'times': item['times'],
                            'quantity': item['quantity'],
                            'visit_id': vid,
                            'note': item['note'],
                        })
                    con.executemany(f"""
                        INSERT INTO {LineDrug.table_name} ({LineDrug.commna_joined_fields()})
                        VALUES ({LineDrug.named_style_fields()})
                    """, insert_ld)
                    wx.MessageBox("Lưu lượt khám mới thành công",
                                  "Lưu lượt khám mới")
                    if wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO) == wx.YES:
                        printout = PrintOut(self.mv)
                        wx.Printer(
                            wx.PrintDialogData(printdata)
                        ).Print(self, printout, False)
                    self.mv.state.refresh()

            except sqlite3.IntegrityError as error:
                for a in error.args:
                    if a == "CHECK constraint failed: shortage":
                        wx.MessageBox("Lỗi hết thuốc trong kho", "Lỗi")
                    else:
                        wx.MessageBox(
                            f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")
            except Exception as error:
                wx.MessageBox(f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")

    def update_visit(self):
        diagnosis: str = self.mv.diagnosis.GetValue().strip()
        weight = self.mv.weight.GetWeight()
        if otf.check_mainview_filled(diagnosis, weight):
            p = self.mv.state.patient
            assert p is not None
            past_history = otf.check_blank(self.mv.past_history.GetValue())
            v = self.mv.state.visit
            assert v is not None
            v.diagnosis = diagnosis
            v.weight = self.mv.weight.GetWeight()
            v.days = self.mv.days.GetValue()
            v.recheck = self.mv.recheck.GetValue()
            v.vnote = otf.check_blank(self.mv.vnote.GetValue())
            v.follow = self.mv.follow.GetFollow()
            update_ld = []
            update_id = []
            update_drug_id = []
            insert_ld = []
            delete_ld = []
            drug_list = self.mv.order_book.page0.drug_list._list
            lld = self.mv.state.linedruglist
            # update same drug_id
            for to_be in drug_list:
                for origin in lld:
                    if to_be['drug_id'] == origin['drug_id']:
                        update_ld.append((
                            to_be['dose'],
                            to_be['times'],
                            to_be['quantity'],
                            to_be['note'],
                            origin['id'],
                        ))
                        update_id.append(origin['id'])
                        update_drug_id.append(origin['drug_id'])
            # delete those in lld but not in update
            for origin in lld:
                if origin['id'] not in update_id:
                    delete_ld.append((origin['id'],))
            # insert those in drug_list but not in update
            for to_be in drug_list:
                if to_be['drug_id'] not in update_drug_id:
                    insert_ld.append({
                        'drug_id': to_be['drug_id'],
                        'dose': to_be['dose'],
                        'times': to_be['times'],
                        'quantity': to_be['quantity'],
                        'visit_id': v.id,
                        'note': to_be['note'],
                    })
            try:
                with self.mv.con as con:
                    con.execute(f"""
                        UPDATE {Patient.table_name} SET past_history = ?
                        WHERE id = {p.id}
                    """, (past_history,))
                    con.execute(f"""
                        UPDATE {Visit.table_name} SET ({Visit.commna_joined_fields()})
                        = ({Visit.qmark_style_fields()})
                        WHERE id = {v.id}
                    """, v.into_sql_args())
                    con.executemany(f"""
                        UPDATE {LineDrug.table_name}
                        SET (dose, times, quantity, note) = (?,?,?,?)
                        WHERE id=?
                    """, update_ld)
                    con.executemany(
                        f"DELETE FROM {LineDrug.table_name} WHERE id = ?",
                        delete_ld)
                    con.executemany(f"""
                        INSERT INTO {LineDrug.table_name} ({LineDrug.commna_joined_fields()})
                        VALUES ({LineDrug.named_style_fields()})
                    """, insert_ld)

                wx.MessageBox("Cập nhật lượt khám thành công",
                              "Cập nhật lượt khám")
                if wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO) == wx.YES:
                    printout = PrintOut(self.mv)
                    wx.Printer(wx.PrintDialogData(printdata)
                               ).Print(self, printout, False)
                self.mv.state.refresh()
            except sqlite3.IntegrityError as error:
                for a in error.args:
                    if a == "CHECK constraint failed: shortage":
                        wx.MessageBox("Lỗi hết thuốc trong kho", "Lỗi")
                    else:
                        wx.MessageBox(
                            f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")
            except Exception as error:
                wx.MessageBox(f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")