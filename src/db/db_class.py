import datetime as dt
import enum
from dataclasses import dataclass
import dataclasses
from typing import ClassVar, TypeVar
from decimal import Decimal
import sqlite3


class Gender(enum.Enum):
    m = 0
    f = 1

    def __str__(self):
        return ["Nam", "Nữ"][self.value]


@dataclass
class BASE():
    table_name: ClassVar[str]
    have_default: ClassVar[list[str]]

    @classmethod
    def parse(cls, row:sqlite3.Row):
        return cls(**row)  # type:ignore


    @classmethod
    def fields(cls,) -> tuple[str]:
        return tuple((f.name for f in dataclasses.fields(cls) if f.name not in cls.have_default))

    @classmethod
    def fields_as_str(cls) -> str:
        return ','.join(cls.fields())

    @classmethod
    def fields_as_qmarks(cls) -> str:
        num_of_qmark = len(cls.fields())
        return ','.join(['?'] * num_of_qmark)
    @classmethod
    def fields_as_names(cls) -> str:
        return ','.join([f":{f}" for f in cls.fields()])

    def into_sql_args(self) -> tuple:
        return tuple((getattr(self, attr) for attr in self.fields()))

    def add_id(self, id: int) -> None:
        self.id = id


@dataclass
class Patient(BASE):
    table_name = 'patients'
    have_default = ['id']
    id: int 
    name: str
    gender: Gender
    birthdate: dt.date
    address: str | None = None
    phone: str | None = None
    past_history: str | None = None


@dataclass
class QueueList(BASE):
    table_name = 'queuelist'
    have_default = ['id', 'added_datetime']
    id: int
    added_datetime: dt.datetime
    patient_id: int


@dataclass
class Visit(BASE):
    table_name = 'visits'
    have_default = ['id', 'exam_datetime']
    id: int
    exam_datetime: dt.datetime
    diagnosis: str
    weight: Decimal
    days: int
    recheck: int
    patient_id: int
    follow: str | None = None
    vnote: str | None = None


@dataclass
class LineDrug(BASE):
    table_name = 'linedrugs'
    have_default = ['id']
    id: int
    drug_id: int
    dose: str
    times: int
    quantity: int
    visit_id: int
    note: str | None = None


@dataclass
class Warehouse(BASE):
    table_name = 'warehouse'
    have_default = ['id']
    id: int
    name: str
    element: str
    quantity: int
    usage_unit: str
    usage: str
    purchase_price: int
    sale_price: int
    sale_unit: str | None = None
    expire_date: dt.date | None = None
    made_by: str | None = None
    note: str | None = None


@dataclass
class SamplePrescription(BASE):
    table_name = 'sampleprescription'
    have_default = ['id']
    id: int
    name: str


@dataclass
class LineSamplePrescription(BASE):
    table_name = 'linesampleprescription'
    have_default = ['id']
    id: int
    drug_id: int
    sample_id: int
    dose: str
    times: int


T = TypeVar('T', bound='BASE')
