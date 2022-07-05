from path_init import APP_DIR
import wx
import wx.adv as adv
import json
import os.path


class SetupDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Cài đặt hệ thống")
        self.name = wx.TextCtrl(self, value=parent.config['ten_phong_kham'])
        self.price = wx.TextCtrl(
            self, value=str(parent.config["cong_kham_benh"]))
        self.days = wx.SpinCtrl(
            self, initial=parent.config["so_ngay_toa_ve_mac_dinh"])
        self.alert = wx.SpinCtrl(
            self, initial=parent.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"], max=10000)
        self.unit = adv.EditableListBox(self, style=adv.EL_DEFAULT_STYLE|adv.EL_NO_REORDER)
        self.unit.GetListCtrl().DeleteAllItems()
        for item in parent.config["thuoc_ban_mot_don_vi"]:
            self.unit.GetListCtrl().Append((item,))

        def static(s):
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER_VERTICAL)

        def widget(w):
            return (w, 1, wx.EXPAND)
        entry_sizer = wx.FlexGridSizer(5, 2, 5, 5)
        entry_sizer.AddMany([
            static("Tên phòng khám:"),
            widget(self.name),
            static("Công khám bệnh:"),
            widget(self.price),
            static("Số ngày toa về mặc định:"),
            widget(self.days),
            static("Lượng thuốc tối thiểu để báo động đỏ:"),
            widget(self.alert),
            static("Thuốc bán một đơn vị:"),
            widget(self.unit)
        ])

        btn_sizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry_sizer, 0, wx.EXPAND),
            (btn_sizer, 0, wx.EXPAND)
        ])
        self.SetSizerAndFit(sizer)

        okbtn = btn_sizer.Children[3].Window
        okbtn.Bind(wx.EVT_BUTTON, self.onOk)

    def onOk(self, e):
        try:
            self.Parent.config['ten_phong_kham'] = self.name.Value
            self.Parent.config['cong_kham_benh'] = int(self.price.Value)
            self.Parent.config['so_ngay_toa_ve_mac_dinh'] = self.days.GetValue()
            self.Parent.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"] = self.alert.GetValue()
            self.Parent.config["thuoc_ban_mot_don_vi"] = [
                self.unit.GetListCtrl().GetItemText(idx).strip()
                for idx in range(self.unit.GetListCtrl().ItemCount)
                if self.unit.GetListCtrl().GetItemText(idx).strip() != ''
            ]
            with open(os.path.join(APP_DIR, "config.json"), mode='w', encoding="utf-8") as f:
                json.dump(self.Parent.config, f, ensure_ascii=False, indent=4)
            wx.MessageBox("Đã lưu cài đặt", "Cài đặt")
            self.Parent.price.set_price()
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Lỗi không lưu được\n{error}", "Lỗi")
