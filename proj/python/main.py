import tkinter as tk
from ui.app_ui import AutomationAppUI
from core.ocr_engine import setup_tesseract

# Tesseract OCR 설정
setup_tesseract(r'..\..\Tesseract-OCR\tesseract.exe')
# Python에서 상대 경로는 파일 위치가 아니라 코드가 실행되는 현재 작업 디렉토리(current working directory)를 기준

def main():
    """메인 애플리케이션 실행"""
    root = tk.Tk()
    app = AutomationAppUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()