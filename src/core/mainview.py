from ath_init import weight_bm
from db.db_class import *
from db import db_func
from core.initialize import *
import core.other_func as otf
from core.printer import PrintOut, printdata
from core.state import State
from core.generic import *
from core.patient_book import PatientBook, VisitList
from core.order_book import OrderBook
from core.menubar import MyMenuBar
from core.accel import my_accel
from itertools import cycle
import sqlite3
import wx
from typing import Any


class MainView(wx.Frame):

    def __init__(self, con: 'db_func.Connection', config:dict[str,Any]):

        # config
        super().__init__(
            parent=None,
            title='PHẦN MỀM PHÒNG KHÁM TẠI NHÀ',
            pos=(10, 10),
            size=window_size)
        self.SetBackgroundColour(background_color)
        self.SetMinClientSize(window_size)

        # data
        self.con = con
        self.state = State(self)
        self.config = config

        # GUI
        self._createInterface()
        self.SetMenuBar(MyMenuBar())
        self.SetAcceleratorTable(my_accel)
        self._bind()
        self.start()

##########################################################################
##########################################################################
##########################################################################

    def _createInterface(self):
        self._createWidgets()
        self._setSizer()

    def _createWidgets(self):
        self._create_left_widgets()
        self._create_right_widgets()

    def _setSizer(self):

        left_sizer = self._create_left_sizer()
        right_sizer = self._create_right_sizer()

        whole_sizer = wx.BoxSizer(wx.HORIZONTAL)
        whole_sizer.Add(left_sizer, 4, wx.EXPAND)
        whole_sizer.Add(right_sizer, 6,
                        wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(whole_sizer)

    def _create_left_widgets(self):
        self.patient_book = PatientBook(self)
        self.visit_label = wx.StaticText(self, label='Lượt khám cũ:')
        self.visit_list = VisitList(self)

    def _create_left_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.patient_book, 10, wx.EXPAND | wx.LEFT | wx.TOP, 10)
        sizer.Add(self.visit_label, 0, wx.EXPAND | wx.LEFT, 20)
        sizer.Add(self.visit_list, 4, wx.EXPAND | wx.LEFT | wx.BOTTOM, 20)
        return sizer

    def _create_right_widgets(self):
        self.name = otf.disable_text_ctrl(wx.TextCtrl(self))
        self.gender = otf.disable_text_ctrl(wx.TextCtrl(self))
        self.birthdate = otf.disable_text_ctrl(DateTextCtrl(self))
        self.age = otf.disable_text_ctrl(AgeCtrl(self))
        self.phone = otf.disable_text_ctrl(PhoneTextCtrl(self))
        self.address = otf.disable_text_ctrl(wx.TextCtrl(self))
        self.past_history = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.diagnosis = wx.TextCtrl(self)
        self.vnote = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.weight = WeightCtrl(self)
        self.get_weight_btn = GetWeightBtn(self)
        self.days = DaysCtrl(self)
        self.updatequantitybtn = UpdateQuantityBtn(self)
        self.order_book = OrderBook(self)
        self.recheck = RecheckCtrl(self)
        self.norecheck = NoRecheckBtn(self)
        self.price = otf.disable_text_ctrl(PriceCtrl(self))
        self.follow = Follow(self, self.config['loi_dan_do'])
        self.newvisitbtn = NewVisitBtn(self)
        self.savebtn = SaveBtn(self)

    def _create_right_sizer(self):
        def static(s):
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER | wx.ALL, 2)

        def widget(w, p=0, r=5):
            return (w, p, wx.RIGHT, r)

        name_row = wx.BoxSizer(wx.HORIZONTAL)
        name_row.AddMany([
            static("Họ tên:"),
            widget(self.name, 3, 0),
            static("Giới:"),
            widget(self.gender, 1, 0),
            static("Ngày sinh:"),
            widget(self.birthdate, 2, 0),
            static("Tuổi:"),
            widget(self.age, 2, 0),
        ])
        addr_row = wx.BoxSizer(wx.HORIZONTAL)
        addr_row.AddMany([
            static("Địa chỉ:"),
            widget(self.address, 6),
            static("Điện thoại:"),
            widget(self.phone, 2, 0)
        ])

        diag_row = wx.BoxSizer(wx.HORIZONTAL)
        diag_row.AddMany([
            static("Chẩn đoán:"),
            widget(self.diagnosis, 1, 0)
        ])

        weight_row = wx.BoxSizer(wx.HORIZONTAL)
        weight_row.AddMany([
            static("Cân nặng (kg)"),
            widget(self.weight),
            widget(self.get_weight_btn),
            static("Số ngày cho toa"),
            widget(self.days),
            widget(self.updatequantitybtn)
        ])

        recheck_row = wx.BoxSizer(wx.HORIZONTAL)
        recheck_row.AddMany([
            static("Số ngày tái khám"),
            widget(self.recheck, 1),
            widget(self.norecheck),
            (0, 0, 3),
            static("Giá tiền"),
            widget(self.price, 1)

        ])

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddMany([
            widget(self.newvisitbtn),
            widget(self.savebtn),
        ])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (name_row, 0, wx.EXPAND),
            (addr_row, 0, wx.EXPAND),
            (wx.StaticText(self, label='Bệnh nền, dị ứng:')),
            (self.past_history, 1, wx.EXPAND),
            (diag_row, 0, wx.EXPAND),
            (wx.StaticText(self, label='Bệnh sử:')),
            (self.vnote, 1, wx.EXPAND),
            (weight_row, 0),
            (self.order_book, 3, wx.EXPAND),
            (recheck_row, 0, wx.EXPAND),
            (self.follow, 0, wx.EXPAND),
            (btn_row, 0, wx.EXPAND),

        ])
        return sizer
##########################################################################
##########################################################################
##########################################################################

    def _bind(self):
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, e:wx.CloseEvent):
        print("close sqlite3 connection")
        self.con.close()
        e.Skip()

    def start(self):
        self.patient_book.page0.build(self.state.queuelist)
        self.patient_book.page1.build(self.state.todaylist)



class GetWeightBtn(wx.BitmapButton):
    """ Used in conjuction with WeightCtrl """

    def __init__(self, parent: MainView):
        super().__init__(parent, bitmap=wx.Bitmap(weight_bm))
        self.mv = parent
        self.SetToolTip("Lấy cân nặng mới nhất")
        self.Bind(wx.EVT_BUTTON, self.onGetWeight)

    def onGetWeight(self, e: wx.CommandEvent):
        visit_count = self.mv.visit_list.GetItemCount()
        if self.mv.state.patient and (visit_count > 0):
            self.mv.weight.SetWeight(self.mv.con.execute(f"""
                SELECT weight
                FROM {Visit.table_name}
                WHERE (patient_id) = {self.mv.state.patient.id}
                ORDER BY exam_datetime DESC
                LIMIT 1
            """).fetchone()['weight'])


class DaysCtrl(wx.SpinCtrl):
    """ Changing DaysCtrl Value also changes RecheckCtrl Value """

    def __init__(self, parent: MainView, **kwargs):
        super().__init__(
            parent,
            style=wx.SP_ARROW_KEYS,
            initial=parent.config["so_ngay_toa_ve_mac_dinh"],
            **kwargs
        )
        self.mv = parent
        self.SetRange(0, 100)
        self.Disable()
        self.Bind(wx.EVT_SPINCTRL, self.onSpin)

    def onSpin(self, e: wx.SpinEvent):
        self.mv.recheck.SetValue(e.GetPosition())


class RecheckCtrl(wx.SpinCtrl):
    """Independant of DaysCtrl"""

    def __init__(self, parent: MainView, **kwargs):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"], **kwargs)
        self.SetRange(0, 100)
        self.Disable()


class NoRecheckBtn(wx.Button):
    """Set RecheckCtrl Value to 0"""

    def __init__(self, parent: MainView, **kwargs):
        super().__init__(parent, label="Không tái khám", **kwargs)
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e: wx.CommandEvent):
        self.mv.recheck.SetValue(0)


class UpdateQuantityBtn(wx.Button):
    """Provide `update_quantity` method for DrugList, also update price"""

    def __init__(self, parent: MainView):
        super().__init__(parent, label="Cập nhật lại số lượng thuốc trong toa theo ngày")
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e: wx.CommandEvent):
        self.update_quantity()

    def update_quantity(self):
        """Update quantity in DrugList, also update price"""
        drug_list = self.mv.order_book.page0.drug_list
        for idx, item in enumerate(drug_list._list):
            q = otf.calc_quantity(
                times=item['times'],
                dose=item['dose'],
                days=self.mv.days.GetValue(),
                sale_unit=item['sale_unit'],
                list_of_unit=self.mv.config['thuoc_ban_mot_don_vi']
            )
            assert q is not None
            item['quantity'] = q
            drug_list.SetItem(
                idx, 4, f"{q} {item['sale_unit'] or item['usage_unit']}")
        self.mv.price.FetchPrice()


class PriceCtrl(wx.TextCtrl):
    """A TextCtrl with proper Vietnamese currency format with default set according to config"""

    def __init__(self, parent: MainView, **kwargs):
        super().__init__(parent, **kwargs)
        self.mv = parent
        self.clear()

    def FetchPrice(self):
        price: int = self.mv.config['cong_kham_benh']
        price += sum(
            item['sale_price'] * item['quantity']
            for item in self.mv.order_book.page0.drug_list._list
        )
        self.ChangeValue(self.num_to_str(price))

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
        self.ChangeValue(self.num_to_str(self.mv.config['cong_kham_benh']))


class NewVisitBtn(wx.Button):
    """Deselect a visit from visitlist to simulate new visit"""

    def __init__(self, parent: MainView):
        super().__init__(parent, label="Lượt khám mới")
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e: wx.CommandEvent):
        idx: int = self.mv.visit_list.GetFirstSelected()
        self.mv.visit_list.Select(idx, 0)


class SaveBtn(wx.Button):
    """Change between insert/update base on visit selecting"""

    def __init__(self, parent: MainView):
        super().__init__(parent, label="Lưu")
        self.mv = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
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
                    """, v.into_qmark_style_params())
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
