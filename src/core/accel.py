from core.initialize import *
import wx


my_accel = wx.AcceleratorTable([
    wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_CONTROL_N, wx.ID_NEW),
    wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_CONTROL_O, wx.ID_OPEN),
    wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F5, wx.ID_REFRESH),
    wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_CONTROL_U, wx.ID_EDIT),

    wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_CONTROL_Q, wx.ID_EXIT),
])
