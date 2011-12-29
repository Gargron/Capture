import os, sys, httplib, tempfile
import win32api, win32con
import win32clipboard, webbrowser
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
    global startx, starty, endx, endy

    tmpId, tmpPath = tempfile.mkstemp()

    if startx > endx:
        tempx  = endx
        endx   = startx
        startx = tempx
    if starty > endy:
        tempy  = endy
        endy   = starty
        starty = tempy

    if (endx - startx) is 0 or (endy - starty) is 0:
        Close()

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
        url = status[5:]
    else:
        print "Error, welp"
    
    conn.close()
    Close(url)

def toClipboard(string):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(string)
    win32clipboard.CloseClipboard()

def OnCancel(event):
    Close()
    return False

def Close(url = None):
    win32api.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0)
    if url is not None:
        toClipboard(url)
        webbrowser.open_new_tab(url)
    sys.exit(0)

hm = pyHook.HookManager()

hm.MouseLeftDown  = OnStart
hm.MouseLeftUp    = OnEnd
hm.MouseRightDown = OnCancel

hm.HookMouse()

pythoncom.PumpMessages()
