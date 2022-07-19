import db.db_func as dbf
from path_init import *
import os.path
from pathlib import Path
import shutil
import wx
import argparse
import os
import sys
import json
from typing import Any
import locale


class App(wx.App):
    def __init__(self, sample):
        super().__init__()

        config = self.get_config()
        locale.setlocale(locale.LC_TIME, "vi_VN.utf-8")
        from core.mainview import MainView
        if sample:
            # con = dbf.Connection('test.db')
            con = dbf.Connection(':memory:')
            con.make_db()
            con.make_sample()

        else:
            con = dbf.Connection(MY_DATABASE_PATH)
            con.make_db()
        mv = MainView(con, config, sample)
        self.SetTopWindow(mv)
        mv.Show()
        self.MainLoop()

    def get_config(self) -> dict[str, Any]:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                sys.exit("ERROR: Config file is not a dict")
        return config


def mainloop(sample=False):
    copy_config()
    platform_settings()
    App(sample)


def make_bak():
    bak = os.path.realpath(MY_DATABASE_PATH) + ".bak"
    if Path(MY_DATABASE_PATH).exists():
        os.rename(MY_DATABASE_PATH, bak)
        print(f"Back up database to: {bak}")
    else:
        print(f"{MY_DATABASE_PATH} not found")


def make_db():
    con = dbf.Connection(MY_DATABASE_PATH)
    con.make_db()
    con.close()
    print(f'New database created: {MY_DATABASE_PATH}')


def copy_config():
    if not Path(CONFIG_PATH).exists():
        shutil.copyfile(
            os.path.join(SRC_DIR, 'default_config.json'), CONFIG_PATH
        )
        print(f"Create new {CONFIG_PATH}")
    else:
        print(f"Found {CONFIG_PATH}")


def replace_config():
    shutil.copyfile(
        os.path.join(SRC_DIR, 'default_config.json'), CONFIG_PATH
    )
    print(f"Reset to default: {CONFIG_PATH}")


def platform_settings():
    if sys.platform == 'linux':
        # light theme
        os.environ['GTK_THEME'] = "Default " + os.path.join(SRC_DIR, "main.py")
        pass


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true",
                    help="Back up database and create a clean one")
    ap.add_argument("--reset-config", action="store_true",
                    help="Reset to default user config")
    ap.add_argument("--sample", action="store_true",
                    help="Run app with sample database")
    args = ap.parse_args()

    if args.reset:
        make_bak()
        make_db()
    elif args.reset_config:
        replace_config()
    elif args.sample:
        mainloop(sample=True)
    else:
        mainloop()
