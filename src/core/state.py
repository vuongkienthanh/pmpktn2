from db.db_class import *
from core import main_view
import core.other_func as otf


import sqlite3


class State():
    '''Manager data, appearance and button state'''

    def __init__(self, mv: 'main_view.MainView') -> None:
        self.mv = mv
        self.Init()

    def Init(self) -> None:
        self._patient: Patient | None = None
        self._visit: Visit | None = None
        self._warehouse: Warehouse | None = None
        self._visitlist: list[sqlite3.Row] = []
        self._linedruglist: list[sqlite3.Row] = []
        self.queuelist: list[sqlite3.Row] = self.get_queuelist()
        self.todaylist: list[sqlite3.Row] = self.get_todaylist()
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
        self.mv.savebtn.SetLabel("Lưu")
        self.mv.savebtn.Enable()
        self.mv.updatequantitybtn.Enable()
        self.mv.weight.Enable()
        self.mv.get_weight_btn.Enable()
        self.mv.days.Enable()
        self.mv.recheck.Enable()
        self.mv.norecheck.Enable()
        self.visitlist = self.mv.con.select_visits_by_patient_id(p.id, limit=5)
        idx = self.mv.patient_book.Selection
        self.mv.GetMenuBar().menuUpdatePatient.Enable()
        self.mv.GetMenuBar().menuDeletePatient.Enable()
        self.mv.GetMenuBar().menuInsertVisit.Enable()
        self.mv.GetMenuBar().menuPrint.Enable()
        self.mv.GetMenuBar().menuPreview.Enable()
        self.mv.GetMenuBar().menuDeleteQueueList.Enable()
        self.mv.patient_book.GetPage(idx).SetFocus()

    def onPatientDeselect(self) -> None:
        self.mv.name.ChangeValue('')
        self.mv.gender.ChangeValue('')
        self.mv.birthdate.ChangeValue('')
        self.mv.age.ChangeValue('')
        self.mv.address.ChangeValue('')
        self.mv.phone.ChangeValue('')
        self.mv.past_history.ChangeValue('')
        self.mv.savebtn.SetLabel("Lưu")
        self.mv.savebtn.Disable()
        self.mv.updatequantitybtn.Disable()
        self.mv.weight.Disable()
        self.mv.get_weight_btn.Disable()
        self.mv.days.Disable()
        self.mv.recheck.Disable()
        self.mv.norecheck.Disable()
        self.visit = None
        self.visitlist = []
        self.mv.GetMenuBar().menuUpdatePatient.Enable(False)
        self.mv.GetMenuBar().menuDeletePatient.Enable(False)
        self.mv.GetMenuBar().menuInsertVisit.Enable(False)
        self.mv.GetMenuBar().menuPrint.Enable(False)
        self.mv.GetMenuBar().menuPreview.Enable(False)
        self.mv.GetMenuBar().menuDeleteQueueList.Enable(False)

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
        self.mv.follow.SetValue(v.follow)
        self.linedruglist = self.mv.con.select_linedrugs_by_visit_id(v.id)
        self.mv.savebtn.SetLabel("Cập nhật")
        self.mv.price.set_price()
        self.mv.newvisitbtn.Enable()
        self.mv.order_book.GetPage(0).reuse_druglist_btn.Enable()
        self.mv.GetMenuBar().menuNewVisit.Enable()
        if self.patient is not None:
            self.mv.GetMenuBar().menuInsertVisit.Enable(False)
        self.mv.GetMenuBar().menuUpdateVisit.Enable()
        self.mv.GetMenuBar().menuDeleteVisit.Enable()
        self.mv.visit_list.SetFocus()

    def onVisitDeselect(self) -> None:
        self.mv.diagnosis.ChangeValue('')
        self.mv.vnote.ChangeValue('')
        self.mv.weight.SetValue(0)
        self.mv.days.SetValue(self.mv.config['so_ngay_toa_ve_mac_dinh'])
        self.mv.recheck.SetValue(self.mv.config['so_ngay_toa_ve_mac_dinh'])
        self.mv.follow.ChangeValue("")
        self.linedruglist = []
        self.mv.price.ChangeValue('')
        self.mv.newvisitbtn.Disable()
        self.mv.savebtn.SetLabel("Lưu")
        self.mv.order_book.GetPage(0).reuse_druglist_btn.Disable()
        self.mv.GetMenuBar().menuNewVisit.Enable(False)
        if self.patient is not None:
            self.mv.GetMenuBar().menuInsertVisit.Enable()
        self.mv.GetMenuBar().menuUpdateVisit.Enable(False)
        self.mv.GetMenuBar().menuDeleteVisit.Enable(False)
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

    def onWarehouseSelect(self, wh) -> None:
        pg = self.mv.order_book.GetPage(0)
        pg.drug_picker.SetValue(wh.name)
        pg.usage_unit.SetLabel(wh.usage_unit)
        pg.sale_unit.SetLabel(wh.sale_unit if wh.sale_unit else wh.usage_unit)
        pg.drug_picker.SelectAll()

    def onWarehouseDeselect(self) -> None:
        pg = self.mv.order_book.GetPage(0)
        pg.drug_picker.ChangeValue('')
        pg.usage_unit.SetLabel('{Đơn vị}')
        pg.sale_unit.SetLabel('{Đơn vị}')
        pg.times.ChangeValue('')
        pg.dose.ChangeValue('')
        pg.quantity.ChangeValue('')
        pg.note.ChangeValue('')

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
        self.mv.order_book.GetPage(0).drug_list.rebuild(lld)

    def get_wh_by_id(self, id: int):
        for wh in self.warehouselist:
            if id == wh.id:
                return wh

    def get_queuelist(self) -> list[sqlite3.Row]:
        return self.mv.con.execute("""
            SELECT
                p.id AS pid,
                p.name,
                p.gender,
                p.birthdate,
                ql.added_datetime
            FROM patients AS p
            JOIN queuelist AS ql
            ON ql.patient_id = p.id
            ORDER BY ql.added_datetime ASC
        """).fetchall()

    def get_todaylist(self) -> list[sqlite3.Row]:
        return self.mv.con.execute("""
            SELECT
                p.id AS pid,
                p.name,
                p.gender,
                p.birthdate,
                v.id AS vid,
                v.exam_datetime
            FROM patients AS p
            JOIN (
                SELECT id,patient_id,exam_datetime FROM visits
                WHERE date(exam_datetime) = date('now', 'localtime')
            ) AS v
            ON v.patient_id = p.id
        """).fetchall()
