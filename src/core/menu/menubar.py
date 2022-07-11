import subprocess
from path_init import SRC_DIR, CONFIG_PATH
from db.db_class import *
from core.menu.find_patient_dialog import FindPatientDialog
from core.menu.patient_dialog import EditPatientDialog, NewPatientDialog
from core.menu.setup_dialog import SetupDialog
from core.menu.warehouse_dialog import WarehouseSetupDialog
from core.menu.sample_prescription_dialog import SampleDialog
from core.printing.printer import PrintOut, printdata
import wx
import shutil
import os.path
import sys
import os
import sqlite3

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

        editMenu.Append(wx.ID_NEW, "Bệnh nhân mới")
        editMenu.Append(wx.ID_OPEN, "Tìm bệnh nhân cũ")
        editMenu.AppendSeparator()

        menuPatient = wx.Menu()
        menuPatient.Append(wx.ID_NEW, "Bệnh nhân mới")
        self.menuUpdatePatient = menuPatient.Append(
            wx.ID_EDIT, "Cập nhật thông tin bệnh nhân\tCTRL+U")
        self.menuDeletePatient = menuPatient.Append(
            wx.ID_DELETE, "Xóa bệnh nhân\tCTRL+D")
        self.menuUpdatePatient.Enable(False)
        self.menuDeletePatient.Enable(False)
        editMenu.AppendSubMenu(menuPatient, "Bệnh nhân")

        menuVisit = wx.Menu()
        self.menuNewVisit = menuVisit.Append(wx.ID_ANY, "Lượt khám mới")
        self.menuInsertVisit = menuVisit.Append(wx.ID_ANY, "Lưu lượt khám")
        self.menuUpdateVisit = menuVisit.Append(
            wx.ID_ANY, "Cập nhật lượt khám")
        self.menuNewVisit.Enable(False)
        self.menuInsertVisit.Enable(False)
        self.menuUpdateVisit.Enable(False)
        self.menuDeleteVisit = menuVisit.Append(wx.ID_ANY, "Xóa lượt khám cũ")
        self.menuDeleteVisit.Enable(False)
        editMenu.AppendSubMenu(menuVisit, "Lượt khám")

        menuQueueList = wx.Menu()
        self.menuDeleteQueueList = menuQueueList.Append(
            wx.ID_ANY, "Xóa lượt chờ khám")
        self.menuDeleteQueueList.Enable(False)
        editMenu.AppendSubMenu(menuQueueList, "Danh sách chờ")

        menuDrug = wx.Menu()
        menuUpdateQuantity = menuDrug.Append(
            wx.ID_ANY, "Cập nhật lại số lượng thuốc trong toa theo ngày")
        editMenu.AppendSubMenu(menuDrug, "Thuốc")

        editMenu.AppendSeparator()
        self.menuPrint = editMenu.Append(wx.ID_PRINT, "In")
        self.menuPreview = editMenu.Append(wx.ID_PREVIEW, "Xem trước bản in")
        self.menuPrint.Enable(False)
        self.menuPreview.Enable(False)

        storeMenu = wx.Menu()
        menuWarehouseSetup = storeMenu.Append(wx.ID_ANY, "Kho thuốc")
        menuSampleSetup = storeMenu.Append(wx.ID_ANY, "Toa mẫu")

        settingMenu = wx.Menu()
        menuSetup = settingMenu.Append(wx.ID_ANY, "Cài đặt hệ thống")
        menuJSON = settingMenu.Append(wx.ID_ANY, "Cài đặt qua JSON")
        menuResetSetting = settingMenu.Append(
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
        self.Bind(wx.EVT_MENU, self.onUpdateQuantity, menuUpdateQuantity)
        self.Bind(wx.EVT_MENU, self.onPrint, self.menuPrint)
        self.Bind(wx.EVT_MENU, self.onPreview, self.menuPreview)
        self.Bind(wx.EVT_MENU, self.onWarehouseSetup, menuWarehouseSetup)
        self.Bind(wx.EVT_MENU, self.onSampleSetup, menuSampleSetup)
        self.Bind(wx.EVT_MENU, self.onSetup, menuSetup)
        self.Bind(wx.EVT_MENU, self.onMenuJSON, menuJSON)
        self.Bind(wx.EVT_MENU, self.onResetSetting, menuResetSetting)

    def onRefresh(self, e):
        self.GetFrame().refresh()

    def onAbout(self, e):
        wx.MessageBox(
            "Phần mềm phòng khám tại nhà\nTác giả: Vương Kiến Thanh\nEmail: thanhstardust@outlook.com",
            style=wx.OK | wx.CENTRE | wx.ICON_NONE)

    def onNewPatient(self, e):
        NewPatientDialog(self.GetFrame()).ShowModal()

    def onFindPatient(self, e):
        FindPatientDialog(self.GetFrame()).ShowModal()

    def onEditPatient(self, e):
        mv = self.GetFrame()
        page = mv.patient_book.GetPage(mv.patient_book.Selection)
        idx = page.GetFirstSelected()
        if EditPatientDialog(mv, mv.state.patient).ShowModal() == wx.ID_OK:
            page.EnsureVisible(idx)

    def onDeletePatient(self, e):
        mv = self.GetFrame()
        try:
            mv.con.delete(Patient, mv.state.patient.id)
            wx.MessageBox("Xóa thành công", "OK")
            mv.refresh()
        except sqlite3.Error as error:
            wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onNewVisit(self, e):
        idx = self.GetFrame().visit_list.GetFirstSelected()
        self.GetFrame().visit_list.Select(idx, 0)

    def onInsertVisit(self, e):
        self.GetFrame().savebtn.insert_visit()

    def onUpdateVisit(self, e):
        self.GetFrame().savebtn.update_visit()

    def onDeleteVisit(self, e):
        mv = self.GetFrame()
        try:
            mv.con.delete(Visit, mv.state.visit.id)
            wx.MessageBox("Xóa thành công", "OK")
            mv.state.refresh()
        except sqlite3.Error as error:
            wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onDeleteQueueList(self, e):
        mv = self.GetFrame()
        try:
            mv.con.delete_queuelist_by_patient_id(mv.state.patient.id)
            wx.MessageBox("Xóa thành công", "OK")
            mv.refresh()
        except sqlite3.Error as error:
            wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onUpdateQuantity(self, e):
        self.GetFrame().updatequantitybtn.onClick(None)

    def onPrint(self, e):
        printout = PrintOut(self.Parent)
        wx.Printer(wx.PrintDialogData(printdata)).Print(self, printout, True)

    def onPreview(self, e):
        printout = PrintOut(self.Parent, preview=True)
        printdialogdata = wx.PrintDialogData(printdata)
        printpreview = wx.PrintPreview(printout, data=printdialogdata)
        printpreview.SetZoom(85)
        frame = wx.PreviewFrame(printpreview, self.GetFrame())
        frame.Maximize()
        frame.Initialize()
        frame.Show()

    def onWarehouseSetup(self, e):
        WarehouseSetupDialog(self.GetFrame()).ShowModal()

    def onSampleSetup(self, e):
        SampleDialog(parent=self.GetFrame()).ShowModal()

    def onSetup(self, e):
        SetupDialog(self.GetFrame()).ShowModal()

    def onMenuJSON(self, e):
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

    def onResetSetting(self, e):
        if wx.MessageBox(
            "Khôi phục cài đặt gốc",
            "Cài đặt",
            style=wx.OK | wx.CANCEL | wx.CENTRE
        ) == wx.OK:
            shutil.copyfile(
                os.path.join(os.path.dirname(SRC_DIR), 'default_config.json'),
                CONFIG_PATH
            )
