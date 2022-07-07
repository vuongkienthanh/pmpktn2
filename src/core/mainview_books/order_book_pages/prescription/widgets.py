import core.other_func as otf
from path_init import plus_bm, minus_bm
import wx


class Times(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent,)
        self.SetHint('lần')
        self.Bind(wx.EVT_CHAR, otf.only_nums)
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.Parent.check_wh_do_ti_filled():
            self.Parent.quantity.set()
            self.Parent.note.set()


class Dose(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetHint('liều')
        self.Bind(
            wx.EVT_CHAR,
            lambda e: otf.only_nums(e, decimal=True, slash=True)
        )
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.Parent.check_wh_do_ti_filled():
            self.Parent.quantity.set()
            self.Parent.note.set()


class Quantity(wx.TextCtrl):

    def __init__(self, parent):
        super().__init__(parent)
        self.SetHint('Enter')
        self.Bind(wx.EVT_CHAR, self.onKey)

    def onKey(self, e):
        x = e.KeyCode
        if x in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and self.Value.strip() != '':
            self.Parent.save_drug_btn.onClick(None)
        else:
            otf.only_nums(e)

    def set(self):
        mv = self.Parent.Parent.Parent
        times = int(self.Parent.times.GetValue())
        dose = self.Parent.dose.GetValue()
        days = mv.days.GetValue()
        wh = mv.state.warehouse
        res = otf.calc_quantity(times, dose, days, wh.sale_unit,
                                self.Parent.Parent.Parent.config['thuoc_ban_mot_don_vi'])
        if res is not None:
            self.SetValue(str(res))
        else:
            self.SetValue('')


class Note(wx.TextCtrl):
    def __init__(self, parent):
        super().__init__(parent)

    def set(self):
        self.ChangeValue(otf.get_note_str(
            usage=self.Parent.Parent.Parent.state.warehouse.usage,
            times=self.Parent.times.GetValue(),
            dose=self.Parent.dose.GetValue(),
            usage_unit=self.Parent.Parent.Parent.state.warehouse.usage_unit
        ))

    def GetValue(self):
        s = super().GetValue().strip()
        pg = self.Parent
        wh = self.Parent.Parent.Parent.state.warehouse
        if s == otf.get_note_str(
                usage=wh.usage,
                times=pg.times.Value,
                dose=pg.dose.Value,
                usage_unit=wh.usage_unit):
            return None
        elif s == '':
            return None
        else:
            return s

    def SetValue(self, s):
        if s == '' or s is None:
            pg = self.Parent
            wh = self.Parent.Parent.Parent.state.warehouse
            s = otf.get_note_str(
                usage=wh.usage,
                times=pg.times.Value,
                dose=pg.dose.Value,
                usage_unit=wh.usage_unit)
        super().SetValue(s)


class SaveDrugButton(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent,
                         bitmap=wx.Bitmap(plus_bm))
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        if self.Parent.check_all_filled():
            self.Parent.drug_list.upsert()
            self.Parent.Parent.Parent.state.warehouse = None
            self.Parent.Parent.Parent.price.set_price()


class DelDrugButton(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent,
                         bitmap=wx.Bitmap(minus_bm))
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        self.Parent.drug_list.remove()
        self.Parent.Parent.Parent.state.warehouse = None
        self.Parent.Parent.Parent.price.set_price()


class ReuseDrugListButton(wx.Button):
    def __init__(self, parent):
        super().__init__(parent,
                         label='Lượt khám mới với toa cũ này')
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        mv = self.Parent.Parent.Parent
        lld = self.Parent.drug_list._list.copy()
        weight = mv.weight.GetValue()
        mv.state.visit = None
        mv.weight.SetValue(weight)
        self.Parent.drug_list.rebuild(lld)
        self.Parent.Parent.Parent.updatequantitybtn.onClick(None)
