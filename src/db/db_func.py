import decimal
from db.csv_helper import CSVReader
from db.db_class import *
from path_init import SAMPLE_DIR, DB_DIR
from db.csv_helper import CSVReader
import os.path
import sqlite3
from decimal import Decimal
from collections.abc import Iterable
from typing import overload


class Connection():
    def __init__(self, path: str):
        self.sqlcon = self._get_db_connection(path)

    def close(self):
        self.sqlcon.close()

    def register_custom_type(self):
        def custom_type_decimal():
            def adapt(decimal: Decimal) -> str:
                return str(decimal)

            def convert(b: bytes) -> Decimal:
                return Decimal(b.decode())
            sqlite3.register_adapter(Decimal, adapt)
            sqlite3.register_converter("DECIMAL", convert)

        def custom_type_gender():
            def adapt(gender: Gender) -> int:
                return gender.value

            def convert(b: bytes) -> Gender:
                return Gender(int(b))
            sqlite3.register_adapter(Gender, adapt)
            sqlite3.register_converter("GENDER", convert)

        custom_type_decimal()
        custom_type_gender()

    def _get_db_connection(self, path: str) -> sqlite3.Connection:
        self.register_custom_type()
        con = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def make_db(self):
        with self.sqlcon as con:
            create_table_sql_path = os.path.join(
                DB_DIR, 'create_table.sql')
            with open(create_table_sql_path, 'r') as f:
                sql = f.read()
                con.executescript(sql)

    def make_sample(self):
        def f(s): return os.path.join(SAMPLE_DIR, s)
        for reader in [
            CSVReader(Warehouse, f('warehouse.csv')),
            CSVReader(Patient, f('patients.csv')),
            CSVReader(Visit, f('visits.csv')),
            CSVReader(LineDrug, f('linedrugs.csv')),
            CSVReader(QueueList, f('queuelist.csv')),
            CSVReader(SamplePrescription, f('sampleprescription.csv')),
            CSVReader(LineSamplePrescription, f('linesampleprescription.csv')),
        ]:
            with self.sqlcon as con:
                con.executemany(f"""
                    INSERT INTO {reader.t.table_name} ({','.join(reader.fields)})
                    VALUES ({','.join(['?']* len(reader.fields))})
                """, (
                    tuple(getattr(row, attr)
                          for attr in reader.fields)
                    for row in reader
                ))
            reader.close()
        self.insert(Visit, {
            "diagnosis": "Viêm ruột thừa",
            "weight": decimal.Decimal(10),
            "days": 2,
            "recheck": 2,
            "patient_id": 1,
            "follow": "follow",
            "vnote": "dynamic created"
        })

    def __enter__(self):
        return self.sqlcon.__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.sqlcon.__exit__(exc_type, exc_value, exc_traceback)

    def execute(self, sql,*parameters):
        return self.sqlcon.execute(sql, *parameters)

    def insert(self, t: type[BASE], base: dict) -> int | None:
        with self.sqlcon as con:
            cur = con.execute(f"""
                INSERT INTO {t.table_name} ({t.commna_joined_fields()})
                VALUES ({t.named_style_fields()})
            """,
                              base
                              )
            assert cur.lastrowid is not None
            return cur.lastrowid

    def select(self, t: type[T], id: int) -> T | None:
        row = self.execute(
            f"SELECT * FROM {t.table_name} WHERE id={id}",
        ).fetchone()
        if row is None:
            return None
        else:
            return t.parse(row)

    def selectall(self, t: type[T]) -> list[T]:
        rows = self.execute(
            f"SELECT * FROM {t.table_name}"
        ).fetchall()
        return [t.parse(row) for row in rows]


    def delete(self, t: type[BASE], id: int) -> int | None:
        with self.sqlcon as con:
            return con.execute(
                f"DELETE FROM {t.table_name} WHERE id = {id}"
            ).rowcount

    def update(self, base: BASE) -> int | None:
        t = type(base)
        with self.sqlcon as con:
            return con.execute(f"""
                UPDATE {t.table_name} SET ({t.commna_joined_fields()})
                = ({t.qmark_style_fields()})
                WHERE id = {base.id}
            """,
                               base.into_sql_args()
                               ).rowcount


#########################################################################
#########################################################################
#########################################################################


    def select_visits_by_patient_id(self, pid: int, limit: int = -1) -> list[sqlite3.Row]:
        query = f"""
            SELECT id AS vid, exam_datetime,diagnosis
            FROM {Visit.table_name}
            WHERE visits.patient_id = {pid}
            ORDER BY exam_datetime DESC
            LIMIT {limit}
        """
        return self.sqlcon.execute(query).fetchall()

    def select_linedrugs_by_visit_id(self, vid: int) -> list[sqlite3.Row]:
        query = f"""
            SELECT 
                ld.id,
                ld.drug_id, wh.name,
                ld.times, ld.dose,
                ld.quantity, ld.note,
                wh.usage, wh.usage_unit,
                wh.sale_unit
            FROM (SELECT * FROM linedrugs
                  WHERE visit_id = {vid}
            ) AS ld
            JOIN warehouse AS wh
            ON wh.id = ld.drug_id
        """
        return self.sqlcon.execute(query).fetchall()

    def delete_queuelist_by_patient_id(self, pid) -> int | None:
        with self.sqlcon as con:
            return con.execute(
                f"DELETE FROM {QueueList.table_name} WHERE patient_id = {pid}"
            ).rowcount
