# High DPI aware
import ctypes
import sys
if sys.platform == 'win32':
    ctypes.windll.shcore.SetProcessDpiAwareness(True)

import wx


background_color = wx.Colour(206, 219, 186)


# some size
w :tuple[int, int] = wx.DisplaySize()[0]



def size(p):
    return round(w*p)
def tsize(p):
    return (size(p), -1)


# keycode
# back, del, home, end, left,right
k_special: tuple[int, ...] = (8, 314, 316, 127, 313, 312)
k_number: tuple[int, ...] = tuple(range(48, 58))
k_decimal: tuple[int] = (46,)
k_hash: tuple[int] = (35,)
k_slash: tuple[int] = (47,)
k_tab: tuple[int] = (9,)


# mapmode
# wx.MM_TEXT: Each logical unit is 1 device pixel.
# wx.MM_METRIC: Each logical unit is 1 millimeter.
# wx.MM_LOMETRIC: Each logical unit is 1/10 of a millimeter.
# wx.MM_TWIPS: Each logical unit is 1/20 of a “printer point”, or 1/1440 of an inch (also known as “twip”).
# wx.MM_POINTS: Each logical unit is a “printer point” i.e. 1/72 of an inch.
if sys.platform == 'win32':
    print_mm = wx.MM_LOMETRIC
    preview_mm = wx.MM_LOMETRIC
    scale=0.8
else:
    print_mm = wx.MM_TEXT
    preview_mm = wx.MM_LOMETRIC
    scale=1