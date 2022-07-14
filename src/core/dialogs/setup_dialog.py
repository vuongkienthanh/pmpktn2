from path_init import APP_DIR
from core import mainview
import wx
import wx.adv as adv
import json
import os.path


class SetupDialog(wx.Dialog):
    def __init__(self, parent:'mainview.MainView'):
        super().__init__(parent, title="Cài đặt hệ thống")
        self.mv = parent
        self.clinic_name = wx.TextCtrl(self, value=self.mv.config['ten_phong_kham'], name="Tên phòng khám")
        self.doctor_name = wx.TextCtrl(self, value=self.mv.config['ky_ten_bac_si'], name="Ký tên bác sĩ")
        self.price = wx.TextCtrl(
            self, value=str(self.mv.config["cong_kham_benh"]), name="Công khám bệnh")
        self.days = wx.SpinCtrl(
            self, initial=self.mv.config["so_ngay_toa_ve_mac_dinh"], name="Số ngày toa về mặc định")
        self.alert = wx.SpinCtrl(
            self, initial=self.mv.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"], max=10000, name="Lượng thuốc tối thiểu để báo động đỏ")
        self.unit = adv.EditableListBox(self, style=adv.EL_DEFAULT_STYLE|adv.EL_NO_REORDER, name="Thuốc bán một đơn vị")
        lc : wx.ListCtrl = self.unit.GetListCtrl()
        lc.DeleteAllItems()
        for item in self.mv.config["thuoc_ban_mot_don_vi"]:
            lc.Append((item,))
        
        cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        okbtn = wx.Button(self, id=wx.ID_OK)


        def widget(w:wx.Window):
            s :str = w.GetName()
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5), (w, 1, wx.EXPAND|wx.ALL, 5)

        entry_sizer = wx.FlexGridSizer(6, 2, 5, 5)
        entry_sizer.AddMany([
            *widget(self.clinic_name),
            *widget(self.doctor_name),
            *widget(self.price),
            *widget(self.days),
            *widget(self.alert),
            *widget(self.unit)
        ])
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany([
            (0,0,1),
            (cancelbtn, 0, wx.ALL,5),
            (okbtn, 0, wx.ALL, 5),
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry_sizer, 0, wx.EXPAND),
            (btn_sizer, 0, wx.EXPAND)
        ])
        self.SetSizerAndFit(sizer)

        okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def onOkBtn(self, e:wx.CommandEvent):
        try:
            lc : wx.ListCtrl = self.unit.GetListCtrl()

            self.mv.config['ten_phong_kham'] = self.clinic_name.Value
            self.mv.config['ky_ten_bac_si'] = self.doctor_name.Value
            self.mv.config['cong_kham_benh'] = int(self.price.Value)
            self.mv.config['so_ngay_toa_ve_mac_dinh'] = self.days.GetValue()
            self.mv.config["so_luong_thuoc_toi_thieu_de_bao_dong_do"] = self.alert.GetValue()
            self.mv.config["thuoc_ban_mot_don_vi"] = [
                lc.GetItemText(idx).strip()
                for idx in range(lc.ItemCount)
                if lc.GetItemText(idx).strip() != ''
            ]
            with open(os.path.join(APP_DIR, "config.json"), mode='w', encoding="utf-8") as f:
                json.dump(self.mv.config, f, ensure_ascii=False, indent=4)
            wx.MessageBox("Đã lưu cài đặt", "Cài đặt")
            self.mv.price.SetPrice()
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Lỗi không lưu được\n{error}", "Lỗi")