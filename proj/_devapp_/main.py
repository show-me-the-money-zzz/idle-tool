import tkinter as tk
import os
from ui.app_ui import AutomationAppUI
from core.ocr_engine import setup_tesseract
from core.settings_manager import SettingsManager
from zzz.config import DEFAULT_TESSERACT_PATH

def main():
    """메인 애플리케이션 실행"""
    # 스크립트 디렉토리 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 설정 관리자 초기화
    settings_manager = SettingsManager()
    
    # UI 초기화 및 실행
    root = tk.Tk()
    app = AutomationAppUI(root, settings_manager)
    root.mainloop()

if __name__ == "__main__":
    main()