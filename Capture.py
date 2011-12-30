import os, sys, httplib, tempfile, string, random, struct
import win32api, win32con, win32gui
import win32clipboard, webbrowser, yaml
import Image, ImageGrab

startx, starty = 0, 0
endx, endy     = 0, 0

scr_x, scr_y   = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN), win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
scr_w, scr_h   = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN), win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)

PATH           = os.path.abspath("./") + "\\"
CONF           = yaml.load(open(PATH + 'config.yaml', 'r'))
DOMAIN         = CONF['domain']
KEY            = CONF['key']

class MainWindow:
    def __init__(self):
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
    def CreateWindow(self):
        className = self.RegisterClass()
        self.BuildWindow(className)
    def RegisterClass(self):
        className = "Cptr"
        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
            win32con.WM_LBUTTONDOWN: self.OnStart,
            win32con.WM_LBUTTONUP: self.OnEnd,
            win32con.WM_RBUTTONUP: self.OnCancel,
        }
        wc = win32gui.WNDCLASS()
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = message_map
        wc.cbWndExtra = 0
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_CROSS)
        wc.hbrBackground = 0
        wc.hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        wc.lpszClassName = className
        wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
        classAtom = win32gui.RegisterClass(wc)
        return className
    def BuildWindow(self, className):
        style = win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_TOPMOST | win32con.WS_EX_NOACTIVATE
        self.hwnd = win32gui.CreateWindowEx(style,
                                            className,
                                            "Capture",
                                            win32con.WS_POPUP,
                                            scr_x,
                                            scr_y,
                                            scr_w,
                                            scr_h,
                                            0,
                                            0,
                                            self.hinst,
                                            None)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
    def OnDestroy(self, hwnd, message, wparam, lparam):
        win32gui.PostQuitMessage(0)
        return True
    def OnStart(self, hwnd, message, wparam, lparam):
        global startx, starty
        startx, starty = win32gui.GetCursorPos()
        return True
    def OnEnd(self, hwnd, message, wparam, lparam):
        global endx, endy
        endx, endy = win32gui.GetCursorPos()
        url = Finish()
        if CONF['copy_link']:
            set_clipboard(url)
        if CONF['open_browser']:
            webbrowser.open_new_tab(url)
        self.CloseWindow()
        return True
    def OnCancel(self, hwnd, message, wparam, lparam):
        self.CloseWindow()
        return True
    def CloseWindow(self):
        win32gui.DestroyWindow(self.hwnd)

def Finish():
    global startx, starty, endx, endy

    tmpId, tmpPath = tempfile.mkstemp()
    url            = None

    if startx > endx:
        tempx  = endx
        endx   = startx
        startx = tempx
    if starty > endy:
        tempy  = endy
        endy   = starty
        starty = tempy

    if (endx - startx) is 0 or (endy - starty) is 0:
        return False

    im   = ImageGrab.grab((startx, starty, endx, endy))
    sIm  = os.fdopen(tmpId, "w+b")

    im.save(sIm, "PNG")

    sIm.seek(0)

    if CONF['local_only'] is True:
        new_filename = get_random_filename()
        im.save(new_filename, "PNG")
        return new_filename
    else:
        headers = {"Content-type": "application/octet-stream"}
        conn    = httplib.HTTPConnection(DOMAIN)
        
        conn.request("POST", "/?key=" + KEY, sIm.read(), headers)
        
        response = conn.getresponse()
        status   = response.read()

        conn.close()

        if "YES" in status:
            url = status[5:]
        else:
            win32api.MessageBox(w.hwnd, 'Error while uploading, welp', 'Capture: Error', win32con.MB_OK | win32con.MB_ICONERROR)
            return False

        return url

def set_clipboard(string):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(string)
    win32clipboard.CloseClipboard()

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def get_random_filename():
    if not os.path.exists(PATH + "i"):
        os.mkdir(PATH + "i")
        
    name = PATH + "i\\" + toRandom() + ".png"

    try:
        open(name)
    except IOError as e:
        return name
    
    get_random_filename()

w = MainWindow()
w.CreateWindow()

win32gui.PumpMessages()
