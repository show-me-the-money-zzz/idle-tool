import tkinter as tk
from tkinter import messagebox, ttk
import win32gui
from datetime import datetime
import os
from tkinter import filedialog

from zzz.config import *

class ConnectionFrame(ttk.LabelFrame):
    """프로그램 연결 프레임"""
    
    def __init__(self, parent, window_manager, status_var):
        super().__init__(parent, text="프로그램 연결", padding="10")
        
        self.window_manager = window_manager
        self.status_var = status_var
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # PID 탭과 앱 이름 탭
        tab_control = ttk.Notebook(self)
        tab_control.pack(fill=tk.X, pady=5)
        
        pid_tab = ttk.Frame(tab_control, padding="10")
        name_tab = ttk.Frame(tab_control, padding="10")
        
        tab_control.add(name_tab, text="앱 이름으로 연결")
        tab_control.add(pid_tab, text="PID로 연결")
        
        # PID 탭 내용
        ttk.Label(pid_tab, text="프로세스 ID (PID):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pid_var = tk.StringVar(value=DEFAULT_PID)
        ttk.Entry(pid_tab, textvariable=self.pid_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Button(pid_tab, text="연결", command=self.connect_to_pid).grid(row=0, column=2, padx=5, pady=2)
        
        # 앱 이름 탭 내용
        ttk.Label(name_tab, text="앱 이름 (부분 일치):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.app_name_var = tk.StringVar(value=DEFAULT_APP_NAME)
        ttk.Entry(name_tab, textvariable=self.app_name_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Button(name_tab, text="검색 및 연결", command=self.connect_to_app_name).grid(row=0, column=2, padx=5, pady=2)
        
        # 검색 결과 선택 (앱 이름으로 검색 시)
        ttk.Label(name_tab, text="검색 결과:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.app_list = ttk.Combobox(name_tab, width=40, state="readonly")
        self.app_list.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
        ttk.Button(name_tab, text="선택 연결", command=self.connect_to_selected_app).grid(row=2, column=1, pady=2)
        
        # 연결된 윈도우 정보
        self.window_info_var = tk.StringVar(value="연결된 창 없음")
        ttk.Label(self, textvariable=self.window_info_var).pack(fill=tk.X, pady=5)
        
        # 창 전체 캡처 버튼과 활성화 버튼을 위한 프레임
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.capture_window_btn = ttk.Button(btn_frame, text="창 전체 캡처 저장", command=self.capture_full_window)
        self.capture_window_btn.pack(side=tk.LEFT, padx=5)
        
        # 창 활성화 버튼 추가
        self.activate_window_btn = ttk.Button(btn_frame, text="연결된 창 활성화", command=self.activate_connected_window)
        self.activate_window_btn.pack(side=tk.LEFT, padx=5)
    
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
            
            # 창 활성화
            self.window_manager.activate_window()
            
            self.window_info_var.set(f"연결됨: '{title}' (HWND: {hwnd})")
            self.status_var.set(f"PID {pid}에 연결되었습니다. 창이 활성화되었습니다.")
            
        except ValueError as e:
            messagebox.showerror("입력 오류", f"올바른 PID를 입력해주세요: {str(e)}")
        except Exception as e:
            messagebox.showerror("오류", f"{ERROR_CONNECTION}: {str(e)}")
    
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
            messagebox.showerror("오류", f"{ERROR_FINDING}: {str(e)}")
    
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
            
            # 창 활성화
            self.window_manager.activate_window()
            
            self.window_info_var.set(f"연결됨: '{title}' (PID: {pid}, {proc_name})")
            self.status_var.set(f"창 '{title}'에 연결되었습니다. 창이 활성화되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"{ERROR_CONNECTION}: {str(e)}")
    
    def capture_full_window(self):
        """창 전체 캡처"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", ERROR_NO_WINDOW)
                return
            
            # 외부 참조 필요
            from datetime import datetime
            import os
            from tkinter import filedialog
            
            # 화면 캡처
            from core.capture_utils import CaptureManager
            capture_manager = CaptureManager(self.window_manager, None)
            screenshot = capture_manager.capture_full_window()
            
            if not screenshot:
                messagebox.showerror("오류", "캡처에 실패했습니다.")
                return
            
            # 저장 경로 선택
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            initial_file = f"window_capture_{timestamp}.{DEFAULT_IMAGE_FORMAT}"
            
            # 저장 디렉토리가 있는지 확인하고 없으면 생성
            if not os.path.exists(SAVE_DIRECTORY):
                os.makedirs(SAVE_DIRECTORY)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=f".{DEFAULT_IMAGE_FORMAT}",
                filetypes=[("PNG 파일", "*.png"), ("JPEG 파일", "*.jpg"), ("모든 파일", "*.*")],
                initialfile=initial_file,
                initialdir=SAVE_DIRECTORY
            )
            
            if file_path:
                screenshot.save(file_path)
                self.status_var.set(f"창 캡처가 저장되었습니다: {file_path}")
                
        except Exception as e:
            messagebox.showerror("캡처 오류", f"창 캡처 중 오류가 발생했습니다: {str(e)}")
    
    def activate_connected_window(self):
        """연결된 창 활성화"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", ERROR_NO_WINDOW)
                return
            
            if self.window_manager.activate_window():
                self.status_var.set("연결된 창이 활성화되었습니다.")
            else:
                messagebox.showerror("오류", "창 활성화에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"창 활성화 중 오류가 발생했습니다: {str(e)}")