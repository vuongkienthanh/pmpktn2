from core.mainview_books.order_book_pages.prescription.page import PrescriptionPage
from core import mainview 

import wx


class OrderBook(wx.Notebook):

    def __init__(self, parent:'mainview.MainView'):
        super().__init__(parent)
        self.mv = parent
        self.page0 = PrescriptionPage(self)
        self.AddPage(page=self.page0,
                     text='Toa thuốc', select=True)


