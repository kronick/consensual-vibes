import serial
import random

#ser = serial.Serial("/dev/ttyATH0", 19200, timeout=1)

_bold_mode = False
_double_high_mode = False
_double_wide_mode = False
_delete_line_mode = False
_underline_mode = False

def _updatePrintMode():
    '''Send command to select correct print mode by combining state vars set with other functions'''
    n = (_bold_mode << 3) + (_double_high_mode << 4) + (_double_wide_mode << 5) + \
        (_delete_line_mode << 6) + (_underline_mode << 7)
    #ser.write(bytearray([27, 33, n]))


def init():
    #ser.write(bytearray([27, 64]))
    setHeat(128, 2, 4)

def printTest():
    pass
    #ser.write(bytearray([18,84]))

def feed(n=1):
    pass
    #ser.write(bytearray([27,100,n]))


def println(string):
    pass
    #ser.write(bytearray(string + "\n"))

def write(string):
    pass
    #ser.write(bytearray(string))

def printMatch(a, b):
    try:
      a = a.encode("ascii")
      b = b.encode("ascii")
    except:
        return

    setLinespacing(5)
    setAlign("center")
    setInverted(False)
    println("IT'S A MATCH")
    println("--------------------------------")
    setInverted(True)
    println(" " + a + " ")
    setInverted(False)
    println(" + ")
    setBold(True)
    println(b)
    setBold(False)
    println("--------------------------------")
    setAlign("center")
    setLinespacing(30)
    feed(3)


def setUpsidedown(v):
    pass
    #ser.write(bytearray([27, 123, 1 if v else 0]))

def setInverted(v):
    pass
    #ser.write(bytearray([29, 66, 1 if v else 0]))

def setDoublewide(v):
    global _double_wide_mode
    _double_wide_mode = v
    _updatePrintMode()

def setDoublehigh(v):
    global _double_high_mode
    _double_high_mode = v
    _updatePrintMode()

def setBold(v):
    pass
    #global _bold_mode
    #_bold_mode = v
    #_updatePrintMode()
    #ser.write(bytearray([27, 69, v]))

def setDeleteline(v):
    global _delete_line_mode
    _delete_line_mode = v
    _updatePrintMode()

def setUnderline(v, thickness=1):
    if thickness > 2:
        thickness = 2
    #ser.write(bytearray([27,45,thickness]))
    global _underline_mode
    _underline_mode = v
    _updatePrintMode()

def setLinespacing(spacing=30):
    pass
    #ser.write(bytearray([27, 51, spacing]))

def setAlign(align):
    v = 0
    if align.lower() == "right":
        v = 2
    elif align.lower() == "middle" or align.lower() == "center":
        v = 1
    
    #ser.write(bytearray([27,97,v]))

def setHeat(time=80, interval=2, density=7):
    if time < 3:
        time = 3
    if time > 255:
        time = 255
    if interval > 255:
        interval = 255
    if density > 255:
        density = 255

    #ser.write(bytearray([27,55,density,time,interval]))

def setDensity(n):
    if n > 50:
        n = 50
    #ser.write(bytearray([18,35,n]))

def printSavedImage():
    pass
    #ser.write(bytearray([29,47,0]))

def printNoise(height=10):
    for r in range(height):
        pass
        #ser.write(bytearray([18, 86,16,0]))
        for i in range(0, 16*48):
            pass
            #ser.write(bytearray([random.randint(0,255)]))

def printHeader():
    setLinespacing(30)
    feed(2)
    printNoise(1)
    feed(1)
    printNoise(1)
    feed(1)
    printNoise(1)
    feed(2)
    setAlign("center")
    println("disk cactus")
    setInverted(True)
    setDoublehigh(True)
    setDoublewide(True)
    println(" CONSENSUAL ")
    println(" VIBES ")
    setDoublehigh(False)
    setDoublewide(False)
    feed(4)
    

if __name__ == "__main__":
    init()
    setHeat(128, 2, 4)
    #setHeat(128)
    setUpsidedown(False)
    feed(2)
    printNoise(1)
    feed(1)
    printNoise(1)
    feed(1)
    printNoise(1)
    feed(2)
    setLinespacing(30)
    setAlign("center")
    println("disk cactus")
    setInverted(True)
    setDoublehigh(True)
    setDoublewide(True)
    println(" CONSENSUAL ")
    println(" VIBES ")
    setDoublehigh(False)
    setDoublewide(False)
    
    feed(1)
    setAlign("center")
    printMatch("disk", "cactus")
    printMatch("simple environments", "string")
    printMatch("wifi", "stories")
    printMatch("VR zones", "soil")
    printMatch("antenna", "pendant")
    printMatch("do-it-yourself soil", "deployable gradient")
    printMatch("hammocks", "desert")
    printMatch("api", "flags")
    printMatch("overwhelming balloons", "zone")


    feed(3)
