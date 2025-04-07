import tkinter as tk
from tkinter import ttk
import time
import os

from core.window_utils import WindowManager
from core.capture_utils import CaptureManager
from core.ocr_engine import setup_tesseract
from zzz.config import *
from core.region_selector import RegionSelector

# 각 UI 컴포넌트 import
from zzz.menu_bar import MenuBar
from zzz.status_bar import StatusBar
from ui.connection_frame import ConnectionFrame
from ui.capture_area_frame import CaptureAreaFrame
from ui.log_frame import LogFrame
from ui.input_handler_frame import InputHandlerFrame

class AppUI:
    """자동화 도구 UI 클래스"""
    
    def __init__(self, root, settings_manager):
        # 메인 윈도우 설정
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(True, True)
        
        # 설정 관리자 저장
        self.settings_manager = settings_manager
        
        # 상태바 생성 (먼저 생성하여 status_var 참조 가능하게)
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = self.status_bar.get_status_var()
        self.status_var.set(STATUS_READY)
        
        # OCR 엔진 초기화
        self.initialize_ocr()
        
        # 메뉴바 생성
        self.menu_bar = MenuBar(
            self.root, 
            self.settings_manager, 
            self.initialize_ocr_with_path
        )
        
        # 기본 매니저 객체 생성
        self.window_manager = WindowManager()
        self.capture_manager = CaptureManager(self.window_manager, self.handle_capture_callback)
        self.region_selector = RegionSelector(self.window_manager)
        
        # UI 컴포넌트 생성
        self.setup_ui()
        
        # 마우스 위치 추적 시작
        self.track_mouse_position()
    
    def initialize_ocr(self):
        """OCR 엔진 초기화"""
        # Tesseract 경로 확인 및 설정
        tesseract_path = self.settings_manager.check_tesseract_path(self.root)
        
        if tesseract_path and os.path.exists(tesseract_path):
            # OCR 엔진 초기화
            return self.initialize_ocr_with_path(tesseract_path)
        else:
            # 사용자에게 경고 메시지 표시
            from tkinter import messagebox
            messagebox.showwarning(
                "OCR 초기화 실패",
                "Tesseract OCR 경로 설정이 필요합니다.\n"
                "설정 메뉴에서 경로를 설정해주세요.",
                parent=self.root
            )
            return False
    
    def initialize_ocr_with_path(self, tesseract_path):
        """지정된 경로로 OCR 엔진 초기화"""
        try:
            setup_tesseract(tesseract_path)
            from tkinter import messagebox
            messagebox.showinfo(
                "설정 완료",
                f"Tesseract OCR 경로가 설정되었습니다.\n{tesseract_path}",
                parent=self.root
            )
            self.status_var.set("Tesseract OCR 경로가 업데이트되었습니다.")
            return True
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror(
                "OCR 초기화 오류",
                f"Tesseract OCR 초기화 중 오류가 발생했습니다.\n{str(e)}",
                parent=self.root
            )
            return False
    
    def setup_ui(self):
        """UI 구성요소 초기화"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 프로그램 연결 프레임
        self.connection_frame = ConnectionFrame(
            main_frame, 
            self.window_manager,
            self.status_var
        )
        self.connection_frame.pack(fill=tk.X, pady=5)
        
        # 2. 캡처 영역 설정 프레임
        self.capture_area_frame = CaptureAreaFrame(
            main_frame,
            self.window_manager,
            self.region_selector,
            self.capture_manager,
            self.status_var
        )
        self.capture_area_frame.pack(fill=tk.X, pady=5)
        
        # 캡처 시작/중지 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.capture_btn = ttk.Button(btn_frame, text="캡처 시작", command=self.toggle_capture)
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        # 3. 로그 프레임
        self.log_frame = LogFrame(
            main_frame,
            self.status_var
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 4. 입력 처리 프레임
        self.input_handler_frame = InputHandlerFrame(
            main_frame,
            self.window_manager,
            self.status_var
        )
        self.input_handler_frame.pack(fill=tk.X, pady=5)
    
    def track_mouse_position(self):
        """마우스 위치 추적"""
        # 입력 처리 프레임의 마우스 위치 업데이트 메소드 호출
        self.input_handler_frame.update_mouse_position()
        self.root.after(100, self.track_mouse_position)

    def toggle_capture(self):
        """캡처 시작/중지 전환"""
        if self.capture_manager.is_capturing:
            # 캡처 중지
            self.capture_manager.stop_capture()
            self.capture_btn.config(text="캡처 시작")
            self.status_var.set(STATUS_STOPPED)
        else:
            try:
                # Tesseract OCR이 설정되어 있는지 확인
                tesseract_path = self.settings_manager.get('Tesseract', 'Path', '')
                if not tesseract_path or not os.path.exists(tesseract_path):
                    # OCR 설정 요청
                    if not self.initialize_ocr():
                        self.status_var.set(ERROR_OCR_CONFIG)
                        return
                
                # 타겟 윈도우 확인
                if not self.window_manager.is_window_valid():
                    from tkinter import messagebox
                    messagebox.showerror("오류", ERROR_NO_WINDOW)
                    return
                
                # 캡처 영역 프레임에서 좌표와 간격 가져오기
                capture_info = self.capture_area_frame.get_capture_info()
                if not capture_info:
                    return
                
                x, y, width, height, interval = capture_info
                
                # 캡처 시작
                self.capture_manager.start_capture(x, y, width, height, interval)
                self.capture_btn.config(text="캡처 중지")
                self.status_var.set(STATUS_CAPTURING)
                
            except ValueError as e:
                from tkinter import messagebox
                messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("캡처 오류", f"캡처 시작 중 오류가 발생했습니다: {str(e)}")

    def handle_capture_callback(self, type_str, message):
        """캡처 콜백 처리"""
        if type_str == "result":
            # 텍스트 결과 영역에 추가
            self.log_frame.add_log(message)
        elif type_str == "error":
            # 에러 메시지 표시
            self.status_var.set(message)
            # 심각한 오류면 UI 업데이트
            if ERROR_WINDOW_CLOSED in message:
                self.root.after(0, lambda: self.capture_btn.config(text="캡처 시작"))