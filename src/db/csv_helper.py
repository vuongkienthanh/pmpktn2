from db.db_class import *
import csv


class CSVReader(csv.DictReader):
    def __init__(self, t, csvfilepath):
        self.t = t
        self.csvfile = open(csvfilepath, 'r')
        super().__init__(self.csvfile)

    def get_type(self):
        return self.t

    def parse(self, row):
        return self.t.parse(row)

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
