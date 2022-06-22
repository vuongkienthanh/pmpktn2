from test_path_init import *
from path_init import MY_DATABASE_PATH
import db.db_func as dbf
import unittest
import subprocess as sp
from os import remove, chdir
import shutil


@unittest.skip('For now')
class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        chdir(SRC_DIR)
        self.dst = str(MY_DATABASE_PATH) + '.temp'
        shutil.copyfile(MY_DATABASE_PATH, self.dst)

    def test_reset(self):
        sp.run(['python', 'main.py', '--reset'])
        con = dbf.Connection(MY_DATABASE_PATH)
        with con.sqlcon as con:
            rows = con.execute(
                "SELECT name FROM sqlite_master where type='table'").fetchall()
            self.assertEqual(len(rows), 5)
        con.close()

    def tearDown(self) -> None:
        shutil.copyfile(self.dst, MY_DATABASE_PATH)
        remove(self.dst)
