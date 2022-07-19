from db import db_func
from core.initialize import  background_color, window_size
import core.other_func as otf
from core.state import State
from core.generic import AgeCtrl, PhoneTextCtrl, DateTextCtrl, WeightCtrl
from core.mainview_widgets import (
    GetWeightBtn, DaysCtrl, UpdateQuantityBtn,
    RecheckCtrl, NoRecheckBtn, PriceCtrl,
    Follow, NewVisitBtn, SaveBtn
)
from core.patient_book import PatientBook, VisitList
from core.order_book import OrderBook
from core.menubar import MyMenuBar
from core.accel import my_accel
import wx
from typing import Any


class MainView(wx.Frame):

    def __init__(self, con: 'db_func.Connection', config: dict[str, Any], sample: bool = False):
        super().__init__(
            parent=None,
            pos=(20,20),
            title='PHẦN MỀM PHÒNG KHÁM TẠI NHÀ')
        self.SetBackgroundColour(background_color)

        self.con = con
        self.state = State(self)
        self.config = config
        self.sample = sample

        self.patient_book = PatientBook(self)
        self.visit_list = VisitList(self)
        self.name = otf.disable_text_ctrl(wx.TextCtrl(self, name="Họ tên:"))
        self.gender = otf.disable_text_ctrl(wx.TextCtrl(self, name="Giới:"))
        self.birthdate = otf.disable_text_ctrl(
            DateTextCtrl(self, name="Ngày sinh:"))
        self.age = otf.disable_text_ctrl(AgeCtrl(self, name="Tuổi:"))
        self.address = otf.disable_text_ctrl(
            wx.TextCtrl(self, name="Địa chỉ:"))
        self.phone = otf.disable_text_ctrl(
            PhoneTextCtrl(self, name="Điện thoại:"))
        self.past_history = wx.TextCtrl(
            self, style=wx.TE_MULTILINE, name="Bệnh nền, dị ứng:")
        self.diagnosis = wx.TextCtrl(self, name="Chẩn đoán:")
        self.vnote = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Bệnh sử")
        self.weight = WeightCtrl(self, name="Cân nặng (kg):")
        self.get_weight_btn = GetWeightBtn(self)
        self.days = DaysCtrl(self, name="Số ngày cho toa:")
        self.updatequantitybtn = UpdateQuantityBtn(self)
        self.order_book = OrderBook(self)
        self.recheck = RecheckCtrl(self, name="Số ngày tái khám:")
        self.norecheck = NoRecheckBtn(self)
        self.price = otf.disable_text_ctrl(PriceCtrl(self, name="Giá tiền"))
        self.follow = Follow(self, self.config['loi_dan_do'])
        self.newvisitbtn = NewVisitBtn(self)
        self.savebtn = SaveBtn(self)

        def widget(w, p, r):
            return (w, p, wx.EXPAND | wx.RIGHT, r)

        def comb(w, p=0, r=5):
            s: str = w.Name
            return (
                (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER | wx.RIGHT, 2),
                widget(w, p, r)
            )

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.AddMany([
            (self.patient_book, 10, wx.EXPAND),
            (wx.StaticText(self, label='Lượt khám cũ:'), 0, wx.EXPAND | wx.ALL, 10),
            (self.visit_list, 4, wx.EXPAND),
        ])
        name_row = wx.BoxSizer(wx.HORIZONTAL)
        name_row.AddMany([
            *comb(self.name, 1),
            *comb(self.gender, 0),
            *comb(self.birthdate, 0),
            *comb(self.age, 0, 0),
        ])
        addr_row = wx.BoxSizer(wx.HORIZONTAL)
        addr_row.AddMany([
            *comb(self.address, 1),
            *comb(self.phone, 0, 0)
        ])
        diag_row = wx.BoxSizer(wx.HORIZONTAL)
        diag_row.AddMany([
            *comb(self.diagnosis, 1, 0)
        ])
        weight_row = wx.BoxSizer(wx.HORIZONTAL)
        weight_row.AddMany([
            *comb(self.weight),
            widget(self.get_weight_btn, 0, 5),
            *comb(self.days),
            widget(self.updatequantitybtn, 0, 0)
        ])
        recheck_row = wx.BoxSizer(wx.HORIZONTAL)
        recheck_row.AddMany([
            *comb(self.recheck),
            widget(self.norecheck, 0, 5),
            (0, 0, 1),
            *comb(self.price, 0, 0)

        ])
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddMany([
            widget(self.newvisitbtn, 0, 5),
            widget(self.savebtn, 0, 0),
        ])
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.AddMany([
            (name_row, 0, wx.EXPAND),
            (addr_row, 0, wx.EXPAND),
            (wx.StaticText(self, label=self.past_history.Name),0,wx.EXPAND),
            widget(self.past_history, 1, 0),
            (diag_row, 0, wx.EXPAND),
            (wx.StaticText(self, label=self.vnote.Name),0,wx.EXPAND),
            widget(self.vnote, 1, 0),
            (weight_row, 0,wx.EXPAND),
            (self.order_book, 3, wx.EXPAND),
            (recheck_row, 0, wx.EXPAND),
            (self.follow, 0, wx.EXPAND),
            (btn_row, 0, wx.EXPAND),

        ])
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([
            (left_sizer, 4, wx.EXPAND | wx.ALL, 10),
            (right_sizer, 6, wx.EXPAND | wx.ALL, 10)
        ])
        self.SetSizerAndFit(sizer)

        self.SetMenuBar(MyMenuBar())
        self.SetAcceleratorTable(my_accel)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.start()

    def onClose(self, e: wx.CloseEvent):
        print("close sqlite3 connection")
        self.con.close()
        e.Skip()

    def start(self):
        self.patient_book.page0.build(self.state.queuelist)
        self.patient_book.page1.build(self.state.todaylist)

    def check_filled(self) -> bool:
        diagnosis: str = self.diagnosis.GetValue()
        weight = self.weight.GetWeight()
        if diagnosis.strip() == '':
            wx.MessageBox("Chưa nhập chẩn đoán", "Lỗi")
            return False
        elif weight == 0:
            wx.MessageBox(f"Cân nặng = 0", "Lỗi")
            return False
        else:
            return True
