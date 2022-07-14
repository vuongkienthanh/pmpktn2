import datetime as dt
import enum
from dataclasses import dataclass
import dataclasses
from typing import ClassVar, TypeVar
from decimal import Decimal
from typing import Any
from collections.abc import Mapping


class Gender(enum.Enum):
    m = 0
    f = 1

    def __str__(self):
        return ["Nam", "Nữ"][self.value]


@dataclass
class BASE():
    """
    Base Abstract Class for derived sql table
    - `table_name`: name of table in sqlite database
    - `not_in_fields`: names of fields that are not returned by classmethod fields() 
    """
    table_name: ClassVar[str]
    not_in_fields: ClassVar[list[str]]
    id: int

    @classmethod
    def parse(cls, row: Mapping[str, Any]):
        """
        Return the BASE object from a mapping with no conversion
        """
        return cls(**row)

    @classmethod
    def fields(cls) -> tuple[str]:
        """
        Return fields used in sql insert & update string
        """
        return tuple((f.name for f in dataclasses.fields(cls) if f.name not in cls.not_in_fields))

    @classmethod
    def commna_joined_fields(cls) -> str:
        """
        Return comma-joined fields
        """
        return ','.join(cls.fields())

    @classmethod
    def qmark_style_fields(cls) -> str:
        """
        Return qmark-style placeholders
        """
        num_of_qmark = len(cls.fields())
        return ','.join(['?'] * num_of_qmark)

    @classmethod
    def named_style_fields(cls) -> str:
        """
        Return named-style placeholders
        """
        return ','.join([f":{f}" for f in cls.fields()])

    def into_sql_args(self) -> tuple:
        return tuple((getattr(self, attr) for attr in self.fields()))

    def into_sql_kwargs(self) -> dict[str, Any]:
        return {attr: getattr(self, attr) for attr in self.fields()}


@dataclass
class Patient(BASE):
    table_name = 'patients'
    not_in_fields = ['id']
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
    not_in_fields = ['id', 'added_datetime']
    id: int
    added_datetime: dt.datetime
    patient_id: int


@dataclass
class Visit(BASE):
    table_name = 'visits'
    not_in_fields = ['id', 'exam_datetime']
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
    not_in_fields = ['id']
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
    not_in_fields = ['id']
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
    not_in_fields = ['id']
    id: int
    name: str


@dataclass
class LineSamplePrescription(BASE):
    table_name = 'linesampleprescription'
    not_in_fields = ['id']
    id: int
    drug_id: int
    sample_id: int
    times: int
    dose: str


T = TypeVar('T', bound='BASE')
