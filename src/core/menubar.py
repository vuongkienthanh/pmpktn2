from re import S
import subprocess
from path_init import SRC_DIR, CONFIG_PATH
from db.db_class import *
from core import mainview
from core.dialogs.find_patient_dialog import FindPatientDialog
from core.dialogs.patient_dialog import EditPatientDialog, NewPatientDialog
from core.dialogs.setup_dialog import SetupDialog
from core.dialogs.warehouse_dialog import WarehouseSetupDialog
from core.dialogs.sample_prescription_dialog import SampleDialog
from core.printer import PrintOut, printdata
import wx
import shutil
import os.path
import sys
import os
import sqlite3
import json


class MyMenuBar(wx.MenuBar):

    def __init__(self):
        super().__init__()

        homeMenu = wx.Menu()
        homeMenu.Append(
            wx.ID_REFRESH,
            wx.GetStockLabel(wx.ID_REFRESH) + "\tF5"
        )
        homeMenu.Append(wx.ID_ABOUT)
        homeMenu.Append(wx.ID_EXIT)

        editMenu = wx.Menu()

        menuPatient = wx.Menu()
        menuPatient.Append(wx.ID_NEW, "Bệnh nhân mới\tCTRL+N")
        self.menuUpdatePatient: wx.MenuItem = menuPatient.Append(
            wx.ID_EDIT, "Cập nhật thông tin bệnh nhân\tCTRL+U")
        self.menuDeletePatient: wx.MenuItem = menuPatient.Append(
            wx.ID_DELETE, "Xóa bệnh nhân\tCTRL+D")
        self.menuUpdatePatient.Enable(False)
        self.menuDeletePatient.Enable(False)
        editMenu.AppendSubMenu(menuPatient, "Bệnh nhân")

        menuVisit = wx.Menu()
        self.menuNewVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Lượt khám mới")
        self.menuInsertVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Lưu lượt khám\tCTRL+S")
        self.menuUpdateVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Cập nhật lượt khám\tCTRL+S")
        self.menuDeleteVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Xóa lượt khám cũ")

        self.menuNewVisit.Enable(False)
        self.menuInsertVisit.Enable(False)
        self.menuUpdateVisit.Enable(False)
        self.menuDeleteVisit.Enable(False)

        editMenu.AppendSubMenu(menuVisit, "Lượt khám")

        menuQueueList = wx.Menu()
        self.menuDeleteQueueList: wx.MenuItem = menuQueueList.Append(
            wx.ID_ANY, "Xóa lượt chờ khám")
        self.menuDeleteQueueList.Enable(False)
        editMenu.AppendSubMenu(menuQueueList, "Danh sách chờ")

        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_OPEN, "Tìm bệnh nhân cũ\tCTRL+O")

        editMenu.AppendSeparator()
        self.menuPrint: wx.MenuItem = editMenu.Append(wx.ID_PRINT, "In")
        self.menuPreview: wx.MenuItem = editMenu.Append(
            wx.ID_PREVIEW, "Xem trước bản in")
        self.menuPrint.Enable(False)
        self.menuPreview.Enable(False)

        storeMenu = wx.Menu()
        menuWarehouseSetup: wx.MenuItem = storeMenu.Append(
            wx.ID_ANY, "Kho thuốc")
        menuSampleSetup: wx.MenuItem = storeMenu.Append(wx.ID_ANY, "Toa mẫu")

        settingMenu = wx.Menu()
        menuSetup: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Cài đặt hệ thống")
        menuJSON: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Cài đặt qua JSON")
        menuResetSetting: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Khôi phục cài đặt gốc")

        self.Append(homeMenu, "&Home")
        self.Append(editMenu, "&Khám bệnh")
        self.Append(storeMenu, "&Quản lý")
        self.Append(settingMenu, "&Cài đặt")

        self.Bind(wx.EVT_MENU, self.onRefresh, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_MENU, self.onAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, lambda e: self.Parent.Close(), id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onNewPatient, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.onFindPatient, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onEditPatient, id=wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.onDeletePatient, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.onNewVisit, self.menuNewVisit)
        self.Bind(wx.EVT_MENU, self.onInsertVisit, self.menuInsertVisit)
        self.Bind(wx.EVT_MENU, self.onUpdateVisit, self.menuUpdateVisit)
        self.Bind(wx.EVT_MENU, self.onDeleteVisit, self.menuDeleteVisit)
        self.Bind(wx.EVT_MENU, self.onDeleteQueueList,
                  self.menuDeleteQueueList)
        self.Bind(wx.EVT_MENU, self.onPrint, id=wx.ID_PRINT)
        self.Bind(wx.EVT_MENU, self.onPreview, id=wx.ID_PREVIEW)
        self.Bind(wx.EVT_MENU, self.onWarehouseSetup, menuWarehouseSetup)
        self.Bind(wx.EVT_MENU, self.onSampleSetup, menuSampleSetup)
        self.Bind(wx.EVT_MENU, self.onSetup, menuSetup)
        self.Bind(wx.EVT_MENU, self.onMenuJSON, menuJSON)
        self.Bind(wx.EVT_MENU, self.onResetSetting, menuResetSetting)

    def onRefresh(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        mv.state.refresh()

    def onAbout(self, e):
        wx.MessageBox(
            "Phần mềm phòng khám tại nhà\nTác giả: Vương Kiến Thanh\nEmail: thanhstardust@outlook.com",
            style=wx.OK | wx.CENTRE | wx.ICON_NONE)

    def onNewPatient(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        NewPatientDialog(mv).ShowModal()

    def onFindPatient(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        FindPatientDialog(mv).ShowModal()

    def onEditPatient(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        page: wx.ListCtrl = mv.patient_book.GetPage(mv.patient_book.Selection)
        idx: int = page.GetFirstSelected()
        assert idx >= 0
        assert mv.state.patient is not None
        if EditPatientDialog(mv).ShowModal() == wx.ID_OK:
            page.EnsureVisible(idx)

    def onDeletePatient(self, e):
        if wx.MessageBox("Xác nhận?", "Xóa bệnh nhân", style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE) == wx.YES:
            mv: 'mainview.MainView' = self.GetFrame()
            p = mv.state.patient
            assert p is not None
            try:
                mv.con.delete(Patient, p.id)
                wx.MessageBox("Xóa thành công", "OK")
                mv.state.queuelist = mv.state.get_queuelist()
                mv.state.todaylist = mv.state.get_todaylist()
            except sqlite3.Error as error:
                wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onNewVisit(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        idx = mv.visit_list.GetFirstSelected()
        mv.visit_list.Select(idx, 0)

    def onInsertVisit(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        mv.savebtn.insert_visit()

    def onUpdateVisit(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        mv.savebtn.update_visit()

    def onDeleteVisit(self, e):
        if wx.MessageBox("Xác nhận?", "Xóa lượt khám", style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE) == wx.YES:
            mv: 'mainview.MainView' = self.GetFrame()
            v = mv.state.visit
            p = mv.state.patient
            assert v is not None
            assert p is not None
            try:
                mv.con.delete(Visit, v.id)
                wx.MessageBox("Xóa thành công", "OK")
                mv.state.visitlist = mv.con.select_visits_by_patient_id(
                    p.id, limit=5)
                mv.state.visit = None
            except sqlite3.Error as error:
                wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onDeleteQueueList(self, e):
        if wx.MessageBox("Xác nhận?", "Xóa lượt chờ khám", style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE) == wx.YES:
            mv: 'mainview.MainView' = self.GetFrame()
            p = mv.state.patient
            assert p is not None
            assert mv.patient_book.GetSelection() == 0
            try:
                mv.con.delete_queuelist_by_patient_id(p.id)
                wx.MessageBox("Xóa thành công", "OK")
                mv.state.refresh()
            except Exception as error:
                wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onPrint(self, e):
        printout = PrintOut(self.Parent)
        wx.Printer(wx.PrintDialogData(printdata)).Print(self, printout, True)

    def onPreview(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        printout = PrintOut(mv, preview=True)
        printdialogdata = wx.PrintDialogData(printdata)
        printpreview = wx.PrintPreview(printout, data=printdialogdata)
        printpreview.SetZoom(85)
        frame = wx.PreviewFrame(printpreview, mv)
        frame.Maximize()
        frame.Initialize()
        frame.Show()

    def onWarehouseSetup(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        WarehouseSetupDialog(mv).ShowModal()

    def onSampleSetup(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        SampleDialog(mv).ShowModal()

    def onSetup(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        SetupDialog(mv).ShowModal()

    def onMenuJSON(self, e):
        def openjson():
            if sys.platform == "win32":
                os.startfile(CONFIG_PATH, "edit")
            elif sys.platform == "linux":
                prog = shutil.which("gedit") or \
                    shutil.which("xed") or \
                    shutil.which("kwrite") or \
                    "xdg-open"
                subprocess.run([prog, CONFIG_PATH])
            elif sys.platform == "darwin":
                subprocess.run(['open', '-e', CONFIG_PATH])
        while True:
            openjson()
            mv: 'mainview.MainView' = self.GetFrame()
            try:
                mv.config = json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
                break
            except json.JSONDecodeError as error:
                wx.MessageBox(f"Lỗi JSON\n{error}", "Lỗi")

    def onResetSetting(self, e):
        if wx.MessageBox(
            "Khôi phục cài đặt gốc",
            "Cài đặt",
            style=wx.OK | wx.CANCEL | wx.CENTRE
        ) == wx.OK:
            shutil.copyfile(
                os.path.join(SRC_DIR, 'default_config.json'),
                CONFIG_PATH
            )
            mv: 'mainview.MainView' = self.GetFrame()
            mv.config = json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
            wx.MessageBox("Thành công", "Khôi phục cài đặt gốc")
