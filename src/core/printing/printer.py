import core.other_func as otf
import textwrap as tw
import wx
from itertools import cycle


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

    def __init__(self, mv, num_of_ld=8, preview=False):
        super().__init__(title="Toa thuốc")
        self.mv = mv
        self.num_of_ld = num_of_ld
        self.preview = preview
        ll = self.mv.order_book.GetPage(0).drug_list._list
        self.d_list = []
        temp = []
        for ld, i in zip(ll, cycle(range(self.num_of_ld))):
            temp.append(ld)
            if i == (self.num_of_ld - 1):
                self.d_list.append(temp)
                temp = []
        if len(temp) != 0:
            self.d_list.append(temp)

    def HasPage(self, page):
        x, y = divmod(
            self.mv.order_book.GetPage(0).drug_list.ItemCount,
            self.num_of_ld
        )
        if page <= (x + bool(y)):
            return True
        elif page == 1 and (x + y) == 0:
            return True
        else:
            return False

    def GetPageInfo(self):
        if self.mv.order_book.GetPage(0).drug_list.ItemCount == 0:
            return (1, 1, 1, 1)
        else:
            x, y = divmod(self.mv.order_book.GetPage(
                0).drug_list.ItemCount, self.num_of_ld)
        return (1, x + bool(y), 1, x + bool(y))

    def OnPrintPage(self, page):
        dc = self.GetDC()
        if self.preview:
            dc.SetMapMode(wx.MM_LOMETRIC)

        state = self.mv.state
        p = state.patient

        title = wx.Font(wx.FontInfo(50).Bold())
        info = wx.Font(wx.FontInfo(40))
        info_italic = wx.Font(wx.FontInfo(40).Italic())
        list_num = wx.Font(wx.FontInfo(40).Bold())
        drug_name = wx.Font(wx.FontInfo(46))
        heading = wx.Font(wx.FontInfo(28))
        if page == 1:
            with wx.DCFontChanger(dc, heading):
                dc.DrawText(self.mv.config['ten_phong_kham'], 150, 150)

            with wx.DCFontChanger(dc, title):
                dc.DrawText('TOA THUỐC', 700, 230)
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Họ tên:", 100, 330)
                dc.DrawText("CN:", 1250, 330)
                dc.DrawText("Giới:", 100, 410)
                dc.DrawText("SN:", 500, 410)
                dc.DrawText("Chẩn đoán:", 100, 490)

            with wx.DCFontChanger(dc, info_italic):
                dc.DrawText(p.name, 280, 330)
                dc.DrawText(str(self.mv.weight.Value) + " kg", 1360, 330)
                dc.DrawText(str(p.gender), 230, 410)
                dc.DrawText(p.birthdate.strftime("%d/%m/%Y"), 600, 410)
                dc.DrawText(otf.bd_to_age(
                    p.birthdate).rjust(13, ' '), 1250, 410)
                diagnosis = tw.wrap(self.mv.diagnosis.Value,
                                    65, initial_indent=" " * 20)
                for i, line in enumerate(diagnosis):
                    dc.DrawText(line, 100, 490 + i * 50)
            if len(self.d_list) != 0:
                for i, dl in enumerate(self.d_list[0]):
                    with wx.DCFontChanger(dc, list_num):
                        dc.DrawText(f"{i+1}/", 80, 681 + 130 * i)
                    with wx.DCFontChanger(dc, drug_name):
                        dc.DrawText(f"{dl['name']}", 150, 675 + 130 * i)
                        t = f"{dl['quantity']} {dl['sale_unit'] or dl['usage_unit']}"
                        dc.DrawText(t, 1300, 675 + 130 * i)
                    with wx.DCFontChanger(dc, info_italic):
                        dc.DrawText(dl['note'] or otf.get_note_str(
                            dl['usage'],
                            str(dl['times']),
                            dl['dose'],
                            dl['usage_unit']
                        ), 150, 735 + 130 * i)

            if self.HasPage(2):
                with wx.DCFontChanger(dc, info):
                    dc.DrawText("Trang 1/2", 1300, 1750)
            else:
                with wx.DCFontChanger(dc, info):
                    dc.DrawText("Bác sĩ khám bệnh", 1100, 1800)
                    follow = tw.wrap(self.mv.follow.Value, width=35)
                    for index, line in enumerate(follow):
                        dc.DrawText(line, 100, 1800 + 60 * index)
            return True

        elif page == 2:
            with wx.DCFontChanger(dc, heading):
                dc.DrawText(self.mv.config['ten_phong_kham'], 150, 100)
            with wx.DCFontChanger(dc, title):
                dc.DrawText('TOA THUỐC', 700, 180)
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Họ tên:", 100, 270)
                dc.DrawText("CN:", 1250, 270)
                dc.DrawText("Giới:", 100, 360)
                dc.DrawText("SN:", 500, 360)
                dc.DrawText("Chẩn đoán:", 100, 440)

            with wx.DCFontChanger(dc, info_italic):
                dc.DrawText(p.name, 280, 270)
                dc.DrawText(str(self.mv.weight.Value) + " kg", 1360, 270)
                dc.DrawText(str(p.gender), 230, 360)
                dc.DrawText(p.birthdate.strftime("%d/%m/%Y"), 600, 360)
                dc.DrawText(otf.bd_to_age(
                    p.birthdate).rjust(13, ' '), 1250, 360)
                diagnosis = tw.wrap(self.mv.diagnosis.Value,
                                    65, initial_indent=" " * 20)
                for i, line in enumerate(diagnosis):
                    dc.DrawText(line, 100, 440 + i * 50)
            for i, dl in enumerate(self.d_list[1]):
                with wx.DCFontChanger(dc, list_num):
                    dc.DrawText(f"{i+1+self.num_of_ld}/", 80, 631 + 130 * i)
                with wx.DCFontChanger(dc, drug_name):
                    dc.DrawText(f"{dl['name']}", 150, 625 + 130 * i)
                    t = f"{dl['quantity']} {dl['sale_unit'] or dl['usage_unit']}"
                    dc.DrawText(t, 1300, 625 + 130 * i)
                with wx.DCFontChanger(dc, info_italic):
                    dc.DrawText(dl['note'] or otf.get_note_str(
                        dl['usage'],
                        str(dl['times']),
                        dl['dose'],
                        dl['usage_unit']
                    ), 150, 685 + 130 * i)
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Trang 2/2", 1300, 1700)
                dc.DrawText("Bác sĩ khám bệnh", 1100, 1750)
                follow = tw.wrap(self.mv.follow.Value, width=35)
                for index, line in enumerate(follow):
                    dc.DrawText(line, 100, 1750 + 60 * index)
            return True
        else:
            return False


class MyPrinter(wx.Printer):

    def __init__(self, mv):
        super().__init__(printdata)
        self.mv = mv

    # def onPageSetupDialog(self):
    #     dlg = wx.PageSetupDialog(self.mv, data=self.pagesetupdialogdata)
    #     ans = dlg.ShowModal()
    #     if ans == wx.ID_OK:
    #         self.pagesetupdialogdata = wx.PageSetupDialogData(
    #             dlg.PageSetupData)
    #         self.printdata = wx.PrintData(dlg.PageSetupData.PrintData)

    # def onPrintPreview(self):

    #     myprintout = My_Printout(self.mv)
    #     if self.mv.drug_info.print_btn.IsEnabled():
    #         myprintout2 = My_Printout(self.mv, 'Toa thuốc')
    #     else:
    #         myprintout2 = None
    #     self.printdialogdata = self.createPrintDialogData()
    #     printpreview = wx.PrintPreview(
    #         myprintout, myprintout2, self.printdialogdata)
    #     printpreview.SetZoom(100)
    #     previewframe = wx.PreviewFrame(printpreview, self.mv, 'asd')
    #     previewframe.Initialize()
    #     previewframe.Maximize()
    #     previewframe.Show()

    # def onPrint(self):
    #     printer = wx.Printer(data=wx.PrintDialogData(pd))
    #     printout = My_Printout(self.mv)
    #     printer.Print(self.mv, printout, False)
