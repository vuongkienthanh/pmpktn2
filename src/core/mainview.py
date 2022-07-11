from core.initialize import *
from core.state import State
from core.mainview_books.patient_book import PatientBook
from core.mainview_books.visit_list import VisitList
from core.mainview_books.order_book import OrderBook
from core.widgets import *
from core.menu.menubar import MyMenuBar
from core.accel import my_accel
from db import db_func
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
        self.norecheck = NoRecheck(self)
        self.price = otf.disable_text_ctrl(PriceCtrl(self))
        self.follow = Follow(self)
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

    def onClose(self, e):
        print("close sqlite3 connection")
        self.con.close()
        e.Skip()

    def start(self):
        self.patient_book.GetPage(0).build(self.state.queuelist)
        self.patient_book.GetPage(1).build(self.state.todaylist)
