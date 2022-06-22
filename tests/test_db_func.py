from test_path_init import *
from db.db_class import *
import db.db_func as dbf
from db.csv_helper import CSVReader

import sqlite3
import unittest


class TestDBFbase(unittest.TestCase):
    def setUp(self):
        self.con: dbf.Connection = dbf.Connection(":memory:")
        self.con.make_db()

    def get_file(self, s: str) -> str:
        return os.path.join(SAMPLE_DIR, s)

    def tearDown(self):
        self.con.close()


class TestTables(TestDBFbase):
    def test_make_enough_tables(self):
        with self.con.sqlcon as con:
            rows = con.execute(
                "SELECT name FROM sqlite_master where type='table'").fetchall()
            self.assertEqual(len(rows), 5)


class TestLinewarehouse(TestDBFbase):
    def setUp(self):
        super().setUp()
        self.t = Warehouse
        self.reader = CSVReader(self.t, self.get_file('warehouse.csv'))

    def test_insert(self):
        with self.reader as reader:
            lwh = next(reader)
            res = self.con.insert(lwh)
            if res is None:
                raise Exception("insert fail")
            else:
                lastrowid, rowcount = res
                self.assertEqual((lastrowid, rowcount), (1, 1))

    def test_insertmany(self):
        with self.reader as reader:
            rowcount = self.con.insertmany(reader)
            if rowcount is None:
                raise Exception("insertmany fail")
            else:
                self.assertEqual(rowcount, 10)

    def test_select(self):
        with self.reader as reader:
            lwh = next(reader)
            res = self.con.insert(lwh)
            if res is not None:
                lastrowid, _ = res
                lwh.add_id(lastrowid)
                rhs = self.con.select(self.t, lastrowid)
                if rhs is None:
                    raise Exception('select fail')
                else:
                    self.assertEqual(lwh, rhs)

    def test_selectall(self):
        with self.reader as reader:
            llwh = reader.to_list()
            self.con.insertmany(llwh, self.t)
            [lwh.add_id(i + 1) for i, lwh in enumerate(llwh)]
            rhs = self.con.selectall(self.t)
            if rhs is None:
                raise Exception('selectall fail')
            else:
                rhs = list(rhs)
                self.assertEqual(llwh, rhs)


class TestPatient(TestDBFbase):
    def setUp(self):
        super().setUp()
        self.t = Patient
        self.reader = CSVReader(Patient, self.get_file('patients.csv'))

    def test_insert(self):
        with self.reader as reader:
            p = next(reader)
            res = self.con.insert(p)
            if res is None:
                raise Exception('insert fail')
            else:
                lastrowid, rowcount = res
                self.assertEqual((lastrowid, rowcount), (1, 1))

    def test_insertmany(self):
        with self.reader as reader:
            rowcount = self.con.insertmany(reader)
            if rowcount is None:
                raise Exception("insertmany fail")
            else:
                self.assertEqual(rowcount, 10)

    def test_select(self):
        with self.reader as reader:
            p = next(reader)
            res = self.con.insert(p)
            if res is not None:
                lastrowid, _ = res
                p.add_id(lastrowid)
                rhs = self.con.select(self.t, lastrowid)
                if rhs is None:
                    raise Exception('select fail')
                else:
                    self.assertEqual(p, rhs)

    def test_selectall(self):
        with self.reader as reader:
            lp = reader.to_list()
            self.con.insertmany(lp, self.t)
            [p.add_id(i + 1) for i, p in enumerate(lp)]
            rhs = self.con.selectall(self.t)
            if rhs is None:
                raise Exception('selectall fail')
            else:
                rhs = list(rhs)
                self.assertEqual(lp, rhs)


class TestVisit(TestDBFbase):
    def setUp(self):
        super().setUp()
        self.t = Visit
        self.patient_reader = CSVReader(Patient, self.get_file('patients.csv'))
        self.reader = CSVReader(self.t, self.get_file('visits.csv'))

    def with_no_patient(self):
        self.patient_reader.close()

    def with_one_patient(self):
        with self.patient_reader as reader:
            self.con.insert(next(reader))

    def with_ten_patient(self):
        with self.patient_reader as reader:
            self.con.insertmany(reader)

    def test_insert_with_no_patient_fail(self):
        self.with_no_patient()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.reader as reader:
                self.con.insert(next(reader))

    def test_insert_with_one_patient(self):
        self.with_one_patient()
        with self.reader as reader:
            v = next(reader)
            res = self.con.insert(v)
            if res is None:
                raise Exception('insert fail')
            else:
                lastrowid, rowcount = res
                self.assertEqual((lastrowid, rowcount), (1, 1))

    def test_insertmany_with_one_patient_fail(self):
        self.with_one_patient()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.reader as reader:
                self.con.insertmany(reader)

    def test_insertmany_with_ten_patient(self):
        self.with_ten_patient()
        with self.reader as reader:
            rowcount = self.con.insertmany(reader)
            if rowcount is None:
                raise Exception("insertmany fail")
            else:
                self.assertEqual(rowcount, 10)

    def test_select(self):
        self.with_one_patient()
        with self.reader as reader:
            v = next(reader)
            res = self.con.insert(v)
            if res is not None:
                lastrowid, _ = res
                v.add_id(lastrowid)
                rhs = self.con.select(self.t, lastrowid)
                if rhs is None:
                    raise Exception('select fail')
                else:
                    self.assertEqual(v, rhs)

    def test_selectall(self):
        self.with_ten_patient()
        with self.reader as reader:
            lv = reader.to_list()
            self.con.insertmany(lv, self.t)
            [v.add_id(i + 1) for i, v in enumerate(lv)]
            rhs = self.con.selectall(self.t)
            if rhs is None:
                raise Exception('selectall fail')
            else:
                rhs = list(rhs)
                self.assertEqual(lv, rhs)


class TestLinedrug(TestDBFbase):
    def setUp(self):
        super().setUp()
        self.t = Linedrug
        self.warehouse_reader = CSVReader(
            Warehouse, self.get_file('warehouse.csv'))
        self.patient_reader = CSVReader(Patient, self.get_file('patients.csv'))
        self.visit_reader = CSVReader(Visit, self.get_file('visits.csv'))
        self.reader = CSVReader(self.t, self.get_file('linedrugs.csv'))
        with self.warehouse_reader as reader:
            self.con.insertmany(reader)

    def with_no_visit(self):
        self.patient_reader.close()
        self.visit_reader.close()

    def with_one_visit(self):
        with self.patient_reader as reader:
            self.con.insert(next(reader))
        with self.visit_reader as reader:
            self.con.insert(next(reader))

    def with_ten_visit(self):
        with self.patient_reader as reader:
            self.con.insertmany(reader)
        with self.visit_reader as reader:
            self.con.insertmany(reader)

    def test_insert_with_no_visit_fail(self):
        self.with_no_visit()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.reader as reader:
                self.con.insert(next(reader))

    def test_insert_with_one_visit(self):
        self.with_one_visit()
        with self.reader as reader:
            ld = next(reader)
            res = self.con.insert(ld)
            if res is None:
                raise Exception("insert fail")
            else:
                lastrowid, rowcount = res
                self.assertEqual((lastrowid, rowcount), (1, 1))

    def test_insertmany_with_one_visit_fail(self):
        self.with_one_visit()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.reader as reader:
                self.con.insertmany(reader)

    def test_insertmany_with_ten_visit(self):
        self.with_ten_visit()
        with self.reader as reader:
            rowcount = self.con.insertmany(reader)
            if rowcount is None:
                raise Exception("insertmany fail")
            else:
                self.assertEqual(rowcount, 10)

    def test_select(self):
        self.with_one_visit()
        with self.reader as reader:
            ld = next(reader)
            res = self.con.insert(ld)
            if res is not None:
                lastrowid, _ = res
                ld.add_id(lastrowid)
                rhs = self.con.select(self.t, lastrowid)
                if rhs is None:
                    raise Exception("select fail")
                else:
                    self.assertEqual(ld, rhs)

    def test_selectall(self):
        self.with_ten_visit()
        with self.reader as reader:
            lld = reader.to_list()
            self.con.insertmany(lld, self.t)
            [ld.add_id(i + 1) for i, ld in enumerate(lld)]
            rhs = self.con.selectall(self.t)
            if rhs is None:
                raise Exception('selectall fail')
            else:
                rhs = list(rhs)
                self.assertEqual(lld, rhs)


class TestQueueList(TestDBFbase):
    def setUp(self):
        super().setUp()
        self.t = QueueList
        self.patient_reader = CSVReader(Patient, self.get_file('patients.csv'))
        self.reader = CSVReader(self.t, self.get_file('queuelist.csv'))

    def with_no_patient(self):
        self.patient_reader.close()

    def with_one_patient(self):
        with self.patient_reader as reader:
            self.con.insert(next(reader))

    def with_ten_patient(self):
        with self.patient_reader as reader:
            self.con.insertmany(reader)

    def test_insert_with_no_patient_fail(self):
        self.with_no_patient()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.reader as reader:
                self.con.insert(next(reader))

    def test_insert_with_one_patient(self):
        self.with_one_patient()
        with self.reader as reader:
            ql = next(reader)
            res = self.con.insert(ql)
            if res is None:
                raise Exception("insert fail")
            else:
                lastrowid, rowcount = res
                self.assertEqual((lastrowid, rowcount), (1, 1))

    def test_insertmany_with_one_patient_fail(self):
        self.with_one_patient()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.reader as reader:
                self.con.insertmany(reader)

    def test_insertmany_with_ten_patient(self):
        self.with_ten_patient()
        with self.reader as reader:
            rowcount = self.con.insertmany(reader)
            if rowcount is None:
                raise Exception("insertmany fail")
            else:
                self.assertEqual(rowcount, 10)

    def test_select(self):
        self.with_one_patient()
        with self.reader as reader:
            ql = next(reader)
            res = self.con.insert(ql)
            if res is not None:
                lastrowid, _ = res
                ql.add_id(lastrowid)
                rhs = self.con.select(self.t, lastrowid)
                if rhs is None:
                    raise Exception("select fail")
                else:
                    self.assertEqual(ql, rhs)

    def test_selectall(self):
        self.with_ten_patient()
        with self.reader as reader:
            lql = reader.to_list()
            self.con.insertmany(lql, self.t)
            [ql.add_id(i + 1) for i, ql in enumerate(lql)]
            rhs = self.con.selectall(self.t)
            if rhs is None:
                raise Exception('selectall fail')
            else:
                rhs = list(rhs)
                self.assertEqual(lql, rhs)

    def test_delete(self):
        self.with_one_patient()
        with self.reader as reader:
            ql = next(reader)
            res = self.con.insert(ql)
            if res is not None:
                lastrowid, _ = res
                ql.add_id(lastrowid)
                rowcount = self.con.delete(ql)
                if rowcount is None:
                    raise Exception("delete fail")
                else:
                    self.assertEqual(rowcount, 1)


class TestDBF(TestDBFbase):
    def setUp(self):
        super().setUp()
        self.con.make_sample()

    def test_get_visits(self):
        lv = self.con.select_visits_by_patient_id(1)
        self.assertEqual(len(list(lv)), 6)

    def test_get_visits_limit(self):
        limit = 2
        lv = self.con.select_visits_by_patient_id(1, limit)
        self.assertEqual(len(list(lv)), limit)
