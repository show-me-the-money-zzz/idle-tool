import sys
import site
from datetime import datetime

DEVAPP = getattr(sys, 'frozen', False)

def PrintDEV(text):
    if False == DEVAPP:
        print(text)

def Print_LibPath():
    for path in site.getsitepackages():
        print("라이브러리 경로:", path)

def Calc_MS(fsec):
    return int(fsec * 1000)

def GetText_NotiDate():
    return datetime.now().strftime("%y-%m-%d %H:%M:%S")

def GetText_NoticeLog(bot, title):
    return f"📢 알림 ({bot}): [{title}] 알림을 전송했습니다."