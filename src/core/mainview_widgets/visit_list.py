from core.initialize import *
from db.db_class import Visit
import sqlite3
import wx


class VisitList(wx.ListCtrl):

    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.AppendColumn('Mã lượt khám', width=-2)
        self.AppendColumn('Ngày giờ khám'.ljust(16, ' '), width=-2)
        self.AppendColumn('Chẩn đoán'.ljust(40, ' '), width=-2)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, _list) -> None:
        for item in _list:
            self.append_ui(item)

    def append_ui(self, row: sqlite3.Row) -> None:
        self.Append([
            row['vid'],
            row['exam_datetime'].strftime("%d/%m/%Y %H:%M"),
            row['diagnosis']
        ])

    def rebuild(self, _list: list[sqlite3.Row]) -> None:
        self.DeleteAllItems()
        self.build(_list)

    def onSelect(self, e: wx.ListEvent) -> None:
        vid = self.Parent.state.visitlist[e.Index]['vid']
        self.Parent.state.visit = self.Parent.con.select(Visit, vid)

    def onDeselect(self, e: wx.ListEvent) -> None:
        self.Parent.state.visit = None
