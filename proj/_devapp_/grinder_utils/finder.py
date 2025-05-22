import sys
# from grinder_utils import system
from pathlib import Path

from core.config import PATH_Data, PATH_FLOWCHART, PATH_TOOL

def Get_LocalPth():
    # 애플리케이션 실행 파일 기준 경로 설정
    
    # PyInstaller로 빌드된 경우
    if getattr(sys, 'frozen', False):
    # if False == system.DEVAPP: #utils.system.
        return Path(sys.executable).parent
    else:
        # 개발 환경인 경우
        return Path(__file__).parent.parent
    
def Get_DataPath():
    return Get_LocalPth() / PATH_Data

def GetPath_Flowchart(): return Get_LocalPth() / PATH_FLOWCHART

def GetPath_Tools(): return Get_LocalPth() / PATH_TOOL
# def GetPath_Tools_luajit(): return GetPath_Tools() / "luajit.exe"
def GetPath_Tools_luajit(): return GetPath_Tools() / "lua5.1.exe"