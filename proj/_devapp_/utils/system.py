import sys
DEVAPP = getattr(sys, 'frozen', False)

def Calc_MS(fsec):
    return int(fsec * 1000)