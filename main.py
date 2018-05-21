import wx
import wx.adv
import os
import sys
import ctypes
from PIL import Image
import urllib.request
import time, threading
import validators

TRAY_TOOLTIP = 'Wallpaper Refresher'
TRAY_ICON = 'icon.ico'

url = 'https://volcanoes.usgs.gov/observatories/hvo/cams/KIcam/images/M.jpg'
width = 5960
height = 1080
refresh_rate = 1 #in minutes

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item

def refresh_image():
    try:
        urllib.request.urlretrieve(url, resource_path("M.jpg"))
        imageFile = resource_path("M.jpg")
        im1 = Image.open(imageFile)
        im1 = im1.resize((width, height), Image.NEAREST) 
        im1.save(imageFile)
    except:
        imageFile = resource_path("N.jpg")
    ctypes.windll.user32.SystemParametersInfoW(20, 0,imageFile,0)

def refresh_cycle():
    refresh_image()
    t = threading.Timer(60*refresh_rate,refresh_cycle)
    t.start()
    return t

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def settings():
    se = Settings()
    se.ShowModal()
    
class Settings(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, title='Settings')

        self.panel = wx.Panel(self, wx.ID_ANY)

        self.labelOne = wx.StaticText(self.panel, wx.ID_ANY, 'URL:')
        self.inputTxtOne = wx.TextCtrl(self.panel, wx.ID_ANY, url)

        self.labelTwo = wx.StaticText(self.panel, wx.ID_ANY, 'Width:')
        self.inputTxtTwo = wx.TextCtrl(self.panel, wx.ID_ANY, str(width))

        self.labelThree = wx.StaticText(self.panel, wx.ID_ANY, 'Height')
        self.inputTxtThree = wx.TextCtrl(self.panel, wx.ID_ANY, str(height))

        self.labelFour = wx.StaticText(self.panel, wx.ID_ANY, 'Refresh(minutes):')
        self.inputTxtFour = wx.TextCtrl(self.panel, wx.ID_ANY, str(refresh_rate))

        okBtn = wx.Button(self.panel, wx.ID_ANY, 'OK')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.onOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)

        topSizer        = wx.BoxSizer(wx.VERTICAL)
        inputOneSizer   = wx.BoxSizer(wx.HORIZONTAL)
        inputTwoSizer   = wx.BoxSizer(wx.HORIZONTAL)
        #inputThreeSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputFourSizer  = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)


        inputOneSizer.Add(self.labelOne, 0, wx.ALL, 5)
        inputOneSizer.Add(self.inputTxtOne, 1, wx.ALL|wx.EXPAND, 5)

        inputTwoSizer.Add(self.labelTwo, 0, wx.ALL, 5)
        inputTwoSizer.Add(self.inputTxtTwo, 1, wx.ALL|wx.EXPAND, 5)

        inputTwoSizer.Add(self.labelThree, 0, wx.ALL, 5)
        inputTwoSizer.Add(self.inputTxtThree, 1, wx.ALL|wx.EXPAND, 5)

        inputFourSizer.Add(self.labelFour, 0, wx.ALL, 5)
        inputFourSizer.Add(self.inputTxtFour, 1, wx.ALL|wx.EXPAND, 5)

        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)

        topSizer.Add(inputOneSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(inputTwoSizer, 0, wx.ALL|wx.EXPAND, 5)
        #topSizer.Add(inputThreeSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(inputFourSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)
        self.CentreOnParent(wx.BOTH)


    def onOK(self, event):
        global url
        global width
        global height
        global refresh_rate
        global timer
        u = self.inputTxtOne.GetValue()
        if validators.url(u):
            url = u
        else:
            url = 'https://volcanoes.usgs.gov/observatories/hvo/cams/KIcam/images/M.jpg'
        w = int(self.inputTxtTwo.GetValue())
        if w > 0:
            width = w
        else:
            width = 1920
        h = int(self.inputTxtThree.GetValue())
        if h > 0:
            height = h
        else:
            height = 1080
        r = int(self.inputTxtFour.GetValue())
        if r > 0:
            refresh_rate = r
        else:
            refresh_rate = 1
        timer.cancel()
        timer = refresh_cycle()
        self.closeProgram()

    def onCancel(self, event):
        self.closeProgram()

    def closeProgram(self):
        self.Destroy()

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super(TaskBarIcon, self).__init__()
        self.set_icon(resource_path(TRAY_ICON))
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Refresh', self.on_refresh)
        create_menu_item(menu, 'Settings', self.on_settings)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        self.icon = wx.Icon(path)
        self.SetIcon(self.icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        settings()

    def on_settings(self, event):
        settings()

    def on_refresh(self, event):
        refresh_image()

    def on_exit(self, event):
        global timer
        timer.cancel()
        self.icon.Visible = False
        wx.CallAfter(self.Destroy)
        self.Destroy()
        sys.exit()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None, -1)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    app = App(False)
    app.MainLoop()

if __name__ == '__main__':
    global timer
    timer = refresh_cycle()
    main()
