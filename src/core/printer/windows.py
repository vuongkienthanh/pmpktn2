import core.other_func as otf
from .printdata import BasePrintOut
import textwrap as tw
import wx


class PrintOut(BasePrintOut):

    def OnPrintPage(self, page):
        dc: wx.DC = self.GetDC()
        dc.SetMapMode(wx.MM_LOMETRIC)
        state = self.mv.state
        p = state.patient
        assert p is not None

        # fonts
        title = wx.Font(wx.FontInfo(36).Bold())        
        info = wx.Font(wx.FontInfo(26))
        info_italic = wx.Font(wx.FontInfo(26).Italic())
        list_num = wx.Font(wx.FontInfo(26).Bold())
        drug_name = wx.Font(wx.FontInfo(32))
        heading = wx.Font(wx.FontInfo(18))

        def draw_top():
            with wx.DCFontChanger(dc, heading):
                dc.DrawText(self.mv.config['ten_phong_kham'], 120, 100)
                dc.DrawText("Địa chỉ: " + self.mv.config['dia_chi'], 120, 140)
                dc.DrawText(
                    "SĐT: " + self.mv.config['so_dien_thoai'], 120, 180)
            with wx.DCFontChanger(dc, title):
                dc.DrawText('ĐƠN THUỐC', 560, 230)
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Họ tên:", 100, 300)
                dc.DrawText("CN:", 1050, 300)
                dc.DrawText("Giới:", 100, 350)
                dc.DrawText("SN:", 480, 350)
                dc.DrawText("Chẩn đoán:", 100, 400)
            with wx.DCFontChanger(dc, info_italic):
                dc.DrawText(p.name, 260, 300)
                dc.DrawText(str(self.mv.weight.Value) + " kg", 1140, 300)
                dc.DrawText(str(p.gender), 210, 350)
                dc.DrawText(p.birthdate.strftime("%d/%m/%Y"), 560, 350)
                dc.DrawText(otf.bd_to_age(
                    p.birthdate).rjust(13, ' '), 1060, 350)
                diagnosis = tw.wrap(self.mv.diagnosis.Value,
                                    60, initial_indent=" " * 20)
                if len(diagnosis) > 3:
                    diagnosis = diagnosis[:3]
                    diagnosis[-1] = diagnosis[-1][:-3] + '...'
                for i, line in enumerate(diagnosis):
                    dc.DrawText(line, 100, 400 + i * 50)

        def draw_bottom():
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Bác sĩ khám bệnh", 1000, 1650)
                dc.DrawText(self.mv.config['ky_ten_bac_si'], 950, 1950)
            with wx.DCFontChanger(dc, heading):
                if self.mv.config['in_gia_tien']:
                    dc.DrawText(
                        f"Tổng cộng: {self.mv.price.GetValue()}", 100, 1550)
                if self.mv.recheck.GetValue() != 0:
                    dc.DrawText(
                        f"Tái khám sau {self.mv.recheck.GetValue()} ngày", 100, 1600)
                follow = tw.wrap(self.mv.follow.Value, width=50)
                for index, line in enumerate(follow):
                    dc.DrawText(line, 100, 1650 + 50 * index)

        def draw_page_count(i: int):
            with wx.DCFontChanger(dc, heading):
                dc.DrawText(f"Trang {i}/2", 1100, 1600)

        def draw_content(first=True):
            i = 0
            if first:
                _list = self.d_list[:self.num_of_ld]
                added = 0
            else:
                _list = self.d_list[self.num_of_ld:]
                added = self.num_of_ld
            for dl in _list:
                with wx.DCFontChanger(dc, list_num):
                    dc.DrawText(f"{i+1+added}/", 80, 580 + 120 * i)
                with wx.DCFontChanger(dc, drug_name):
                    dc.DrawText(f"{dl['name']}", 180, 580 + 120 * i)
                    t = f"{dl['quantity']} {dl['sale_unit'] or dl['usage_unit']}"
                    dc.DrawText(t, 1200, 580 + 120 * i)
                with wx.DCFontChanger(dc, info_italic):
                    dc.DrawText(dl['note'] or otf.get_usage_note_str(
                        dl['usage'],
                        str(dl['times']),
                        dl['dose'],
                        dl['usage_unit']
                    ), 150, 640 + 120 * i)
                i += 1

        if page == 1:
            draw_top()
            if len(self.d_list) != 0:
                draw_content(first=True)
            if self.HasPage(2):
                draw_page_count(1)
            else:
                draw_bottom()
            dc.EndPage()
            return True

        elif page == 2:
            draw_top()
            draw_content(first=False)
            draw_page_count(2)
            draw_bottom()
            dc.EndPage()
            return True
        else:
            return False
