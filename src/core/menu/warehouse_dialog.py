from db.db_class import Warehouse
import wx



class WarehouseDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Kho thuốc",style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.search = wx.TextCtrl(self)
        self.listctrl = self._create_listctrl()
        self.newbtn = wx.Button(self, label="Thêm mới")
        self.editbtn = wx.Button(self, label="Cập nhật")
        self.delbtn = wx.Button(self, label="Xóa")
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)

        btn_sizer= wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany([
            (0,1),
            (self.newbtn, 0),
            (self.editbtn, 0),
            (self.delbtn,0),
            (self.cancelbtn, 0)

        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (self.search,0, wx.EXPAND),
            (self.listctrl, 1, wx.EXPAND),
            (btn_sizer, 0, wx.EXPAND)

        ])
        self.SetSizerAndFit(sizer)
        self.search.Bind(wx.EVT_CHAR, self.onSearch)
        self.newbtn.Bind(wx.EVT_BUTTON, self.onNew)
        self.editbtn.Bind(wx.EVT_BUTTON, self.onEdit)
        self.delbtn.Bind(wx.EVT_BUTTON, self.onDel)


    def _create_listctrl(self):
        w = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        for f in [
            "Mã", "Tên", "Thành phần", "Số lượng", "Đơn vị sử dụng", "Phương thức sử dụng",
            "Đơn vị bán", "Giá mua", "Giá bán", "Ngày hết hạn", "Xuất xứ", "Ghi chú"
        ]:
            w.AppendColumn(f)
        return w

    def onSearch(self, e):
        if e.KeyCode == wx.WXK_RETURN:
            self.rebuild()
        else:
            e.Skip()

    def rebuild(self):
        lwh = self.Parent.state.warehouselist
        fields = ['id']
        fields.extend(Warehouse.fields())
        for i in lwh:
            self.listctrl.Append([getattr(i, f) for f in fields])
    def onNew(self, e): ...
    def onEdit(self, e): ...
    def onDel(self, e): ...
