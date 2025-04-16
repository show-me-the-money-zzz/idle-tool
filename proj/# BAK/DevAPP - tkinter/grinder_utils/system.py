import sys
import site

DEVAPP = getattr(sys, 'frozen', False)

def Print_LibPath():
    for path in site.getsitepackages():
        print("라이브러리 경로:", path)

def Calc_MS(fsec):
    return int(fsec * 1000)