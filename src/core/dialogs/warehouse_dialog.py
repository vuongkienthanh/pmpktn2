from core.initialize import size
from db.db_class import Warehouse
import core.other_func as otf
from core import mainview
from core.generic import DatePicker, NumberTextCtrl
import wx


class WarehouseSetupDialog(wx.Dialog):
    def __init__(self, parent: 'mainview.MainView'):
        """
        `_list`: internal list to keep track of Warehouse in dialog
        """
        super().__init__(parent=parent, title="Kho thuốc",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        self.mv = parent
        self._list: list[Warehouse] = []

        self.search = wx.SearchCtrl(self)
        self.search.SetHint("Tên thuốc hoặc thành phần thuốc")
        self.lc = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        
        self.lc.AppendColumn("Mã")
        self.lc.AppendColumn("Tên", width=size(0.1))
        self.lc.AppendColumn("Thành phần", width=size(0.1))
        self.lc.AppendColumn("Số lượng")
        self.lc.AppendColumn("Đơn vị sử dụng",width=-2)
        self.lc.AppendColumn("Cách sử dụng",width=-2)
        self.lc.AppendColumn("Giá mua")
        self.lc.AppendColumn("Giá bán")
        self.lc.AppendColumn("Đơn vị bán")
        self.lc.AppendColumn("Ngày hết hạn", width=-2)
        self.lc.AppendColumn("Xuất xứ")
        self.lc.AppendColumn("Ghi chú")
        self.newbtn = wx.Button(self, label="Thêm mới")
        self.editbtn = wx.Button(self, label="Cập nhật")
        self.delbtn = wx.Button(self, label="Xóa")
        cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.editbtn.Disable()
        self.delbtn.Disable()

        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        search_sizer.AddMany([
            (wx.StaticText(self, label="Tìm kiếm"), 0, wx.ALL | wx.ALIGN_CENTER, 5),
            (self.search, 1, wx.ALL, 5),
        ])
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
            (search_sizer, 0, wx.EXPAND),
            (self.lc, 1, wx.EXPAND | wx.ALL, 5),
            (btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        ])
        self.SetSizerAndFit(sizer)

        self.search.Bind(wx.EVT_SEARCH, self.onSearch)
        self.search.Bind(wx.EVT_TEXT, self.onSearchText)
        self.lc.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.lc.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEdit)
        self.newbtn.Bind(wx.EVT_BUTTON, self.onNew)
        self.editbtn.Bind(wx.EVT_BUTTON, self.onEdit)
        self.delbtn.Bind(wx.EVT_BUTTON, self.onDelete)
        self.Maximize()
        self.build()

    def clear(self):
        """
        clear display and internal Warehouse list
        """
        self._list = []
        self.lc.DeleteAllItems()

    def get_search_value(self) -> str:
        """
        get string 
        """
        s: str = self.search.GetValue()
        return s.strip().casefold()

    def check_search_str_to_wh(self, wh: Warehouse, s: str) -> bool:
        if (s in wh.name.casefold()) or (s in wh.element.casefold()):
            return True
        else:
            return False

    def rebuild(self, s: str = ''):
        self.clear()
        for wh in filter(
                lambda wh: self.check_search_str_to_wh(wh, s),
                self.mv.state.warehouselist
        ):
            self.append(wh)

    def build(self):
        self.clear()
        for wh in self.mv.state.warehouselist:
            self.append(wh)

    def append(self, wh: Warehouse):
        self._list.append(wh)
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
        self.check_min_quantity(wh, len(self._list) - 1)

    def delete(self, idx: int):
        self.lc.DeleteItem(idx)
        self._list.pop(idx)

    def check_min_quantity(self, wh: Warehouse, idx: int):
        if wh.quantity <= self.mv.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"]:
            self.lc.SetItemTextColour(idx, wx.Colour(252, 3, 57))

    def onSearch(self, e: wx.CommandEvent):
        self.rebuild(self.get_search_value())
        e.Skip()

    def onSearchText(self, e: wx.CommandEvent):
        if len(self.search.GetValue()) == 0:
            self.build()

    def onSelect(self, e: wx.ListEvent):
        self.editbtn.Enable()
        self.delbtn.Enable()

    def onDeselect(self, e: wx.ListEvent):
        self.editbtn.Disable()
        self.delbtn.Disable()

    def onNew(self, e: wx.CommandEvent):
        NewWarehouseDialog(self).ShowModal()

    def onEdit(self, e: wx.CommandEvent | wx.ListEvent):
        idx = self.lc.GetFirstSelected()
        wh = self._list[idx]
        EditWarehouseDialog(self, wh).ShowModal()

    def onDelete(self, e: wx.CommandEvent):
        idx: int = self.lc.GetFirstSelected()
        wh = self._list[idx]
        try:
            rowcount = self.mv.con.delete(Warehouse, wh.id)
            wx.MessageBox(f"Xoá thuốc thành công\n{rowcount}", "Xóa")
            self.mv.state.warehouselist = self.mv.con.selectall(Warehouse)
            self.delete(idx)
        except Exception as error:
            wx.MessageBox(f"Lỗi không xóa được\n{error}", "Lỗi")


class WarehouseDialog(wx.Dialog):
    def __init__(self, parent: WarehouseSetupDialog, title: str):
        super().__init__(parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, title=title)
        self.parent = parent
        self.title = title

        self.name = wx.TextCtrl(self, name="Tên thuốc")
        self.element = wx.TextCtrl(self, name="Thành phần")
        self.quantity = NumberTextCtrl(self, name="Số lượng")
        self.usage_unit = wx.TextCtrl(self, name="Đơn vị sử dụng")
        self.usage = wx.TextCtrl(self, name="Cách sử dụng")
        self.purchase_price = NumberTextCtrl(self, name="Giá mua")
        self.sale_price = NumberTextCtrl(self, name="Giá bán")
        self.sale_unit = wx.TextCtrl(self, name="Đơn vị bán")
        self.expire_date = DatePicker(self, name="Hạn sử dụng")
        self.made_by = wx.TextCtrl(self, name="Xuất xứ")
        self.note = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Ghi chú")
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.okbtn = wx.Button(self, id=wx.ID_OK)

        self.mandatory: tuple = (
            self.name,
            self.element,
            self.quantity,
            self.usage_unit,
            self.usage,
            self.purchase_price,
            self.sale_price
        )

        def widget(w):
            s: str = w.Name
            if w in self.mandatory:
                s += '*'
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3), (w, 1, wx.EXPAND | wx.ALL, 3)
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
            *widget(self.name),
            *widget(self.element),
            *widget(self.quantity),
            *widget(self.usage_unit),
            *widget(self.usage),
            *widget(self.purchase_price),
            *widget(self.sale_price),
            *widget(self.sale_unit),
            *widget(self.expire_date),
            *widget(self.made_by),
            *widget(self.note),
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry_sizer, 1, wx.EXPAND | wx.ALL, 5),
            (wx.StaticText(self, label="* là bắt buộc; Không có hạn sử dụng thì để hôm nay"),
             0, wx.EXPAND | wx.ALL, 5),
            (btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        ])
        self.SetSizerAndFit(sizer)

        self.okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def onOkBtn(self, e: wx.CommandEvent): ...

    def is_valid(self) -> bool:
        for widget in self.mandatory:
            val: str = widget.GetValue()
            name: str = widget.GetName()
            if val.strip() == '':
                wx.MessageBox(f"Chưa nhập đủ thông tin\n{name}", self.title)
                return False
        else:
            return True

    def checked_get_sale_unit_value(self) -> str | None:
        sale_unit: str = self.sale_unit.GetValue()
        sale_unit = sale_unit.strip()
        usage_unit: str = self.usage_unit.GetValue()
        usage_unit = usage_unit.strip()

        if (sale_unit == '') or (sale_unit == usage_unit):
            return None
        else:
            return sale_unit


class NewWarehouseDialog(WarehouseDialog):
    def __init__(self, parent: WarehouseSetupDialog):
        super().__init__(parent, title="Thêm mới")

    def onOkBtn(self, e):
        if self.is_valid():
            wh = {
                'name': self.name.Value.strip(),
                'element': self.element.Value.strip(),
                'quantity': int(self.quantity.Value.strip()),
                'usage_unit': self.usage_unit.Value.strip(),
                'usage': self.usage.Value.strip(),
                'purchase_price': int(self.purchase_price.Value.strip()),
                'sale_price': int(self.sale_price.Value.strip()),
                'sale_unit': self.checked_get_sale_unit_value(),
                'expire_date': self.expire_date.checked_GetDate(),
                'made_by': otf.check_blank(self.made_by.Value),
                'note': otf.check_blank(self.note.Value)
            }
            try:
                lastrowid = self.parent.mv.con.insert(Warehouse, wh)
                assert lastrowid is not None
                wx.MessageBox("Thêm mới thành công", "Thêm mới")
                new_wh = Warehouse(id=lastrowid, **wh)
                self.parent.mv.state.warehouselist.append(new_wh)
                if self.parent.check_search_str_to_wh(new_wh, self.parent.get_search_value()):
                    self.parent.append(new_wh)
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Thêm mới thất bại\n{error}", "Thêm mới")


class EditWarehouseDialog(WarehouseDialog):
    def __init__(self, parent: WarehouseSetupDialog, wh: Warehouse):
        super().__init__(parent, title="Cập nhật")
        self.wh = wh
        self.build(wh)

    def build(self, wh: Warehouse):
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
        if self.is_valid():
            self.wh.name = self.name.Value.strip()
            self.wh.element = self.element.Value.strip()
            self.wh.quantity = int(self.quantity.Value)
            self.wh.usage_unit = self.usage_unit.Value.strip()
            self.wh.usage = self.usage.Value.strip()
            self.wh.purchase_price = int(self.purchase_price.Value)
            self.wh.sale_price = int(self.sale_price.Value)
            self.wh.sale_unit = self.checked_get_sale_unit_value()
            self.wh.expire_date = self.expire_date.checked_GetDate()
            self.wh.made_by = otf.check_blank(self.made_by.Value)
            self.wh.note = otf.check_blank(self.note.Value)
            try:
                self.parent.mv.con.update(self.wh)
                wx.MessageBox("Cập nhật thành công", "Cập nhật")
                self.parent.rebuild(self.parent.get_search_value())
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Cập nhật thất bại\n{error}", "Cập nhật")
