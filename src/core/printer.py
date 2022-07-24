import core.other_func as otf
from core import mainview as mv
from core.initialize import print_mm, preview_mm, scale
import textwrap as tw
import wx


printdata = wx.PrintData()
printdata.Bin = wx.PRINTBIN_DEFAULT
printdata.Collate = False
printdata.Colour = False
printdata.Duplex = wx.DUPLEX_SIMPLEX
printdata.NoCopies = 1
printdata.Orientation = wx.PORTRAIT
printdata.PrinterName = ''
printdata.Quality = wx.PRINT_QUALITY_LOW
printdata.PaperId = wx.PAPER_A5


class PrintOut(wx.Printout):

    def __init__(self, mv: 'mv.MainView', num_of_ld=8, preview=False):
        super().__init__(title="Toa thuốc")

        self.mv = mv
        self.num_of_ld = num_of_ld
        self.preview = preview
        self.d_list = self.mv.order_book.page0.drug_list._list

    def HasPage(self, page):
        x, y = divmod(
            self.mv.order_book.page0.drug_list.ItemCount,
            self.num_of_ld
        )
        if page <= (x + bool(y)):
            return True
        elif page == 1 and (x + y) == 0:
            return True
        else:
            return False

    def GetPageInfo(self):
        if self.mv.order_book.page0.drug_list.ItemCount == 0:
            return (1, 1, 1, 1)
        else:
            x, y = divmod(
                self.mv.order_book.page0.drug_list.ItemCount,
                self.num_of_ld
            )
        return (1, x + bool(y), 1, x + bool(y))

    def OnPrintPage(self, page):
        dc: wx.DC = self.GetDC()
        if self.preview:
            dc.SetMapMode(preview_mm)
        else:
            dc.SetMapMode(print_mm)

        state = self.mv.state
        p = state.patient
        assert p is not None

        # fonts
        title = wx.Font(wx.FontInfo(48*scale).Bold())
        info = wx.Font(wx.FontInfo(38*scale))
        info_italic = wx.Font(wx.FontInfo(38*scale).Italic())
        list_num = wx.Font(wx.FontInfo(38*scale).Bold())
        drug_name = wx.Font(wx.FontInfo(44*scale))
        heading = wx.Font(wx.FontInfo(26*scale))

        def draw_top():
            with wx.DCFontChanger(dc, heading):
                dc.DrawText(self.mv.config['ten_phong_kham'], 150, 120)
                dc.DrawText("Địa chỉ: " + self.mv.config['dia_chi'], 150, 160)
                dc.DrawText(
                    "SĐT: " + self.mv.config['so_dien_thoai'], 150, 200)

            with wx.DCFontChanger(dc, title):
                dc.DrawText('ĐƠN THUỐC', 670, 240)
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Họ tên:", 100, 330)
                dc.DrawText("CN:", 1250, 330)
                dc.DrawText("Giới:", 100, 400)
                dc.DrawText("SN:", 500, 400)
                dc.DrawText("Chẩn đoán:", 100, 470)
            with wx.DCFontChanger(dc, info_italic):
                dc.DrawText(p.name, 300, 330)
                dc.DrawText(str(self.mv.weight.Value) + " kg", 1360, 330)
                dc.DrawText(str(p.gender), 230, 400)
                dc.DrawText(p.birthdate.strftime("%d/%m/%Y"), 600, 400)
                dc.DrawText(otf.bd_to_age(
                    p.birthdate).rjust(13, ' '), 1250, 400)
                diagnosis = tw.wrap(self.mv.diagnosis.Value,
                                    55, initial_indent=" " * 20)
                if len(diagnosis) > 3:
                    diagnosis = diagnosis[:3]
                    diagnosis[-1] = diagnosis[-1][:-3] + '...'
                for i, line in enumerate(diagnosis):
                    dc.DrawText(line, 100, 470 + i * 50)

        def draw_bottom():
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Bác sĩ khám bệnh", 1100, 1750)
                dc.DrawText(self.mv.config['ky_ten_bac_si'], 1050, 2050)
            with wx.DCFontChanger(dc, heading):
                if self.mv.config['hien_thi_gia_tien']:
                    dc.DrawText(
                        f"Tổng cộng: {self.mv.price.GetValue()}", 100, 1720)
                if self.mv.recheck.GetValue() != 0:
                    dc.DrawText(
                        f"Tái khám sau {self.mv.recheck.GetValue()} ngày", 100, 1770)
                follow = tw.wrap(self.mv.follow.Value, width=45)
                for index, line in enumerate(follow):
                    dc.DrawText(line, 100, 1820 + 50 * index)

        def draw_page_count(i: int):
            with wx.DCFontChanger(dc, heading):
                dc.DrawText(f"Trang {i}/2", 1300, 1700)

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
                    dc.DrawText(f"{i+1+added}/", 80, 681 + 130 * i)
                with wx.DCFontChanger(dc, drug_name):
                    dc.DrawText(f"{dl['name']}", 180, 675 + 130 * i)
                    t = f"{dl['quantity']} {dl['sale_unit'] or dl['usage_unit']}"
                    dc.DrawText(t, 1300, 675 + 130 * i)
                with wx.DCFontChanger(dc, info_italic):
                    dc.DrawText(dl['note'] or otf.get_usage_note_str(
                        dl['usage'],
                        str(dl['times']),
                        dl['dose'],
                        dl['usage_unit']
                    ), 150, 730 + 130 * i)
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
