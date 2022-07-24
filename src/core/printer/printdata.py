from core import mainview as mv
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


class BasePrintOut(wx.Printout):

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

    def OnPrintPage(self, page): ...
