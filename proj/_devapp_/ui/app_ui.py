import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk  # PIL의 ImageTk 모듈 추가
import time
import pyautogui
from datetime import datetime
import os
import win32gui

from core.window_utils import WindowManager
from core.capture_utils import CaptureManager
from core.ocr_engine import setup_tesseract
from zzz.config import *  # 상수값 가져오기
from core.region_selector import RegionSelector  # 영역 선택 도구

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
        self.status_var = tk.StringVar(value=STATUS_READY)
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

1. 대상 프로그램 연결:
   - '앱 이름으로 연결' 탭에서 앱 이름 입력 후 검색
   - 목록에서 원하는 앱 선택 후 '선택 연결' 클릭

2. 캡처 영역 설정:
   - '드래그로 영역 선택' 버튼 클릭 후 화면에서 영역 드래그
   - 또는 직접 좌표와 크기 입력

3. 캡처 시작/중지:
   - '캡처 시작' 버튼 클릭하여 OCR 인식 시작
   - 다시 클릭하여 중지

4. 자동화 기능:
   - 'M 키 입력': 대상 창에 M 키 입력
   - '마우스 클릭': 설정된 좌표에 클릭 전송

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
        ttk.Label(connect_frame, textvariable=self.window_info_var).pack(fill=tk.X, pady=5)
        
        # 창 전체 캡처 버튼과 활성화 버튼을 위한 프레임
        btn_frame = ttk.Frame(connect_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.capture_window_btn = ttk.Button(btn_frame, text="창 전체 캡처 저장", command=self.capture_full_window)
        self.capture_window_btn.pack(side=tk.LEFT, padx=5)
        
        # 창 활성화 버튼 추가
        self.activate_window_btn = ttk.Button(btn_frame, text="연결된 창 활성화", command=self.activate_connected_window)
        self.activate_window_btn.pack(side=tk.LEFT, padx=5)

    def setup_area_frame(self, parent):
        """영역 설정 프레임"""
        area_frame = ttk.LabelFrame(parent, text="캡처 영역 설정 (창 내부 좌표)", padding="10")
        area_frame.pack(fill=tk.X, pady=5)
        
        # 왼쪽(설정) 및 오른쪽(미리보기) 영역을 나누기 위한 프레임
        main_frame = ttk.Frame(area_frame)
        main_frame.pack(fill=tk.X, expand=True)
        
        # 좌측 입력 프레임
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # X 좌표 (상대적)
        ttk.Label(input_frame, text="X 좌표:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_var = tk.StringVar(value=DEFAULT_CAPTURE_X)
        ttk.Entry(input_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Y 좌표 (상대적)
        ttk.Label(input_frame, text="Y 좌표:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.y_var = tk.StringVar(value=DEFAULT_CAPTURE_Y)
        ttk.Entry(input_frame, textvariable=self.y_var, width=10).grid(row=0, column=3, sticky=tk.W, pady=2)
        
        # 너비
        ttk.Label(input_frame, text="너비:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.StringVar(value=DEFAULT_CAPTURE_WIDTH)
        ttk.Entry(input_frame, textvariable=self.width_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 높이
        ttk.Label(input_frame, text="높이:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.height_var = tk.StringVar(value=DEFAULT_CAPTURE_HEIGHT)
        ttk.Entry(input_frame, textvariable=self.height_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=2)
        
        # 캡처 간격 설정
        ttk.Label(input_frame, text="캡처 간격(초):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar(value=DEFAULT_CAPTURE_INTERVAL)
        ttk.Entry(input_frame, textvariable=self.interval_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 영역 선택 버튼 (드래그로 영역 선택)
        select_area_btn = ttk.Button(input_frame, text="드래그로 영역 선택", command=self.select_capture_area)
        select_area_btn.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # 캡처 미리보기 업데이트 버튼
        preview_btn = ttk.Button(input_frame, text="미리보기 갱신", command=self.update_area_preview)
        preview_btn.grid(row=3, column=2, columnspan=2, sticky=tk.W, pady=10)
        
        # 창 내 영역만 선택 체크박스
        self.window_only_var = tk.BooleanVar(value=True)
        window_only_check = ttk.Checkbutton(
            input_frame, 
            text="창 내부만 선택", 
            variable=self.window_only_var
        )
        window_only_check.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=2)
        
        # 우측 미리보기 프레임
        preview_frame = ttk.LabelFrame(main_frame, text="영역 미리보기")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 미리보기 캔버스 (이미지 표시용)
        self.preview_canvas = tk.Canvas(preview_frame, width=200, height=150, bg='lightgray')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 미리보기 없음 텍스트
        self.preview_canvas.create_text(
            100, 75, 
            text="영역을 선택하면\n미리보기가 표시됩니다", 
            fill="darkgray", 
            justify=tk.CENTER
        )
        
        # 미리보기 이미지 저장 변수
        self.preview_image = None
        self.preview_photo = None
        self.preview_image_id = None

    def setup_result_frame(self, parent):
        """결과 프레임 설정"""
        result_frame = ttk.LabelFrame(parent, text="인식된 텍스트", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 버튼 프레임 (상단)
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 로그 초기화 버튼
        self.clear_log_btn = ttk.Button(
            button_frame, 
            text="로그 초기화", 
            command=self.clear_result_log
        )
        self.clear_log_btn.pack(side=tk.RIGHT, padx=5)
        
        # 텍스트 영역과 스크롤바를 담을 프레임
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 텍스트 영역
        self.result_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

    def clear_result_log(self):
        """인식된 텍스트 로그 초기화"""
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("로그가 초기화되었습니다.")

    def setup_automation_frame(self, parent):
        """자동화 프레임 설정"""
        automation_frame = ttk.LabelFrame(parent, text="자동화 제어", padding="10")
        automation_frame.pack(fill=tk.X, pady=5)
        
        # 키 입력 관련 프레임
        key_frame = ttk.Frame(automation_frame)
        key_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 키 입력 필드
        ttk.Label(key_frame, text="입력 키:").pack(side=tk.LEFT, padx=(0, 5))
        self.input_key_var = tk.StringVar(value="m")
        ttk.Entry(key_frame, textvariable=self.input_key_var, width=5).pack(side=tk.LEFT, padx=(0, 10))
        
        # 키 입력 버튼
        self.key_btn = ttk.Button(key_frame, text="키보드 입력", command=self.press_key)
        self.key_btn.pack(side=tk.LEFT, padx=5)
        
        # ESC 키 입력 버튼
        self.esc_btn = ttk.Button(key_frame, text="ESC 키 입력", command=self.press_esc_key)
        self.esc_btn.pack(side=tk.LEFT, padx=5)
        
        # 마우스 좌표 입력 필드 (상대적)
        ttk.Label(automation_frame, text="클릭 X (창 내부):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.click_x_var = tk.StringVar(value=DEFAULT_CLICK_X)
        click_x_entry = ttk.Entry(automation_frame, textvariable=self.click_x_var, width=10)
        click_x_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 마우스 클릭 버튼
        self.click_btn = ttk.Button(automation_frame, text="마우스 클릭", command=self.mouse_click)
        self.click_btn.grid(row=1, column=2, padx=5, pady=2)
        
        ttk.Label(automation_frame, text="클릭 Y (창 내부):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.click_y_var = tk.StringVar(value=DEFAULT_CLICK_Y)
        click_y_entry = ttk.Entry(automation_frame, textvariable=self.click_y_var, width=10)
        click_y_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 탭 순서 설정 - 클릭 X에서 클릭 Y로 이동하도록
        click_x_entry.bind('<Tab>', lambda e: click_y_entry.focus_set() or 'break')
        
        # 현재 마우스 위치 표시 레이블 (절대 좌표와 상대 좌표)
        self.mouse_pos_label = ttk.Label(automation_frame, text="마우스 위치: 절대(X=0, Y=0) / 상대(X=0, Y=0)")
        self.mouse_pos_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 마우스 위치 복사 버튼
        copy_pos_btn = ttk.Button(automation_frame, text="현재 위치 복사", command=self.copy_current_mouse_position)
        copy_pos_btn.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
    
    def select_capture_area(self):
        """드래그로 캡처 영역 선택"""
        # 창이 연결되어 있고 '창 내부만 선택' 옵션이 활성화된 경우에만 창 내부로 제한
        target_window_only = self.window_only_var.get() and self.window_manager.is_window_valid()
        
        if target_window_only and not self.window_manager.is_window_valid():
            messagebox.showerror("오류", "창 내부 선택을 위해서는 먼저 창에 연결해주세요.")
            return
        
        # 선택 임시 중단을 알림
        self.status_var.set("영역 선택 중... (ESC 키를 누르면 취소)")
        self.root.update()
        
        # 창 최소화 (선택 화면이 가려지지 않도록)
        self.root.iconify()
        time.sleep(0.5)  # 창이 최소화될 시간 확보
        
        # 영역 선택 시작
        selected_region = self.region_selector.start_selection(
            callback=self.handle_region_selection,
            target_window_only=target_window_only
        )
        
        # 창 복원
        self.root.deiconify()
    
    def handle_region_selection(self, region_info):
        """영역 선택 결과 처리"""
        if not region_info:
            self.status_var.set("영역 선택이 취소되었습니다.")
            return
        
        # 선택된 영역 정보를 UI에 업데이트
        rel_x1, rel_y1, rel_x2, rel_y2 = region_info["rel"]
        width = region_info["width"]
        height = region_info["height"]
        
        self.x_var.set(str(rel_x1))
        self.y_var.set(str(rel_y1))
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        
        self.status_var.set(f"영역이 선택되었습니다: X={rel_x1}, Y={rel_y1}, 너비={width}, 높이={height}")
        
        # 선택 후 미리보기 업데이트
        self.update_area_preview()

    def update_area_preview(self):
        """캡처 영역 미리보기 업데이트"""
        try:
            # 창이 연결되어 있는지 확인
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", ERROR_NO_WINDOW)
                return
            
            # 캡처 영역 좌표 가져오기
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                
                if width <= 0 or height <= 0:
                    raise ValueError("너비와 높이는 양수여야 합니다.")
            except ValueError as e:
                messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
                return
            
            # 전체 창 캡처
            full_window_img = self.capture_manager.capture_full_window()
            if not full_window_img:
                messagebox.showerror("오류", "창 캡처에 실패했습니다.")
                return
            
            # 캡처 영역 추출
            try:
                # PIL 이미지에서 영역 추출
                crop_region = (x, y, x + width, y + height)
                
                # 영역이 이미지 범위를 벗어나는지 확인
                img_width, img_height = full_window_img.size
                if crop_region[0] < 0 or crop_region[1] < 0 or crop_region[2] > img_width or crop_region[3] > img_height:
                    messagebox.showwarning(
                        "영역 경고", 
                        "설정한 영역이 창 범위를 벗어납니다. 일부만 표시됩니다.",
                        parent=self.root
                    )
                
                # 캔버스 크기 가져오기
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                # 이미지 크기 계산에 너무 작은 값이 사용되지 않도록 제한
                if canvas_width < 50:
                    canvas_width = 200
                if canvas_height < 50:
                    canvas_height = 150
                    
                # 영역 자르기
                cropped_img = full_window_img.crop((
                    max(0, crop_region[0]),
                    max(0, crop_region[1]),
                    min(img_width, crop_region[2]),
                    min(img_height, crop_region[3])
                ))
                
                # 캔버스에 맞게 이미지 크기 조정 (비율 유지)
                img_width, img_height = cropped_img.size
                
                # 비율 계산
                width_ratio = canvas_width / img_width
                height_ratio = canvas_height / img_height
                scale_ratio = min(width_ratio, height_ratio)
                
                # 이미지가 너무 크면 축소
                if scale_ratio < 1:
                    new_width = int(img_width * scale_ratio)
                    new_height = int(img_height * scale_ratio)
                    resized_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)
                else:
                    resized_img = cropped_img
                
                # 기존 이미지 삭제
                if self.preview_image_id:
                    self.preview_canvas.delete(self.preview_image_id)
                
                # 캔버스에 이미지 표시
                self.preview_image = resized_img
                self.preview_photo = ImageTk.PhotoImage(resized_img)
                
                # 캔버스 중앙에 이미지 배치
                x_pos = (canvas_width - self.preview_photo.width()) // 2
                y_pos = (canvas_height - self.preview_photo.height()) // 2
                
                self.preview_image_id = self.preview_canvas.create_image(
                    x_pos, y_pos, 
                    image=self.preview_photo, 
                    anchor=tk.NW
                )
                
                # 미리보기 정보 표시
                info_text = f"{width}x{height} 픽셀"
                self.preview_canvas.create_text(
                    canvas_width//2, canvas_height-10,
                    text=info_text,
                    fill="navy",
                    font=("Arial", 8)
                )
                
                self.status_var.set(f"영역 미리보기가 업데이트되었습니다.")
            
            except Exception as e:
                messagebox.showerror("미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
        except Exception as e:
            messagebox.showerror("미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
    
    def copy_current_mouse_position(self):
        """현재 마우스 위치를 클릭 좌표에 복사"""
        if not self.window_manager.is_window_valid():
            messagebox.showerror("오류", "먼저 창에 연결해주세요.")
            return
        
        # 현재 마우스 위치
        x, y = pyautogui.position()
        
        # 상대 좌표 계산
        rel_x, rel_y = self.window_manager.get_relative_position(x, y)
        
        # 클릭 좌표에 복사
        self.click_x_var.set(str(rel_x))
        self.click_y_var.set(str(rel_y))
        
        self.status_var.set(f"현재 마우스 위치가 복사되었습니다: X={rel_x}, Y={rel_y}")

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
            
            # 화면 캡처
            screenshot = self.capture_manager.capture_full_window()
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
                self.status_var.set(STATUS_CAPTURING)
                
            except ValueError as e:
                messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            except Exception as e:
                messagebox.showerror("캡처 오류", f"캡처 시작 중 오류가 발생했습니다: {str(e)}")

    def handle_capture_callback(self, type_str, message):
        """캡처 콜백 처리"""
        # print(f"콜백 호출: {type_str} - {message[:30]}...")  # 디버깅 정보
        
        if type_str == "result":
            # 텍스트 결과 영역에 추가
            self.update_result(message)
        elif type_str == "error":
            # 에러 메시지 표시
            self.update_status(message)
            # 심각한 오류면 UI 업데이트
            if ERROR_WINDOW_CLOSED in message:
                self.root.after(0, lambda: self.capture_btn.config(text="캡처 시작"))

    def update_result(self, text):
        """텍스트 결과 영역 업데이트"""
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)  # 스크롤을 최신 내용으로 이동

    def update_status(self, text):
        """상태 표시줄 업데이트"""
        self.status_var.set(text)

    def press_key(self):
        """사용자가 지정한 키 입력"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", ERROR_NO_WINDOW)
                return
            
            # 사용자가 입력한 키 가져오기
            key = self.input_key_var.get()
            if not key:
                messagebox.showinfo("알림", "입력할 키를 지정해주세요.")
                return
            
            # 키 입력
            if self.window_manager.send_key(key):
                self.status_var.set(f"'{key}' 키가 입력되었습니다.")
            else:
                messagebox.showerror("오류", "키 입력에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("키 입력 오류", f"키 입력 중 오류가 발생했습니다: {str(e)}")

    def press_esc_key(self):
        """ESC 키 입력"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", ERROR_NO_WINDOW)
                return
            
            # ESC 키 입력
            if self.window_manager.send_key('esc'):
                self.status_var.set("'ESC' 키가 입력되었습니다.")
            else:
                messagebox.showerror("오류", "ESC 키 입력에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("키 입력 오류", f"ESC 키 입력 중 오류가 발생했습니다: {str(e)}")

    def mouse_click(self):
        """마우스 클릭"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", ERROR_NO_WINDOW)
                return
            
            # 클릭 좌표 계산
            if self.click_x_var.get() and self.click_y_var.get():
                rel_x = int(self.click_x_var.get())
                rel_y = int(self.click_y_var.get())
                
                # 상태 표시 업데이트
                self.status_var.set(f"클릭 중... (X={rel_x}, Y={rel_y})")
                self.root.update()  # UI 업데이트
                
                # 상대 좌표 위치 클릭
                if self.window_manager.click_at_position(rel_x, rel_y):
                    self.status_var.set(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                else:
                    messagebox.showerror("오류", "클릭 작업에 실패했습니다.")
            else:
                messagebox.showinfo("알림", "클릭할 좌표를 설정해주세요.")
                
        except Exception as e:
            messagebox.showerror("마우스 클릭 오류", f"마우스 클0릭 중 오류가 발생했습니다: {str(e)}")
    
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