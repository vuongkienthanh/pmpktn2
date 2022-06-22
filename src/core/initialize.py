# High DPI aware
import ctypes
import platform
if platform.system() == 'Windows':
    ctypes.windll.shcore.SetProcessDpiAwareness(True)  # type:ignore

import wx


background_color = wx.Colour(206, 219, 186)


# some size
screen_w, screen_h = wx.DisplaySize()
window_size = (int(screen_w*0.75), int(screen_h*0.8))
popup_size = tuple(int(i) for i in (screen_w*0.4, screen_h/5, screen_h/5))
