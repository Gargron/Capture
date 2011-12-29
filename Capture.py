import os, httplib, tempfile
import win32api, win32con
import win32clipboard as w
import pythoncom, pyHook
import Image, ImageGrab

startx, starty = 0, 0
endx, endy     = 0, 0

DOMAIN         = "cptr.zeonfederated.com"

main_thread_id = win32api.GetCurrentThreadId()

def OnStart(event):
    global startx, starty
    startx, starty = event.Position
    return False

def OnEnd(event):
    global endx, endy
    endx, endy     = event.Position

    OnFinish()
    return False

def OnFinish():
    global startx, starty, endx, endy, t

    tmpId, tmpPath = tempfile.mkstemp()

    if startx > endx:
        tempx  = endx
        endx   = startx
        startx = tempx
    if starty > endy:
        tempy  = endy
        endy   = starty
        starty = tempy

    im   = ImageGrab.grab((startx, starty, endx, endy))
    sIm  = os.fdopen(tmpId, "w+b")

    im.save(sIm, "PNG")

    sIm.seek(0)
    
    headers = {"Content-type": "application/octet-stream"}
    conn    = httplib.HTTPConnection(DOMAIN)
    
    conn.request("POST", "/", sIm.read(), headers)
    
    response = conn.getresponse()
    status   = response.read()

    if "YES" in status:
        url = status[4:-0]
        
        w.OpenClipboard()
        w.EmptyClipboard()
        w.SetClipboardData(w.CF_TEXT, url)
        w.CloseClipboard()
    
    conn.close()

    win32api.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0);

hm = pyHook.HookManager()

hm.MouseLeftDown = OnStart
hm.MouseLeftUp   = OnEnd

hm.HookMouse()

pythoncom.PumpMessages()