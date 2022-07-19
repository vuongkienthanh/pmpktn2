from .buttons import *
from .widgets import *
import sys
if sys.platform in ['linux', 'darwin']:
    from .linux_drug_picker import DrugPicker
elif sys.platform == 'win32':
    from .windows_drug_picker import DrugPicker