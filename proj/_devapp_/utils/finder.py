import sys
# from utils import system
from pathlib import Path

from zzz.config import PATH_Data

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
    return Get_LocalPth() / PATH_Data;