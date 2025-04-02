import tkinter as tk
import os
from ui.app_ui import AutomationAppUI
from core.ocr_engine import setup_tesseract
from config import TESSERACT_PATH

def main():
    """메인 애플리케이션 실행"""
    # Tesseract OCR 설정
    # 상대 경로를 절대 경로로 변환하여 사용
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tesseract_path = os.path.normpath(os.path.join(script_dir, TESSERACT_PATH))
    
    # OCR 엔진 초기화
    setup_tesseract(tesseract_path)
    
    # UI 초기화 및 실행
    root = tk.Tk()
    app = AutomationAppUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()