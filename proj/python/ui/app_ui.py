import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import time
import pyautogui
from datetime import datetime
import os
import win32gui

from core.window_utils import WindowManager
from core.capture_utils import CaptureManager

class AutomationAppUI:
    """자동화 도구 UI 클래스"""
    
    def __init__(self, root):
        # 메인 윈도우 설정
        self.root = root
        self.root.title("PID/앱 이름 기반 화면 캡처 및 자동화 도구")
        self.root.geometry("600x650")
        self.root.resizable(True, True)
        
        # 기본 매니저 객체 생성
        self.window_manager = WindowManager()
        self.capture_manager = CaptureManager(self.window_manager, self.handle_capture_callback)
        
        # UI 컴포넌트 생성
        self.setup_ui()
        
        # 마우스 위치 추적 시작
        self.track_mouse_position()
    
    def setup_ui(self):
        """UI 구성요소 초기화"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 대상 프로그램 연결 프레임
        self.setup_connection_frame(main_frame)
        
        # 영역 설정 프레임
        self.setup_area_frame(main_frame)
        
        # 캡처 시작/중지 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.capture_btn = ttk.Button(btn_frame, text="캡처 시작", command=self.toggle_capture)
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        # 텍스트 결과 영역
        self.setup_result_frame(main_frame)
        
        # 자동화 버튼 프레임
        self.setup_automation_frame(main_frame)
        
        # 상태 표시 바
        self.status_var = tk.StringVar(value="준비 완료")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_connection_frame(self, parent):
        """연결 프레임 설정"""
        connect_frame = ttk.LabelFrame(parent, text="대상 프로그램 연결", padding="10")
        connect_frame.pack(fill=tk.X, pady=5)
        
        # PID 탭과 앱 이름 탭
        tab_control = ttk.Notebook(connect_frame)
        tab_control.pack(fill=tk.X, pady=5)
        
        pid_tab = ttk.Frame(tab_control, padding="10")
        name_tab = ttk.Frame(tab_control, padding="10")
        
        tab_control.add(name_tab, text="앱 이름으로 연결")
        tab_control.add(pid_tab, text="PID로 연결")
        
        # PID 탭 내용
        ttk.Label(pid_tab, text="프로세스 ID (PID):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pid_var = tk.StringVar()
        ttk.Entry(pid_tab, textvariable=self.pid_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Button(pid_tab, text="연결", command=self.connect_to_pid).grid(row=0, column=2, padx=5, pady=2)
        
        # 앱 이름 탭 내용
        ttk.Label(name_tab, text="앱 이름 (부분 일치):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.app_name_var = tk.StringVar()
        ttk.Entry(name_tab, textvariable=self.app_name_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Button(name_tab, text="검색 및 연결", command=self.connect_to_app_name).grid(row=0, column=2, padx=5, pady=2)
        
        # 검색 결과 선택 (앱 이름으로 검색 시)
        ttk.Label(name_tab, text="검색 결과:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.app_list = ttk.Combobox(name_tab, width=40, state="readonly")
        self.app_list.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
        ttk.Button(name_tab, text="선택 연결", command=self.connect_to_selected_app).grid(row=2, column=1, pady=2)
        
        # 연결된 윈도우 정보
        self.window_info_var = tk.StringVar(value="연결된 창 없음")
        ttk.Label(connect_frame, textvariable=self.window_info_var).pack(fill=tk.X, pady=5)
        
        # 창 전체 캡처 버튼
        self.capture_window_btn = ttk.Button(connect_frame, text="창 전체 캡처 저장", command=self.capture_full_window)
        self.capture_window_btn.pack(pady=5)

    def setup_area_frame(self, parent):
        """영역 설정 프레임"""
        area_frame = ttk.LabelFrame(parent, text="캡처 영역 설정 (창 내부 좌표)", padding="10")
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

    def setup_result_frame(self, parent):
        """결과 프레임 설정"""
        result_frame = ttk.LabelFrame(parent, text="인식된 텍스트", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

    def setup_automation_frame(self, parent):
        """자동화 프레임 설정"""
        automation_frame = ttk.LabelFrame(parent, text="자동화 제어", padding="10")
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

    def connect_to_pid(self):
        """PID로 창 연결"""
        try:
            pid = int(self.pid_var.get())
            if not pid:
                raise ValueError("PID가 입력되지 않았습니다.")
            
            window_info = self.window_manager.find_window_by_pid(pid)
            if not window_info:
                messagebox.showerror("오류", f"PID {pid}에 해당하는 창을 찾을 수 없습니다.")
                return
            
            hwnd, title = window_info
            self.window_manager.set_target_window(hwnd)
            
            self.window_info_var.set(f"연결됨: '{title}' (HWND: {hwnd})")
            self.status_var.set(f"PID {pid}에 연결되었습니다.")
            
        except ValueError as e:
            messagebox.showerror("입력 오류", f"올바른 PID를 입력해주세요: {str(e)}")
        except Exception as e:
            messagebox.showerror("오류", f"연결 중 오류가 발생했습니다: {str(e)}")

    def connect_to_app_name(self):
        """앱 이름으로 창 검색"""
        try:
            app_name = self.app_name_var.get().strip()
            if not app_name:
                raise ValueError("앱 이름이 입력되지 않았습니다.")
            
            windows = self.window_manager.find_windows_by_name(app_name)
            
            if not windows:
                messagebox.showinfo("검색 결과", "일치하는 창을 찾을 수 없습니다.")
                return
            
            # 검색 결과를 콤보박스에 표시
            self.app_list["values"] = [f"{title} (PID: {pid}, {proc_name})" for hwnd, title, pid, proc_name in windows]
            self.app_list.current(0)  # 첫 번째 항목 선택
            
            # 창 핸들, PID 값 등을 저장 (나중에 선택용)
            self.found_windows = windows
            
            self.status_var.set(f"{len(windows)}개 창을 찾았습니다. 연결할 창을 선택하세요.")
            
        except ValueError as e:
            messagebox.showerror("입력 오류", f"올바른 앱 이름을 입력해주세요: {str(e)}")
        except Exception as e:
            messagebox.showerror("오류", f"검색 중 오류가 발생했습니다: {str(e)}")

    def connect_to_selected_app(self):
        """콤보박스에서 선택된 앱에 연결"""
        try:
            if not hasattr(self, 'found_windows') or not self.found_windows:
                messagebox.showerror("오류", "먼저 앱을 검색해주세요.")
                return
            
            selected_index = self.app_list.current()
            if selected_index < 0:
                messagebox.showerror("오류", "연결할 창을 선택해주세요.")
                return
            
            # 선택된 창 정보
            hwnd, title, pid, proc_name = self.found_windows[selected_index]
            
            # 창이 여전히 존재하는지 확인
            if not win32gui.IsWindow(hwnd):
                messagebox.showerror("오류", "선택한 창이 존재하지 않습니다.")
                return
            
            self.window_manager.set_target_window(hwnd)
            
            self.window_info_var.set(f"연결됨: '{title}' (PID: {pid}, {proc_name})")
            self.status_var.set(f"창 '{title}'에 연결되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"연결 중 오류가 발생했습니다: {str(e)}")

    def capture_full_window(self):
        """창 전체 캡처"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", "먼저 창에 연결해주세요.")
                return
            
            # 화면 캡처
            screenshot = self.capture_manager.capture_full_window()
            if not screenshot:
                messagebox.showerror("오류", "캡처에 실패했습니다.")
                return
            
            # 저장 경로 선택
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            initial_file = f"window_capture_{timestamp}.png"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG 파일", "*.png"), ("JPEG 파일", "*.jpg"), ("모든 파일", "*.*")],
                initialfile=initial_file
            )
            
            if file_path:
                screenshot.save(file_path)
                self.status_var.set(f"창 캡처가 저장되었습니다: {file_path}")
                
        except Exception as e:
            messagebox.showerror("캡처 오류", f"창 캡처 중 오류가 발생했습니다: {str(e)}")

    def track_mouse_position(self):
        """마우스 위치 추적"""
        x, y = pyautogui.position()
        rel_x, rel_y = x, y
        
        # 연결된 창이 있으면 상대 좌표 계산
        if self.window_manager.is_window_valid():
            rel_x, rel_y = self.window_manager.get_relative_position(x, y)
        
        self.mouse_pos_label.config(text=f"마우스 위치: 절대(X={x}, Y={y}) / 상대(X={rel_x}, Y={rel_y})")
        self.root.after(100, self.track_mouse_position)
    
    def toggle_capture(self):
        """캡처 시작/중지 전환"""
        if self.capture_manager.is_capturing:
            # 캡처 중지
            self.capture_manager.stop_capture()
            self.capture_btn.config(text="캡처 시작")
            self.status_var.set("캡처 중지됨")
        else:
            try:
                # 타겟 윈도우 확인
                if not self.window_manager.is_window_valid():
                    messagebox.showerror("오류", "먼저 창에 연결해주세요.")
                    return
                
                # 입력값 검증
                x = int(self.x_var.get())
                y = int(self.y_var.get())
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                interval = float(self.interval_var.get())
                
                if width <= 0 or height <= 0 or interval <= 0:
                    raise ValueError("너비, 높이, 간격은 양수여야 합니다.")
                
                # 캡처 시작
                self.capture_manager.start_capture(x, y, width, height, interval)
                self.capture_btn.config(text="캡처 중지")
                self.status_var.set("캡처 중...")
                
            except ValueError as e:
                messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
    
    def handle_capture_callback(self, type_str, message):
        """캡처 콜백 처리"""
        if type_str == "result":
            # 텍스트 결과 영역에 추가
            self.update_result(message)
        elif type_str == "error":
            # 에러 메시지 표시
            self.update_status(message)
            # 심각한 오류면 UI 업데이트
            if "창이 닫혔습니다" in message:
                self.root.after(0, lambda: self.capture_btn.config(text="캡처 시작"))
    
    def update_result(self, text):
        """텍스트 결과 영역 업데이트"""
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)  # 스크롤을 최신 내용으로 이동
    
    def update_status(self, text):
        """상태 표시줄 업데이트"""
        self.status_var.set(text)
    
    def press_m_key(self):
        """M 키 입력"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", "먼저 창에 연결해주세요.")
                return
            
            # M 키 입력
            if self.window_manager.send_key('m'):
                self.status_var.set("'M' 키가 입력되었습니다.")
            else:
                messagebox.showerror("오류", "키 입력에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("키 입력 오류", f"키 입력 중 오류가 발생했습니다: {str(e)}")
    
    def mouse_click(self):
        """마우스 클릭"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", "먼저 창에 연결해주세요.")
                return
            
            # 클릭 좌표 계산
            if self.click_x_var.get() and self.click_y_var.get():
                rel_x = int(self.click_x_var.get())
                rel_y = int(self.click_y_var.get())
                
                # 상대 좌표 위치 클릭
                if self.window_manager.click_at_position(rel_x, rel_y):
                    self.status_var.set(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                else:
                    messagebox.showerror("오류", "클릭 작업에 실패했습니다.")
            else:
                # 현재 마우스 위치에서 클릭
                x, y = pyautogui.position()
                left, top, _, _ = self.window_manager.get_window_rect()
                rel_x, rel_y = x - left, y - top
                
                # 창 활성화 후 클릭
                if self.window_manager.activate_window():
                    pyautogui.click(x, y)
                    self.status_var.set(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                else:
                    messagebox.showerror("오류", "클릭 작업에 실패했습니다.")
                    
        except Exception as e:
            messagebox.showerror("마우스 클릭 오류", f"마우스 클릭 중 오류가 발생했습니다: {str(e)}")