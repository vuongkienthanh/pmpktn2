import datetime as dt
import enum
from dataclasses import dataclass
import dataclasses
from typing import ClassVar, TypeVar
from decimal import Decimal
import sqlite3

T = TypeVar('T', bound='BASE')


class Gender(enum.Enum):
    m = 0
    f = 1

    def __str__(self):
        return ["Nam", "Nữ"][self.value]


class BASE():
    table_name: ClassVar[str]

    @classmethod
    def parse(cls, row):
        if isinstance(row, sqlite3.Row):
            return cls(**row)  # type:ignore
        elif isinstance(row, dict):
            # for csv.Reader, maybe others in future
            for n, t in cls.__annotations__.items():
                if t == int:
                    row[n] = int(row[n])
                elif t == Gender:
                    row[n] = Gender(int(row[n]))
                elif t == dt.date:
                    row[n] = dt.date.fromisoformat(row[n])
                elif t == dt.datetime | None:
                    if row[n] == '':
                        row[n] =None
                    else:
                        row[n] = dt.datetime.fromisoformat(row[n])
                elif t == Decimal:
                    row[n] = Decimal(row[n])
                elif t == str | None:
                    if row[n] == '':
                        row[n] = None
            return cls(**row)  # type:ignore

    @classmethod
    def fields(cls,) -> tuple[str]:
        return tuple((f.name for f in dataclasses.fields(cls) if f.name != 'id'))

    @classmethod
    def fields_as_str(cls) -> str:
        return ','.join(cls.fields())

    @classmethod
    def fields_as_qmarks(cls) -> str:
        num_of_qmark = len(cls.fields())
        return ','.join(['?'] * num_of_qmark)

    def into_sql_args(self) -> tuple:
        return tuple((getattr(self, attr) for attr in self.fields()))

    def add_id(self, id: int) -> None:
        self.id = id


@dataclass
class Patient(BASE):
    table_name = 'patients'
    name: str
    gender: Gender
    birthdate: dt.date
    id: int | None = None
    address: str | None = None
    phone: str | None = None
    past_history: str | None = None


@dataclass
class QueueList(BASE):
    table_name = 'queuelist'
    patient_id: int
    added_datetime: dt.datetime | None = None
    id: int | None = None


@dataclass
class Visit(BASE):
    table_name = 'visits'
    diagnosis: str
    weight: Decimal
    days: int
    patient_id: int
    follow: str | None = None
    id: int | None = None
    exam_datetime: dt.datetime | None = None
    vnote: str | None = None


@dataclass
class Linedrug(BASE):
    table_name = 'linedrugs'
    drug_id: int
    dose: str
    times: int
    quantity: int
    visit_id: int
    id: int | None = None
    note: str | None = None


@dataclass
class Warehouse(BASE):
    table_name = 'warehouse'
    name: str
    element: str
    quantity: int
    usage_unit: str
    usage: str
    purchase_price: int
    sale_price: int
    id: int | None = None
    sale_unit: str | None = None
    expire_date: dt.date | None = None
    made_by: str | None = None
    note: str | None = None


class VisitWithoutTime(Visit):
    @classmethod
    def fields(cls) -> tuple[str]:
        return tuple((f.name for f in dataclasses.fields(cls) if f.name not in ['id', 'exam_datetime']))


class QueueListWithoutTime(QueueList):
    @classmethod
    def fields(cls) -> tuple[str]:
        return tuple((f.name for f in dataclasses.fields(cls) if f.name not in ['id', 'added_datetime']))
