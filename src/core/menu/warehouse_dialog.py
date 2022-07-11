from db.db_class import Warehouse
import core.other_func as otf
from core import mainview
from core.widgets import DatePicker, NumTextCtrl
import wx
import wx.adv as adv
import datetime as dt


class WarehouseSetupDialog(wx.Dialog):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent=parent, title="Kho thuốc",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.locale = wx.Locale(wx.LANGUAGE_VIETNAMESE)
        self.mv = parent
        self._list = parent.state.warehouselist
        self.search = wx.TextCtrl(self)
        self.search.SetHint("Tên thuốc hoặc thành phần thuốc")
        self.lc = self._create_listctrl()
        self.newbtn = wx.Button(self, label="Thêm mới")
        self.editbtn = wx.Button(self, label="Cập nhật")
        self.delbtn = wx.Button(self, label="Xóa")
        cancelbtn = wx.Button(self, id=wx.ID_CANCEL)

        self.editbtn.Disable()
        self.delbtn.Disable()

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany([
            (0, 0, 1),
            (self.newbtn, 0, wx.RIGHT, 5),
            (self.editbtn, 0, wx.RIGHT, 5),
            (self.delbtn, 0, wx.RIGHT, 5),
            (cancelbtn, 0, wx.RIGHT, 5)

        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (self.search, 0, wx.EXPAND | wx.ALL, 5),
            (self.lc, 1, wx.EXPAND | wx.ALL, 5),
            (btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        ])
        self.SetSizerAndFit(sizer)
        self.search.Bind(wx.EVT_CHAR, self.onSearch)
        self.newbtn.Bind(wx.EVT_BUTTON, self.onNew)
        self.editbtn.Bind(wx.EVT_BUTTON, self.onEdit)
        self.delbtn.Bind(wx.EVT_BUTTON, self.onDel)
        self.Maximize()
        self.build()
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, e):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        e.Skip()

    def _create_listctrl(self):
        w = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for f in [
            "Mã", "Tên".ljust(40, ' '), "Thành phần".ljust(40, ' '),
            "Số lượng", "Đơn vị sử dụng", "Phương thức sử dụng",
            "Giá mua", "Giá bán", "Đơn vị bán", "Ngày hết hạn",
            "Xuất xứ", "Ghi chú".ljust(60, ' ')
        ]:
            w.AppendColumn(f, width=-2)
        w.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        w.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        w.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEdit)
        return w

    def onSearch(self, e):
        if e.KeyCode == wx.WXK_RETURN:
            self.rebuild(self.search.Value.casefold())
        else:
            e.Skip()

    def rebuild(self, s=''):
        self.lc.DeleteAllItems()
        self.fetch(s)
        self.build()

    def fetch(self, s=''):
        lwh = self.mv.state.warehouselist
        self._list = list(filter(lambda wh: (s in wh.name.casefold())
                                 or (s in wh.element.casefold()), lwh))

    def build(self):
        for idx, wh in enumerate(self._list):
            self.append(wh)
            self.check_min_quantity(wh, idx)

    def append(self, wh: Warehouse):
        self.lc.Append([
            str(wh.id),
            wh.name,
            wh.element,
            str(wh.quantity),
            wh.usage_unit,
            wh.usage,
            str(wh.purchase_price),
            str(wh.sale_price),
            wh.sale_unit if wh.sale_unit is not None else wh.usage_unit,
            wh.expire_date.strftime(
                "%d/%m/%Y") if wh.expire_date is not None else '',
            otf.check_none(wh.made_by),
            otf.check_none(wh.note)
        ])

    def check_min_quantity(self, wh: Warehouse, index: int):
        if wh.quantity <= self.mv.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"]:
            self.lc.SetItemTextColour(index, wx.Colour(252, 3, 57))

    def onSelect(self, e):
        self.editbtn.Enable()
        self.delbtn.Enable()

    def onDeselect(self, e):
        self.editbtn.Disable()
        self.delbtn.Disable()

    def onNew(self, e):
        NewWarehouseDialog(self).ShowModal()

    def onEdit(self, e):
        idx = self.lc.GetFirstSelected()
        wh = self._list[idx]
        EditWarehouseDialog(self, wh).ShowModal()

    def onDel(self, e):
        idx = self.lc.GetFirstSelected()
        wh = self._list[idx]
        try:
            rowcount = self.mv.con.delete(Warehouse, wh.id)
            wx.MessageBox(f"Xoá thuốc thành công\n{rowcount}", "Xóa")
            self.mv.state.warehouselist = self.mv.con.selectall(Warehouse)
            self.rebuild()
        except Exception as error:
            wx.MessageBox(f"Lỗi không xóa được\n{error}", "Lỗi")


class WarehouseDialog(wx.Dialog):
    def __init__(self, parent:WarehouseSetupDialog, title:str):
        super().__init__(parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, title=title)
        self.parent = parent
        self.name = wx.TextCtrl(self)
        self.element = wx.TextCtrl(self)
        self.quantity = NumTextCtrl(self)
        self.usage_unit = wx.TextCtrl(self)
        self.usage = wx.TextCtrl(self)
        self.purchase_price = NumTextCtrl(self)
        self.sale_price = NumTextCtrl(self)
        self.sale_unit = wx.TextCtrl(self)
        self.expire_date = DatePicker(self)
        self.made_by = wx.TextCtrl(self)
        self.note = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.okbtn = wx.Button(self, id=wx.ID_OK)
        self.okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)
        self._setSizer()

    def _setSizer(self):
        def static(s):
            return (wx.StaticText(self, label=s), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)

        def widget(w, p=10):
            return (w, p, wx.EXPAND | wx.ALL, 3)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany([
            (0, 0, 1),
            (self.cancelbtn, 0, wx.ALL, 5),
            (self.okbtn, 0, wx.ALL, 5)
        ])
        entry_sizer = wx.FlexGridSizer(11, 2, 3, 3)
        entry_sizer.AddGrowableCol(1, 3)
        entry_sizer.AddGrowableRow(10, 2)
        entry_sizer.AddMany([
            static("Tên*"),
            widget(self.name),
            static("Thành phần*"),
            widget(self.element),
            static("Số lượng*"),
            widget(self.quantity),
            static("Đơn vị sử dụng*"),
            widget(self.usage_unit),
            static("Cách sử dụng*"),
            widget(self.usage),
            static("Giá mua*"),
            widget(self.purchase_price),
            static("Giá bán*"),
            widget(self.sale_price),
            static("Đơn vị bán"),
            widget(self.sale_unit),
            static("Hạn sử dụng"),
            widget(self.expire_date),
            static("Xuất xứ"),
            widget(self.made_by),
            static("Ghi chú"),
            widget(self.note),
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry_sizer, 1, wx.EXPAND | wx.ALL, 5),
            (wx.StaticText(self, label="* là bắt buộc; Không có hạn sử dụng thì để hôm nay"),
             0, wx.EXPAND | wx.ALL, 5),
            (btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        ])
        self.SetSizerAndFit(sizer)

    def onOkBtn(self, e): ...


class NewWarehouseDialog(WarehouseDialog):
    def __init__(self, parent:WarehouseSetupDialog):
        super().__init__(parent, title="Thêm mới")

    def onOkBtn(self, e):
        for widget in [
            self.name,
            self.element,
            self.quantity,
            self.usage_unit,
            self.usage,
            self.purchase_price,
            self.sale_price
        ]:
            if widget.Value.strip() == '':
                wx.MessageBox("Chưa nhập đủ thông tin", "Thêm mới")
                return
        else:
            sale_unit = self.sale_unit.Value.strip()
            if (sale_unit == '') or (sale_unit == self.usage_unit.Value.strip()):
                sale_unit = None
            expire_date = self.expire_date.GetDate()
            if expire_date == dt.date.today():
                expire_date = None

            wh = {
                'name': self.name.Value.strip(),
                'element': self.element.Value.strip(),
                'quantity': int(self.quantity.Value.strip()),
                'usage_unit': self.usage_unit.Value.strip(),
                'usage': self.usage.Value.strip(),
                'purchase_price': int(self.purchase_price.Value.strip()),
                'sale_price': int(self.sale_price.Value.strip()),
                'sale_unit': sale_unit,
                'expire_date': expire_date,
                'made_by': otf.check_blank(self.made_by.Value),
                'note': otf.check_blank(self.note.Value)
            }
            try:
                res = self.parent.mv.con.insert(Warehouse, wh)
                if res is not None:
                    wx.MessageBox("Thêm mới thành công", "Thêm mới")
                    lastrowid ,_ = res
                    new_wh = Warehouse(id=lastrowid,**wh)
                    self.parent.mv.state.warehouselist.append(new_wh)
                    self.parent.rebuild()
                    e.Skip()
                else:
                    raise ValueError('lastrowid is None')
            except Exception as error:
                wx.MessageBox(f"Thêm mới thất bại\n{error}", "Thêm mới")


class EditWarehouseDialog(WarehouseDialog):
    def __init__(self, parent:WarehouseSetupDialog, wh:Warehouse):
        super().__init__(parent, title="Cập nhật")
        self.wh = wh
        self.build(wh)

    def build(self, wh:Warehouse):
        self.name.ChangeValue(wh.name)
        self.element.ChangeValue(wh.element)
        self.quantity.ChangeValue(str(wh.quantity))
        self.usage_unit.ChangeValue(wh.usage_unit)
        self.usage.ChangeValue(wh.usage)
        self.purchase_price.ChangeValue(str(wh.purchase_price))
        self.sale_price.ChangeValue(str(wh.sale_price))
        if wh.sale_unit is None:
            self.sale_unit.ChangeValue(wh.usage_unit)
        else:
            self.sale_unit.ChangeValue(wh.sale_unit)
        if wh.expire_date is not None:
            self.expire_date.SetDate(wh.expire_date)
        self.made_by.ChangeValue(otf.check_none(wh.made_by))
        self.note.ChangeValue(otf.check_none(wh.note))

    def onOkBtn(self, e):
        for widget in [
            self.name,
            self.element,
            self.quantity,
            self.usage_unit,
            self.usage,
            self.purchase_price,
            self.sale_price
        ]:
            if widget.Value.strip() == '':
                wx.MessageBox("Chưa nhập đủ thông tin", "Thêm mới")
                return
        else:
            sale_unit = self.sale_unit.Value.strip()
            if (sale_unit == '') or (sale_unit == self.usage_unit.Value.strip()):
                sale_unit = None
            expire_date = self.expire_date.GetDate()
            if expire_date == dt.date.today():
                expire_date = None
            
            self.wh.name = self.name.Value.strip()
            self.wh.element = self.element.Value.strip()
            self.wh.quantity = int(self.quantity.Value.strip())
            self.wh.usage_unit = self.usage_unit.Value.strip()
            self.wh.usage = self.usage.Value.strip()
            self.wh.purchase_price = int(self.purchase_price.Value.strip())
            self.wh.sale_price = int(self.sale_price.Value.strip())
            self.wh.sale_unit = sale_unit
            self.wh.expire_date = expire_date
            self.wh.made_by = otf.check_blank(self.made_by.Value.strip())
            self.wh.note = otf.check_blank(self.note.Value.strip())
            try:
                self.parent.mv.con.update(self.wh)
                wx.MessageBox("Cập nhật thành công", "Cập nhật")
                self.parent.mv.state.warehouselist = self.parent.mv.con.selectall(Warehouse)
                self.parent.rebuild()  
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Cập nhật thất bại\n{error}", "Cập nhật")
