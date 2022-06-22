import core.other_func as otf
from db.db_class import *
from core.printing.printer import PrintOut, printdata
from path_init import weight_bm

import wx
from decimal import Decimal
import decimal
from itertools import cycle


class DisabledTextCtrl(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TE_READONLY)
        self.Disable()
        self.SetBackgroundColour(wx.Colour(168, 168, 168))
        self.SetForegroundColour(wx.Colour(0, 0, 0))


class WeightCtrl(wx.SpinCtrlDouble):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetDigits(1)

    def GetValue(self):
        if super().GetValue() == 0:
            raise decimal.InvalidOperation("Cân nặng bằng 0")
        return Decimal(super().GetValue())

    def SetValue(self, value: Decimal):
        super().SetValue(str(value))


class DaysCtrl(wx.SpinCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"])
        self.SetRange(0, 200)


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
                list_unit=self.Parent.config['thuoc_ban_mot_don_vi']
            )
            item['quantity'] = q
            drug_list.SetItem(
                idx, 4, f"{q} {item['sale_unit'] or item['usage_unit']}")


class PriceCtrl(DisabledTextCtrl):

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
            v = VisitWithoutTime(
                diagnosis=diagnosis,
                weight=self.Parent.weight.GetValue(),
                days=self.Parent.days.GetValue(),
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
                    INSERT INTO visits ({VisitWithoutTime.fields_as_str()})
                    VALUES ({VisitWithoutTime.fields_as_qmarks()})
                """, v.into_sql_args()).lastrowid
                insert_ld = []
                for item in self.Parent.order_book.GetPage(0).drug_list._list:
                    insert_ld.append(Linedrug(
                        drug_id=item['drug_id'],
                        dose=item['dose'],
                        times=item['times'],
                        quantity=item['quantity'],
                        visit_id=vid,
                        note=item['note'],
                    ))

                con.executemany(f"""
                    INSERT INTO linedrugs ({Linedrug.fields_as_str()})
                    VALUES ({Linedrug.fields_as_qmarks()})
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
                    insert_ld.append(Linedrug(
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
                    INSERT INTO linedrugs ({Linedrug.fields_as_str()})
                    VALUES ({Linedrug.fields_as_qmarks()})
                """, (ld.into_sql_args() for ld in insert_ld))

            wx.MessageBox("Cập nhật lượt khám thành công",
                          "Cập nhật lượt khám")
            if wx.MessageBox("In toa về?", "In toa", style=wx.YES_DEFAULT | wx.NO) == wx.YES:
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
