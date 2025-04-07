import tkinter as tk
from tkinter import messagebox, ttk
import time
import os

from core.window_utils import WindowManager
from core.capture_utils import CaptureManager
from core.ocr_engine import setup_tesseract
from zzz.config import *
from core.region_selector import RegionSelector

# 각 프레임 클래스 import
from ui.connection_frame import ConnectionFrame
from ui.capture_area_frame import CaptureAreaFrame
from ui.log_frame import LogFrame
from ui.input_handler_frame import InputHandlerFrame

class AutomationAppUI:
    """자동화 도구 UI 클래스"""
    
    def __init__(self, root, settings_manager):
        # 메인 윈도우 설정
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.resizable(True, True)
        
        # 설정 관리자 저장
        self.settings_manager = settings_manager
        
        # OCR 엔진 초기화
        self.initialize_ocr()
        
        # 기본 매니저 객체 생성
        self.window_manager = WindowManager()
        self.capture_manager = CaptureManager(self.window_manager, self.handle_capture_callback)
        self.region_selector = RegionSelector(self.window_manager)  # 영역 선택 도구
        
        # 상태바 생성
        self.status_var = tk.StringVar(value=STATUS_READY)
        
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
            setup_tesseract(tesseract_path)
            return True
        else:
            # 사용자에게 경고 메시지 표시
            messagebox.showwarning(
                "OCR 초기화 실패",
                "Tesseract OCR 경로 설정이 필요합니다.\n"
                "설정 메뉴에서 경로를 설정해주세요.",
                parent=self.root
            )
            return False
    
    def setup_ui(self):
        """UI 구성요소 초기화"""
        # 메뉴바 추가
        self.setup_menu()
        
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
        
        # 3. 로그 프레임 (이전의 인식된 텍스트 영역)
        self.log_frame = LogFrame(
            main_frame,
            self.status_var
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 4. 입력 처리 프레임 (이전의 자동화 영역)
        self.input_handler_frame = InputHandlerFrame(
            main_frame,
            self.window_manager,
            self.status_var
        )
        self.input_handler_frame.pack(fill=tk.X, pady=5)
        
        # 상태 표시 바
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_menu(self):
        """메뉴바 설정"""
        # 메뉴바 생성
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="종료", command=self.root.quit)
        
        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="Tesseract OCR 경로 설정", command=self.set_tesseract_path)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self.show_help)
        help_menu.add_command(label="정보", command=self.show_about)
    
    def set_tesseract_path(self):
        """Tesseract OCR 경로 설정"""
        # 현재 설정값 가져오기
        current_path = self.settings_manager.get('Tesseract', 'Path', DEFAULT_TESSERACT_PATH)
        
        # 사용자에게 경로 선택 요청
        new_path = self.settings_manager.prompt_tesseract_path(self.root)
        
        if new_path:
            # OCR 엔진 다시 초기화
            try:
                setup_tesseract(new_path)
                messagebox.showinfo(
                    "설정 완료",
                    f"Tesseract OCR 경로가 설정되었습니다.\n{new_path}",
                    parent=self.root
                )
                self.status_var.set("Tesseract OCR 경로가 업데이트되었습니다.")
            except Exception as e:
                messagebox.showerror(
                    "OCR 초기화 오류",
                    f"Tesseract OCR 초기화 중 오류가 발생했습니다.\n{str(e)}",
                    parent=self.root
                )
    
    def show_help(self):
        """사용법 표시"""
        help_text = """
사용법:

1. 프로그램 연결:
   - '앱 이름으로 연결' 탭에서 앱 이름 입력 후 검색
   - 목록에서 원하는 앱 선택 후 '선택 연결' 클릭

2. 캡처 영역 설정:
   - '드래그로 영역 선택' 버튼 클릭 후 화면에서 영역 드래그
   - 또는 직접 좌표와 크기 입력

3. 캡처 시작/중지:
   - '캡처 시작' 버튼 클릭하여 OCR 인식 시작
   - 다시 클릭하여 중지

4. 입력 처리:
   - 키보드 입력: 원하는 키를 입력 필드에 입력 후 실행
   - 마우스 클릭: 설정된 좌표에 클릭 전송

5. OCR 설정:
   - '설정' 메뉴에서 Tesseract OCR 경로 설정
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("사용법")
        help_window.geometry("500x400")
        
        text = tk.Text(help_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)  # 읽기 전용
    
    def show_about(self):
        """정보 표시"""
        about_text = """
쇼 미더 머니 - 로드나인

버전: 1.0.0

화면 영역을 캡처하여 OCR로 텍스트를 인식하는 도구입니다.

※ OCR 기능을 사용하려면 Tesseract OCR이 필요합니다.
설치: https://github.com/UB-Mannheim/tesseract/wiki
        """
        
        messagebox.showinfo("정보", about_text, parent=self.root)
    
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
                messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            except Exception as e:
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