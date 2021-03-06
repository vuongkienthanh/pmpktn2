from db.db_class import *
from core import mainview
import core.other_func as otf
from core import menubar


import sqlite3
import wx


class State():
    '''Manager data, appearance and button state'''

    def __init__(self, mv: 'mainview.MainView') -> None:
        self.mv = mv
        self.Init()

    def Init(self) -> None:
        self._patient: Patient | None = None
        self._visit: Visit | None = None
        self._warehouse: Warehouse | None = None
        self._visitlist: list[sqlite3.Row] = []
        self._linedruglist: list[sqlite3.Row] = []
        self._queuelist: list[sqlite3.Row] = self.get_queuelist()
        self._todaylist: list[sqlite3.Row] = self.get_todaylist()
        self.warehouselist: list[Warehouse] = self.mv.con.selectall(
            Warehouse)
        self.sampleprescriptionlist: list[SamplePrescription] = self.mv.con.selectall(
            SamplePrescription)

    def refresh(self) -> None:
        self.patient = None
        self.visit = None
        self.warehouse = None
        self.visitlist = []
        self.linedruglist = []
        self.queuelist = self.get_queuelist()
        self.todaylist = self.get_todaylist()
        self.warehouselist = self.mv.con.selectall(Warehouse)
        self.sampleprescriptionlist = self.mv.con.selectall(SamplePrescription)

    @property
    def patient(self) -> Patient | None:
        return self._patient

    @patient.setter
    def patient(self, p: Patient | None):
        self._patient = p
        if p:
            self.onPatientSelect(p)
        else:
            self.onPatientDeselect()

    def onPatientSelect(self, p: Patient) -> None:
        self.mv.name.ChangeValue(p.name)
        self.mv.gender.ChangeValue(str(p.gender))
        self.mv.birthdate.ChangeValue(p.birthdate.strftime("%d/%m/%Y"))
        self.mv.age.ChangeValue(otf.bd_to_age(p.birthdate))
        self.mv.address.ChangeValue(p.address or '')
        self.mv.phone.ChangeValue(p.phone or '')
        self.mv.past_history.ChangeValue(p.past_history or '')
        self.mv.savebtn.SetLabel("L??u")
        self.mv.savebtn.Enable()
        self.mv.weight.Enable()
        self.mv.days.Enable()
        self.mv.recheck.Enable()
        self.mv.norecheck.Enable()
        self.mv.order_book.page0.use_sample_prescription_btn.Enable()
        self.visit = None
        self.visitlist = self.mv.con.select_visits_by_patient_id(p.id, limit=5)
        if len(self.visitlist) > 0:
            self.mv.get_weight_btn.Enable()
        else:
            self.mv.get_weight_btn.Disable()

        idx: int = self.mv.patient_book.Selection
        page: wx.ListCtrl = self.mv.patient_book.GetPage(idx)

        menubar: 'menubar.MyMenuBar' = self.mv.GetMenuBar()
        menubar.menuUpdatePatient.Enable()
        menubar.menuInsertVisit.Enable()
        if idx == 0:
            menubar.menuDeleteQueueList.Enable()

        page.SetFocus()

    def onPatientDeselect(self) -> None:
        self.mv.name.Clear()
        self.mv.gender.Clear()
        self.mv.birthdate.Clear()
        self.mv.age.Clear()
        self.mv.address.Clear()
        self.mv.phone.Clear()
        self.mv.past_history.Clear()
        self.mv.savebtn.SetLabel("L??u")
        self.mv.savebtn.Disable()
        self.mv.weight.Disable()
        self.mv.get_weight_btn.Disable()
        self.mv.days.Disable()
        self.mv.recheck.Disable()
        self.mv.norecheck.Disable()
        self.mv.order_book.page0.use_sample_prescription_btn.Disable()
        self.visit = None
        self.visitlist = []

        menubar: "menubar.MyMenuBar" = self.mv.GetMenuBar()
        menubar.menuUpdatePatient.Enable(False)
        menubar.menuInsertVisit.Enable(False)
        menubar.menuPrint.Enable(False)
        menubar.menuPreview.Enable(False)
        menubar.menuDeleteQueueList.Enable(False)

    @property
    def visit(self) -> Visit | None:
        return self._visit

    @visit.setter
    def visit(self, v: Visit | None) -> None:
        self._visit = v
        if v:
            self.onVisitSelect(v)
        else:
            self.onVisitDeselect()

    def onVisitSelect(self, v: Visit) -> None:
        self.mv.diagnosis.ChangeValue(v.diagnosis)
        self.mv.vnote.ChangeValue(v.vnote or '')
        self.mv.weight.SetValue(v.weight)
        self.mv.days.SetValue(v.days)
        self.mv.recheck.SetValue(v.recheck)
        self.mv.follow.SetFollow(v.follow)
        self.linedruglist = self.mv.con.select_linedrugs_by_visit_id(v.id)
        self.mv.savebtn.SetLabel("C???p nh???t")
        self.mv.price.FetchPrice()
        if self.mv.patient_book.GetSelection() == 0:
            self.mv.newvisitbtn.Enable()
        self.mv.order_book.page0.reuse_druglist_btn.Enable()
        menubar: "menubar.MyMenuBar" = self.mv.GetMenuBar()
        menubar.menuNewVisit.Enable()
        if self.patient:
            menubar.menuInsertVisit.Enable(False)
            self.mv.order_book.page0.use_sample_prescription_btn.Disable()
        menubar.menuUpdateVisit.Enable()
        menubar.menuDeleteVisit.Enable()
        menubar.menuPrint.Enable()
        menubar.menuPreview.Enable()
        self.mv.visit_list.SetFocus()

    def onVisitDeselect(self) -> None:
        self.mv.diagnosis.Clear()
        self.mv.vnote.Clear()
        self.mv.weight.SetValue(0)
        self.mv.days.SetValue(self.mv.config['so_ngay_toa_ve_mac_dinh'])
        self.mv.updatequantitybtn.Disable()
        self.mv.recheck.SetValue(self.mv.config['so_ngay_toa_ve_mac_dinh'])
        self.mv.follow.SetDefault()
        self.linedruglist = []
        self.mv.price.clear()
        self.mv.newvisitbtn.Disable()
        self.mv.savebtn.SetLabel("L??u")
        self.mv.order_book.page0.reuse_druglist_btn.Disable()
        menubar: "menubar.MyMenuBar" = self.mv.GetMenuBar()
        menubar.menuNewVisit.Enable(False)
        if self.patient:
            self.mv.order_book.page0.use_sample_prescription_btn.Enable()
            menubar.menuInsertVisit.Enable()
        menubar.menuUpdateVisit.Enable(False)
        menubar.menuDeleteVisit.Enable(False)
        self.warehouse = None

    @property
    def warehouse(self) -> Warehouse | None:
        return self._warehouse

    @warehouse.setter
    def warehouse(self, wh: Warehouse | None) -> None:
        self._warehouse = wh
        if wh:
            self.onWarehouseSelect(wh)
        else:
            self.onWarehouseDeselect()

    def onWarehouseSelect(self, wh: Warehouse) -> None:
        pg = self.mv.order_book.page0
        pg.drug_picker.SetValue(wh.name)
        pg.usage.SetLabel(wh.usage)
        pg.usage_unit.SetLabel(wh.usage_unit)
        pg.sale_unit.SetLabel(wh.sale_unit if wh.sale_unit else wh.usage_unit)
        pg.drug_picker.SelectAll()

    def onWarehouseDeselect(self) -> None:
        pg = self.mv.order_book.page0
        pg.drug_picker.ChangeValue('')
        pg.usage.SetLabel("{C??ch d??ng}")
        pg.usage_unit.SetLabel('{????n v???}')
        pg.sale_unit.SetLabel('{????n v???}')
        pg.times.Clear()
        pg.dose.Clear()
        pg.quantity.Clear()
        pg.note.Clear()

    @property
    def visitlist(self) -> list[sqlite3.Row]:
        return self._visitlist

    @visitlist.setter
    def visitlist(self, lv: list[sqlite3.Row]):
        self._visitlist = lv
        self.mv.visit_list.rebuild(lv)

    @property
    def linedruglist(self) -> list[sqlite3.Row]:
        return self._linedruglist

    @linedruglist.setter
    def linedruglist(self, lld: list[sqlite3.Row]):
        self._linedruglist = lld
        self.mv.order_book.page0.drug_list.rebuild(lld)

    @property
    def queuelist(self) -> list[sqlite3.Row]:
        return self._queuelist

    @queuelist.setter
    def queuelist(self, ql: list[sqlite3.Row]):
        self._queuelist = ql
        self.mv.patient_book.page0.rebuild(ql)

    @property
    def todaylist(self) -> list[sqlite3.Row]:
        return self._todaylist

    @todaylist.setter
    def todaylist(self, tdl: list[sqlite3.Row]):
        self._todaylist = tdl
        self.mv.patient_book.page1.rebuild(tdl)

    def get_wh_by_id(self, id: int) -> Warehouse | None:
        for wh in self.warehouselist:
            if id == wh.id:
                return wh

    def get_queuelist(self) -> list[sqlite3.Row]:
        return self.mv.con.execute(f"""
            SELECT
                p.id AS pid,
                p.name,
                p.gender,
                p.birthdate,
                ql.added_datetime
            FROM {Patient.table_name} AS p
            JOIN {QueueList.table_name} AS ql
            ON ql.patient_id = p.id
            ORDER BY ql.added_datetime ASC
        """).fetchall()

    def get_todaylist(self) -> list[sqlite3.Row]:
        return self.mv.con.execute(f"""
            SELECT
                p.id AS pid,
                p.name,
                p.gender,
                p.birthdate,
                v.id AS vid,
                v.exam_datetime
            FROM {Patient.table_name} AS p
            JOIN (
                SELECT id,patient_id,exam_datetime FROM {Visit.table_name}
                WHERE date(exam_datetime) = date('now', 'localtime')
            ) AS v
            ON v.patient_id = p.id
        """).fetchall()
