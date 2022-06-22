import os
from pathlib import Path

APP_DIR = os.path.join(Path.home(), ".pmpktn")
# create database in home directory
if not Path(APP_DIR).exists():
    os.mkdir(APP_DIR)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")


# database
MY_DATABASE_PATH = os.path.join(APP_DIR, "my_database.db")

# src dir
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# sample dir
SAMPLE_DIR = os.path.join(SRC_DIR, 'sample')
# db, sql dir
DB_DIR = os.path.join(SRC_DIR, 'db')


# bitmaps
BITMAPS_DIR = os.path.join(SRC_DIR, 'bitmaps')

new_p_bm = os.path.join(BITMAPS_DIR, 'new_patient.png')
del_p_bm = os.path.join(BITMAPS_DIR, 'delete_patient.png')
save_drug_bm = os.path.join(BITMAPS_DIR, 'save_drug.png')
erase_drug_bm = os.path.join(BITMAPS_DIR, 'erase_drug.png')
new_visit_bm = os.path.join(BITMAPS_DIR, 'new_visit.png')
save_visit_bm = os.path.join(BITMAPS_DIR, 'save_visit.png')
del_visit_bm = os.path.join(BITMAPS_DIR, 'del_visit.png')
print_bm = os.path.join(BITMAPS_DIR, 'print.png')
refresh_bm = os.path.join(BITMAPS_DIR, 'refresh.png')
plus_bm = os.path.join(BITMAPS_DIR, 'plus.png')
pencil_bm = os.path.join(BITMAPS_DIR, 'pencil.png')
minus_bm = os.path.join(BITMAPS_DIR, 'minus.png')
weight_bm = os.path.join(BITMAPS_DIR, 'weight.png')
