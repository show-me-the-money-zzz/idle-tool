import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import pyautogui
import pytesseract
from PIL import ImageGrab
import cv2
import numpy as np
import win32gui
import win32process
import win32con
import psutil

# Tesseract OCR 경로 설정 (Windows 기준)
pytesseract.pytesseract.tesseract_cmd = r'D:\libs\Tesseract-OCR\tesseract.exe'

class AutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PID 기반 화면 캡처 및 자동화 도구")
        self.root.geometry("550x600")
        self.root.resizable(True, True)
        
        self.capture_thread = None
        self.is_capturing = False
        self.capture_interval = 1.0  # 기본 1초 간격
        self.target_hwnd = None
        self.window_rect = (0, 0, 0, 0)  # (left, top, right, bottom)
        
        self.setup_ui()
    
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # PID 입력 프레임
        pid_frame = ttk.LabelFrame(main_frame, text="대상 프로그램 설정", padding="10")
        pid_frame.pack(fill=tk.X, pady=5)
        
        # PID 입력
        ttk.Label(pid_frame, text="프로세스 ID (PID):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pid_var = tk.StringVar()
        ttk.Entry(pid_frame, textvariable=self.pid_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # PID 연결 버튼
        self.connect_btn = ttk.Button(pid_frame, text="연결", command=self.connect_to_pid)
        self.connect_btn.grid(row=0, column=2, padx=5, pady=2)
        
        # 연결된 윈도우 정보
        self.window_info_var = tk.StringVar(value="연결된 창 없음")
        ttk.Label(pid_frame, textvariable=self.window_info_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # 영역 설정 프레임
        area_frame = ttk.LabelFrame(main_frame, text="캡처 영역 설정 (창 내부 좌표)", padding="10")
        area_frame.pack(fill=tk.X, pady=5)
        
        # X 좌표 (상대적)
        ttk.Label(area_frame, text="X 좌표:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_var = tk.StringVar(value="0")
        ttk.Entry(area_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Y 좌표 (상대적)
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
        
        # 마우스 좌표 입력 필드 (상대적)
        ttk.Label(automation_frame, text="클릭 X (창 내부):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.click_x_var = tk.StringVar(value="0")
        ttk.Entry(automation_frame, textvariable=self.click_x_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(automation_frame, text="클릭 Y (창 내부):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.click_y_var = tk.StringVar(value="0")
        ttk.Entry(automation_frame, textvariable=self.click_y_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 현재 마우스 위치 표시 레이블 (절대 좌표와 상대 좌표)
        self.mouse_pos_label = ttk.Label(automation_frame, text="마우스 위치: 절대(X=0, Y=0) / 상대(X=0, Y=0)")
        self.mouse_pos_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 마우스 위치 추적 시작
        self.track_mouse_position()
        
        # 상태 표시 바
        self.status_var = tk.StringVar(value="준비 완료")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def connect_to_pid(self):
        """입력된 PID를 가진 프로세스의 메인 윈도우를 찾습니다"""
        try:
            pid = int(self.pid_var.get())
            if not pid:
                raise ValueError("PID가 입력되지 않았습니다.")
            
            # PID가 유효한지 확인
            process = psutil.Process(pid)
            
            # 해당 프로세스의 창 찾기
            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid:
                        text = win32gui.GetWindowText(hwnd)
                        if text:  # 타이틀이 있는 창만 처리
                            hwnds.append((hwnd, text))
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if not windows:
                messagebox.showerror("오류", f"PID {pid}에 해당하는 창을 찾을 수 없습니다.")
                return
            
            # 첫 번째 창 선택 (복수의 창이 있을 경우 향후 선택 UI 추가 가능)
            self.target_hwnd, title = windows[0]
            
            # 창 정보 저장
            self.update_window_info()
            
            self.window_info_var.set(f"연결됨: '{title}' (HWND: {self.target_hwnd})")
            self.status_var.set(f"PID {pid}에 연결되었습니다.")
            
        except ValueError as e:
            messagebox.showerror("입력 오류", f"올바른 PID를 입력해주세요: {str(e)}")
        except psutil.NoSuchProcess:
            messagebox.showerror("오류", f"PID {pid}에 해당하는 프로세스가 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"연결 중 오류가 발생했습니다: {str(e)}")
    
    def update_window_info(self):
        """타겟 윈도우의 현재 위치와 크기 정보를 업데이트"""
        if self.target_hwnd:
            self.window_rect = win32gui.GetWindowRect(self.target_hwnd)
    
    def track_mouse_position(self):
        """현재 마우스 위치를 절대 좌표와 타겟 창 기준 상대 좌표로 표시"""
        x, y = pyautogui.position()
        rel_x, rel_y = x, y
        
        # 연결된 창이 있으면 상대 좌표 계산
        if self.target_hwnd:
            self.update_window_info()
            left, top, _, _ = self.window_rect
            rel_x, rel_y = x - left, y - top
        
        self.mouse_pos_label.config(text=f"마우스 위치: 절대(X={x}, Y={y}) / 상대(X={rel_x}, Y={rel_y})")
        self.root.after(100, self.track_mouse_position)
    
    def toggle_capture(self):
        """캡처 시작/중지 전환"""
        if self.is_capturing:
            self.is_capturing = False
            self.capture_btn.config(text="캡처 시작")
            self.status_var.set("캡처 중지됨")
        else:
            try:
                # 타겟 윈도우 확인
                if not self.target_hwnd:
                    messagebox.showerror("오류", "먼저 프로세스에 연결해주세요.")
                    return
                
                # 창이 여전히 존재하는지 확인
                if not win32gui.IsWindow(self.target_hwnd):
                    messagebox.showerror("오류", "연결된 창이 더 이상 존재하지 않습니다.")
                    self.target_hwnd = None
                    self.window_info_var.set("연결된 창 없음")
                    return
                
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
                # 창이 여전히 존재하는지 확인
                if not win32gui.IsWindow(self.target_hwnd):
                    self.root.after(0, lambda: messagebox.showerror("오류", "창이 닫혔습니다."))
                    self.is_capturing = False
                    self.root.after(0, lambda: self.capture_btn.config(text="캡처 시작"))
                    break
                
                # 윈도우 위치 업데이트
                self.update_window_info()
                left, top, _, _ = self.window_rect
                
                # 상대 좌표로 입력된 값을 절대 좌표로 변환
                x = int(self.x_var.get()) + left
                y = int(self.y_var.get()) + top
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
        """대상 창을 활성화하고 M 키 입력 함수"""
        try:
            if not self.target_hwnd:
                messagebox.showerror("오류", "먼저 프로세스에 연결해주세요.")
                return
            
            # 창이 여전히 존재하는지 확인
            if not win32gui.IsWindow(self.target_hwnd):
                messagebox.showerror("오류", "연결된 창이 더 이상 존재하지 않습니다.")
                self.target_hwnd = None
                self.window_info_var.set("연결된 창 없음")
                return
            
            # 창 활성화
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.1)  # 창이 활성화되기를 기다림
            
            # M 키 입력
            pyautogui.press('m')
            self.status_var.set("'M' 키가 입력되었습니다.")
        except Exception as e:
            messagebox.showerror("키 입력 오류", f"키 입력 중 오류가 발생했습니다: {str(e)}")
    
    def mouse_click(self):
        """대상 창 기준 상대 좌표에서 마우스 클릭 함수"""
        try:
            if not self.target_hwnd:
                messagebox.showerror("오류", "먼저 프로세스에 연결해주세요.")
                return
            
            # 창이 여전히 존재하는지 확인
            if not win32gui.IsWindow(self.target_hwnd):
                messagebox.showerror("오류", "연결된 창이 더 이상 존재하지 않습니다.")
                self.target_hwnd = None
                self.window_info_var.set("연결된 창 없음")
                return
            
            # 윈도우 위치 업데이트
            self.update_window_info()
            left, top, _, _ = self.window_rect
            
            # 클릭 좌표 계산 (상대 좌표를 절대 좌표로 변환)
            if self.click_x_var.get() and self.click_y_var.get():
                rel_x = int(self.click_x_var.get())
                rel_y = int(self.click_y_var.get())
                abs_x = left + rel_x
                abs_y = top + rel_y
            else:
                # 현재 마우스 위치에서 클릭
                abs_x, abs_y = pyautogui.position()
                rel_x, rel_y = abs_x - left, abs_y - top
            
            # 창 활성화 (선택적)
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.1)  # 창이 활성화되기를 기다림
            
            # 클릭
            pyautogui.click(abs_x, abs_y)
            self.status_var.set(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
        except Exception as e:
            messagebox.showerror("마우스 클릭 오류", f"마우스 클릭 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    # 메인 앱 실행
    root = tk.Tk()
    app = AutomationApp(root)
    root.mainloop()