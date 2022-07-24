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

plus_bm = os.path.join(BITMAPS_DIR, 'plus.png')
minus_bm = os.path.join(BITMAPS_DIR, 'minus.png')
weight_bm = os.path.join(BITMAPS_DIR, 'weight.png')
update_druglist_bm = os.path.join(BITMAPS_DIR, 'update_druglist.png')
