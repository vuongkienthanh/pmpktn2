from core import mainview as mv
import wx
from itertools import cycle


class DaysCtrl(wx.SpinCtrl):
    """ Changing DaysCtrl Value also changes RecheckCtrl Value """

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(
            parent,
            style=wx.SP_ARROW_KEYS,
            initial=parent.config["so_ngay_toa_ve_mac_dinh"],
            **kwargs
        )
        self.mv = parent
        self.SetRange(0, 100)
        self.Disable()
        self.Bind(wx.EVT_SPINCTRL, self.onSpin)

    def onSpin(self, e: wx.SpinEvent):
        self.mv.recheck.SetValue(e.GetPosition())
        self.mv.updatequantitybtn.Enable()


class RecheckCtrl(wx.SpinCtrl):
    """Independant of DaysCtrl"""

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"], **kwargs)
        self.SetRange(0, 100)
        self.Disable()


class PriceCtrl(wx.TextCtrl):
    """A TextCtrl with proper Vietnamese currency format with default set according to config"""

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, **kwargs)
        self.mv = parent
        self.clear()

    def FetchPrice(self):
        """Display new price"""
        price: int = self.mv.config['cong_kham_benh']
        price += sum(
            item['sale_price'] * item['quantity']
            for item in self.mv.order_book.page0.drug_list._list
        )
        self.ChangeValue(self.num_to_str(price))

    def num_to_str(self, price: int) -> str:
        """Return proper currency format str from int"""
        s = str(price)
        res = ''
        for char, cyc in zip(s[::-1], cycle(range(3))):
            res += char
            if cyc == 2:
                res += '.'
        else:
            if res[-1] == '.':
                res = res[:-1]
        return res[::-1]

    def clear(self):
        self.ChangeValue(self.num_to_str(self.mv.config['cong_kham_benh']))


class Follow(wx.ComboBox):
    """A Combobox which is able to return None if conditions met"""

    def __init__(self, parent: wx.Window, choice_dict: dict[str, str], **kwargs):
        super().__init__(
            parent,
            style=wx.CB_DROPDOWN,
            choices=[f"{i}: {j[:100]}..." for i, j in choice_dict.items()],
            **kwargs
        )
        self.choice_dict = choice_dict
        self.SetSelection(0)

    def SetFollow(self, val: str | None):
        if val is None:
            self.SetValue('')
        elif val in self.choice_dict.keys():
            self.SetValue(f"{val}: {self.choice_dict[val]}")
        else:
            self.SetValue(val)

    def GetFollow(self) -> str | None:
        val: str = self.GetValue().strip()
        k, v = tuple(val.split(":", 1))
        if val == '':
            return None
        elif (k, v) in self.choice_dict.items():
            return k
        else:
            return val
