import tkinter as tk
from tkinter import ttk
import sys
import os

# 모듈 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from zzz.app_ui import AppUI
from core.settings_manager import SettingsManager
from zzz.config import *

def main():
    """메인 함수"""
    # 설정 관리자 생성
    settings_manager = SettingsManager()
    
    # 기본 tkinter 윈도우 생성
    root = tk.Tk()
    
    # 테마 설정 - Windows 테마
    try:
        style = ttk.Style()
        
        style.theme_use(APP_THEME)  # Windows 10 테마
        # print(style.theme_names())  # 사용 가능한 모든 테마 이름 출력
    except:
        pass  # 테마 적용 실패 시 기본값 사용
    
    # 메인 애플리케이션 UI 생성
    app = AppUI(root, settings_manager)
    
    # 메인 이벤트 루프 실행
    root.mainloop()

if __name__ == "__main__":
    main()