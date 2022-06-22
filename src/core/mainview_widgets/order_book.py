import wx
from .order_book_pages.prescription.prescription_page import PrescriptionPage


class OrderBook(wx.Notebook):

    def __init__(self, parent):
        super().__init__(parent)
        self.mv = parent
        self.AddPage(page=PrescriptionPage(self),
                     text='Toa thuốc', select=True)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onChangePage)

    def clear(self):
        self.ChangeSelection(0)
        self.GetPage(0).clear()

    def onChangePage(self, e):
        self.GetPage(e.GetSelection()).refresh()
        e.Skip()
