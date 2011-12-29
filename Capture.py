import os, sys, httplib, tempfile, string, random
import win32api, win32con
import win32clipboard, webbrowser, yaml
import pythoncom, pyHook
import Image, ImageGrab

startx, starty = 0, 0
endx, endy     = 0, 0

DOMAIN         = "cptr.zeonfederated.com"
PATH           = os.path.abspath("./") + "\\"
CONF           = yaml.load(open(PATH + 'config.yaml', 'r'))

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
        Close()

    im   = ImageGrab.grab((startx, starty, endx, endy))
    sIm  = os.fdopen(tmpId, "w+b")

    im.save(sIm, "PNG")

    sIm.seek(0)

    if CONF['local_only'] is True:
        new_filename = toRandomFilename()
        im.save(new_filename, "PNG")
        Close(new_filename)
    else:
        headers = {"Content-type": "application/octet-stream"}
        conn    = httplib.HTTPConnection(DOMAIN)
        
        conn.request("POST", "/", sIm.read(), headers)
        
        response = conn.getresponse()
        status   = response.read()

        if "YES" in status:
            url = status[5:]
        else:
            win32api.MessageBox(0, 'Error while uploading, welp', 'Capture: Error', win32con.MB_OK | win32con.MB_ICONERROR)

        conn.close()
        Close(url)

def toClipboard(string):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(string)
    win32clipboard.CloseClipboard()

def toRandom(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def toRandomFilename():
    name = PATH + toRandom() + ".png"

    try:
        open(name)
    except IOError as e:
        return name
    
    toRandomFilename()

def OnCancel(event):
    Close()
    return False

def Close(url = None):
    print url
    win32api.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0)
    if url is not None:
        if CONF['copy_link'] is True:
            toClipboard(url)
        if CONF['open_browser'] is True:
            webbrowser.open_new_tab(url)
    sys.exit(0)

hm = pyHook.HookManager()

hm.MouseLeftDown  = OnStart
hm.MouseLeftUp    = OnEnd
hm.MouseRightDown = OnCancel

hm.HookMouse()

pythoncom.PumpMessages()
