# High DPI aware
import ctypes
import sys
if sys.platform == 'win32':
    ctypes.windll.shcore.SetProcessDpiAwareness(True)

import wx


background_color = wx.Colour(206, 219, 186)


# some size
screen_w, screen_h = wx.DisplaySize()
window_size = (int(screen_w*0.75), int(screen_h*0.8))
popup_size = tuple(int(i) for i in (screen_w*0.4, screen_h/5, screen_h/5))

# keycode
# back, del, home, end, left,right
k_special = [8, 314, 316, 127, 313, 312]
k_number = list(range(48, 58))
k_decimal = [46]
k_hash = [35]
k_slash = [47]
k_tab = [9]
