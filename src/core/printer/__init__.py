from .printdata import printdata
import sys
if sys.platform in ['linux', 'darwin']:
    from core.printer.linux import PrintOut
else:
    from core.printer.windows import PrintOut
