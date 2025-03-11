import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import pyautogui
import pytesseract
from PIL import ImageGrab
import cv2
import numpy as np

# Tesseract OCR 경로 설정 (Windows 기준)
pytesseract.pytesseract.tesseract_cmd = r'D:\libs\Tesseract-OCR\tesseract.exe'

class AutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("화면 캡처 및 자동화 도구")
        self.root.geometry("500x550")
        self.root.resizable(True, True)
        
        self.capture_thread = None
        self.is_capturing = False
        self.capture_interval = 1.0  # 기본 1초 간격
        
        self.setup_ui()
    
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 영역 설정 프레임
        area_frame = ttk.LabelFrame(main_frame, text="캡처 영역 설정", padding="10")
        area_frame.pack(fill=tk.X, pady=5)
        
        # X 좌표
        ttk.Label(area_frame, text="X 좌표:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_var = tk.StringVar(value="0")
        ttk.Entry(area_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Y 좌표
        ttk.Label(area_frame, text="Y 좌표:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.y_var = tk.StringVar(value="0")
        ttk.Entry(area_frame, textvariable=self.y_var, width=10).grid(row=0, column=3, sticky=tk.W, pady=2)
        
        # 너비
        ttk.Label(area_frame, text="너비:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.StringVar(value="300")
        ttk.Entry(area_frame, textvariable=self.width_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 높이
        ttk.Label(area_frame, text="높이:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.height_var = tk.StringVar(value="100")
        ttk.Entry(area_frame, textvariable=self.height_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=2)
        
        # 캡처 간격 설정
        ttk.Label(area_frame, text="캡처 간격(초):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar(value="1.0")
        ttk.Entry(area_frame, textvariable=self.interval_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 캡처 시작/중지 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.capture_btn = ttk.Button(btn_frame, text="캡처 시작", command=self.toggle_capture)
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        # 텍스트 결과 영역
        result_frame = ttk.LabelFrame(main_frame, text="인식된 텍스트", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 자동화 버튼 프레임
        automation_frame = ttk.LabelFrame(main_frame, text="자동화 제어", padding="10")
        automation_frame.pack(fill=tk.X, pady=5)
        
        # M 키 입력 버튼
        self.key_btn = ttk.Button(automation_frame, text="'M' 키 입력", command=self.press_m_key)
        self.key_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # 마우스 클릭 버튼
        self.click_btn = ttk.Button(automation_frame, text="마우스 클릭", command=self.mouse_click)
        self.click_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # 마우스 좌표 입력 필드
        ttk.Label(automation_frame, text="클릭 X:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.click_x_var = tk.StringVar(value="0")
        ttk.Entry(automation_frame, textvariable=self.click_x_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(automation_frame, text="클릭 Y:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.click_y_var = tk.StringVar(value="0")
        ttk.Entry(automation_frame, textvariable=self.click_y_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 현재 마우스 위치 표시 레이블
        self.mouse_pos_label = ttk.Label(automation_frame, text="현재 마우스 위치: X=0, Y=0")
        self.mouse_pos_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 마우스 위치 추적 시작
        self.track_mouse_position()
        
        # 상태 표시 바
        self.status_var = tk.StringVar(value="준비 완료")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def track_mouse_position(self):
        """현재 마우스 위치를 실시간으로 업데이트"""
        x, y = pyautogui.position()
        self.mouse_pos_label.config(text=f"현재 마우스 위치: X={x}, Y={y}")
        self.root.after(100, self.track_mouse_position)  # 100ms마다 업데이트
    
    def toggle_capture(self):
        """캡처 시작/중지 전환"""
        if self.is_capturing:
            self.is_capturing = False
            self.capture_btn.config(text="캡처 시작")
            self.status_var.set("캡처 중지됨")
        else:
            try:
                # 입력값 검증
                x = int(self.x_var.get())
                y = int(self.y_var.get())
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                interval = float(self.interval_var.get())
                
                if width <= 0 or height <= 0 or interval <= 0:
                    raise ValueError("너비, 높이, 간격은 양수여야 합니다.")
                
                self.capture_interval = interval
                self.is_capturing = True
                self.capture_btn.config(text="캡처 중지")
                self.status_var.set("캡처 중...")
                
                # 새 스레드에서 캡처 실행
                self.capture_thread = threading.Thread(target=self.capture_text, daemon=True)
                self.capture_thread.start()
                
            except ValueError as e:
                messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
    
    def capture_text(self):
        """지정된 영역의 텍스트를 캡처하고 OCR로 인식"""
        while self.is_capturing:
            try:
                # 영역 좌표 획득
                x = int(self.x_var.get())
                y = int(self.y_var.get())
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                
                # 화면 캡처
                screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
                
                # 이미지 전처리 (옵션)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                
                # OCR 실행
                text = pytesseract.image_to_string(img, lang='kor+eng')
                
                # 결과 표시 (메인 스레드에서 UI 업데이트)
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                self.root.after(0, self.update_result, f"[{timestamp}] 인식 결과:\n{text}\n{'='*50}\n")
                
            except Exception as e:
                self.root.after(0, self.update_status, f"오류 발생: {str(e)}")
            
            # 지정된 간격만큼 대기
            time.sleep(self.capture_interval)
    
    def update_result(self, text):
        """텍스트 결과 영역 업데이트"""
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)  # 스크롤을 최신 내용으로 이동
    
    def update_status(self, text):
        """상태 표시줄 업데이트"""
        self.status_var.set(text)
    
    def press_m_key(self):
        """M 키 입력 함수"""
        try:
            pyautogui.press('m')
            self.status_var.set("'M' 키가 입력되었습니다.")
        except Exception as e:
            messagebox.showerror("키 입력 오류", f"키 입력 중 오류가 발생했습니다: {str(e)}")
    
    def mouse_click(self):
        """지정된 위치에서 마우스 클릭 함수"""
        try:
            # 클릭 좌표가 입력되어 있으면 해당 위치 사용, 아니면 현재 마우스 위치 사용
            if self.click_x_var.get() and self.click_y_var.get():
                x = int(self.click_x_var.get())
                y = int(self.click_y_var.get())
            else:
                x, y = pyautogui.position()
            
            pyautogui.click(x, y)
            self.status_var.set(f"마우스 클릭 완료 (X={x}, Y={y})")
        except Exception as e:
            messagebox.showerror("마우스 클릭 오류", f"마우스 클릭 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    # 메인 앱 실행
    root = tk.Tk()
    app = AutomationApp(root)
    root.mainloop()