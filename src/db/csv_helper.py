from db.db_class import *
import csv
import datetime as dt
from decimal import Decimal


class CSVReader(csv.DictReader):
    def __init__(self, t: type[BASE], csvfilepath: str):
        self.t = t
        self.csvfile = open(csvfilepath, 'r', encoding='utf-8')
        self.fields = self.csvfile.readline().strip().split(',')
        self.csvfile.seek(0)
        super().__init__(self.csvfile)

    def get_type(self):
        return self.t

    def parse(self, row):
        for n, t in self.t.__annotations__.items():
            if t == int:
                row[n] = int(row[n])
            elif t == Gender:
                row[n] = Gender(int(row[n]))
            elif t == dt.date:
                row[n] = dt.date.fromisoformat(row[n])
            elif t == dt.datetime:
                row[n] = dt.datetime.fromisoformat(row[n])
            elif t == Decimal:
                row[n] = Decimal(row[n])
            elif t == str | None:
                if row[n] == '':
                    row[n] = None
        return self.t(**row)

    def __iter__(self):
        return super().__iter__()

    def __next__(self):
        res = self.parse(super().__next__())
        if res is not None:
            return res
        else:
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.csvfile.close()

    def to_list(self):
        return [row for row in self]

    def close(self):
        self.csvfile.close()
