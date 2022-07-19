# High DPI aware
import ctypes
import sys
if sys.platform == 'win32':
    ctypes.windll.shcore.SetProcessDpiAwareness(True)

import wx


background_color = wx.Colour(206, 219, 186)


# some size
window_size :tuple[int, int] = wx.DisplaySize()
screen_w, screen_h = window_size
left = round(screen_w *0.2)
right = round(screen_w *0.6)
popup_size = tuple(int(i) for i in (screen_w*0.4, screen_h/5, screen_h/5))

# keycode
# back, del, home, end, left,right
k_special: tuple[int, ...] = (8, 314, 316, 127, 313, 312)
k_number: tuple[int, ...] = tuple(range(48, 58))
k_decimal: tuple[int] = (46,)
k_hash: tuple[int] = (35,)
k_slash: tuple[int] = (47,)
k_tab: tuple[int] = (9,)
