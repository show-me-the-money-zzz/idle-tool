import tkinter as tk
from tkinter import messagebox, ttk
import time
from PIL import Image, ImageTk
from datetime import datetime

from zzz.config import *
from stores import areas
from grinder_utils.system import Calc_MS

class CaptureAreaPopup(tk.Toplevel):
    """캡처 영역 설정 팝업 창"""
    
    READTEXT_BUTTON_START_TEXT = "글자 읽기 ▶"
    READTEXT_BUTTON_STOP_TEXT = "글자 읽기 ■"

    def __init__(self, parent, window_manager, region_selector, capture_manager, status_var, on_close_callback=None):
        super().__init__(parent)
        self.title("캡처 영역 설정")
        self.geometry("700x640")
        self.transient(parent)
        self.on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.parent = parent
        self.window_manager = window_manager
        self.region_selector = region_selector
        self.capture_manager = capture_manager
        self.status_var = status_var

        self.preview_image = None
        self.preview_photo = None
        self.preview_image_id = None
        self.capture_settings = None

        self.reading_text = False

        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding="10", height=640)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 좌측 메인 영역과 우측 버튼 영역으로 분할
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        buttons_container = ttk.Frame(main_frame)
        buttons_container.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 위치 및 크기 설정 영역 (상단)
        coords_frame = ttk.LabelFrame(content_frame, text="위치 및 크기", padding="10")
        coords_frame.pack(fill=tk.X, pady=(0, 5))
        
        # KEY 입력 영역
        key_frame = ttk.Frame(coords_frame)
        key_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(key_frame, text="KEY").pack(side=tk.LEFT, padx=(0, 5))
        self.key_var = tk.StringVar(value="")
        ttk.Entry(key_frame, textvariable=self.key_var, width=20).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 예약 키워드 정보 (자동 높이 조절 Text 위젯)
        info_frame = ttk.Frame(coords_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        info_frame.columnconfigure(0, weight=1)
        
        self.desc_key_text = tk.Text(info_frame, height=1, wrap=tk.WORD, 
                                font=("TkDefaultFont", 8), relief="flat", 
                                bg=self.cget("background"))
        self.desc_key_text.grid(row=0, column=0, sticky=tk.EW)
        
        keywords_text = f"※ 예약 키워드: {' / '.join(LOOP_TEXT_KEYWORD)}"
        keywords_text += " / ";
        keywords_text += f"{' / '.join(LOOP_IMAGE_KEYWORD)}"
        self.desc_key_text.insert("1.0", keywords_text)
        
        # 텍스트 높이 자동 조절 함수
        def update_text_height(event=None):
            width = self.desc_key_text.winfo_width()
            if width > 1:
                text_content = self.desc_key_text.get("1.0", "end-1c")
                font = self.desc_key_text.cget("font")
                
                temp_canvas = tk.Canvas(self)
                text_item = temp_canvas.create_text(0, 0, text=text_content, font=font, anchor="nw", width=width-10)
                bbox = temp_canvas.bbox(text_item)
                temp_canvas.destroy()
                
                if bbox:
                    line_height = 14
                    needed_lines = max(1, (bbox[3] - bbox[1]) // line_height)
                    self.desc_key_text.configure(height=needed_lines)
        
        self.desc_key_text.bind("<Configure>", update_text_height)
        self.desc_key_text.configure(state="disabled")
        self.desc_key_text.bind("<1>", lambda event: self.desc_key_text.focus_set())
        
        # X, Y, 너비, 높이를 한 줄에 배치
        controls_frame = ttk.Frame(coords_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 숫자만 입력 가능한 Spinbox 사용
        From_Spinbox = 0
        To_Spinbox = 99999

        ttk.Label(controls_frame, text="X 좌표:").grid(row=0, column=0, sticky=tk.W, padx=(0, 2))
        self.x_var = tk.IntVar(value=int(DEFAULT_CAPTURE_X))
        tk.Spinbox(controls_frame, from_=From_Spinbox, to=To_Spinbox, textvariable=self.x_var, width=5).grid(row=0, column=1, sticky=tk.W, padx=(0, 5))

        ttk.Label(controls_frame, text="Y 좌표:").grid(row=0, column=2, sticky=tk.W, padx=(5, 2))
        self.y_var = tk.IntVar(value=int(DEFAULT_CAPTURE_Y))
        tk.Spinbox(controls_frame, from_=From_Spinbox, to=To_Spinbox, textvariable=self.y_var, width=5).grid(row=0, column=3, sticky=tk.W, padx=(0, 5))

        ttk.Label(controls_frame, text="너비:").grid(row=0, column=4, sticky=tk.W, padx=(5, 2))
        self.width_var = tk.IntVar(value=int(DEFAULT_CAPTURE_WIDTH))
        tk.Spinbox(controls_frame, from_=From_Spinbox, to=To_Spinbox, textvariable=self.width_var, width=5).grid(row=0, column=5, sticky=tk.W, padx=(0, 5))

        ttk.Label(controls_frame, text="높이:").grid(row=0, column=6, sticky=tk.W, padx=(5, 2))
        self.height_var = tk.IntVar(value=int(DEFAULT_CAPTURE_HEIGHT))
        tk.Spinbox(controls_frame, from_=From_Spinbox, to=To_Spinbox, textvariable=self.height_var, width=5).grid(row=0, column=7, sticky=tk.W, padx=(0, 5))
        
        # 간격 및 창 내부 선택 옵션
        options_frame = ttk.Frame(coords_frame)
        options_frame.pack(fill=tk.X)
        
        ttk.Label(options_frame, text="캡처 간격(초):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar(value=1.0)
        ttk.Entry(options_frame, textvariable=self.interval_var, width=8, state=tk.DISABLED).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        self.window_only_var = tk.BooleanVar(value=True)
        window_only_check = ttk.Checkbutton(options_frame, text="창 내부만 선택", variable=self.window_only_var)
        window_only_check.grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        
        # 미리보기 영역 (왼쪽 하단)
        preview_frame = ttk.LabelFrame(content_frame, text="영역 미리보기")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 색상 바 프레임: preview_frame의 오른쪽 상단에 부착
        color_bar_frame = ttk.Frame(preview_frame)
        color_bar_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))

        # 색 추출 버튼 (좌측 상단 고정)
        self.extract_color_btn = ttk.Button(color_bar_frame, text="색 추출", command=self.extract_color)
        self.extract_color_btn.pack(side=tk.LEFT, anchor="n", padx=(0, 10))

        # 컬러 캔버스를 감싸는 프레임 (버튼 오른쪽 상단)
        color_container = ttk.Frame(color_bar_frame)
        color_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 컬러 캔버스 (작은 컬러 박스 표시)
        self.color_canvas = tk.Canvas(color_container, height=16, highlightthickness=0)
        self.color_canvas.pack(side=tk.TOP, fill=tk.X)

        # 스크롤바는 캔버스 아래쪽 (폭 자동 정렬)
        color_scrollbar = ttk.Scrollbar(color_container, orient=tk.HORIZONTAL, command=self.color_canvas.xview)
        color_scrollbar.pack(side=tk.TOP, fill=tk.X)
        self.color_canvas.configure(xscrollcommand=color_scrollbar.set)

        # 컬러 프레임 (컬러 박스가 담기는 내부 프레임)
        self.color_frame = ttk.Frame(self.color_canvas)
        self.color_canvas.create_window((0, 0), window=self.color_frame, anchor="nw")

        # 컬러 프레임 스크롤 자동 조정
        def update_scroll(event=None):
            self.color_canvas.configure(scrollregion=self.color_canvas.bbox("all"))

        self.color_frame.bind("<Configure>", update_scroll)
        # 기본 색상 추가
        self.Test_AddColors()
        
        self.preview_canvas = tk.Canvas(preview_frame, width=300, height=200, bg='lightgray')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_canvas.create_text(
            150, 100, 
            text="영역을 선택하면\n미리보기가 표시됩니다", 
            fill="darkgray", 
            justify=tk.CENTER
        )
        
        # 오른쪽 버튼 그룹 - 첫 번째 그룹: 영역 선택/미리보기/글자 읽기
        btn_width = 12  # 버튼 너비 통일

        # 첫 번째 버튼 그룹을 위한 프레임
        btn_group1 = ttk.LabelFrame(buttons_container, text="동작")
        btn_group1.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        ttk.Button(
            btn_group1, text="영역 선택", width=btn_width,
            command=self.select_capture_area
        ).pack(side=tk.TOP, pady=2, padx=5, fill=tk.X)

        ttk.Button(
            btn_group1, text="미리보기 업뎃", width=btn_width,
            command=self.update_area_preview
        ).pack(side=tk.TOP, pady=2, padx=5, fill=tk.X)

        self.read_text_btn = ttk.Button(
            btn_group1, text=CaptureAreaPopup.READTEXT_BUTTON_START_TEXT, width=btn_width,
            command=self.toggle_read_text
        )
        self.read_text_btn.pack(side=tk.TOP, pady=2, padx=5, fill=tk.X)

        # 두 번째 버튼 그룹을 위한 프레임 - 남은 공간을 모두 차지하도록 설정
        btn_group2 = ttk.LabelFrame(buttons_container, text="작업")
        btn_group2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # expand=True로 남은 공간 차지

        # 상단 버튼 영역
        top_buttons = ttk.Frame(btn_group2)
        top_buttons.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # 저장 버튼 - 녹색, 흰색 텍스트
        save_btn = tk.Button(
            top_buttons, text="저장", width=btn_width,
            command=self.apply_settings,
            bg="#2ecc71",  # 녹색 배경
            fg="white",    # 흰색 텍스트
            activebackground="#27ae60",  # 클릭 시 약간 더 어두운 녹색
            activeforeground="white",    # 클릭 시 흰색 텍스트 유지
            font=("TkDefaultFont", 9, "bold")  # 약간 더 굵은 폰트
        )
        save_btn.pack(side=tk.TOP, pady=(2, 1), fill=tk.X)  # 상단 패딩만 2, 하단 패딩은 1로 설정

        # 이미지로 저장 버튼 - 저장 버튼과 가까이 배치
        save_image_btn = tk.Button(
            top_buttons, text="이미지로 저장", width=btn_width,
            command=lambda: self.save_as_image(),  # 이 함수는 구현해야 함
            bg="#3498db",  # 파란색 배경
            fg="white",    # 흰색 텍스트
            activebackground="#2980b9",  # 클릭 시 약간 더 어두운 파란색
            activeforeground="white",    # 클릭 시 흰색 텍스트 유지
            font=("TkDefaultFont", 9, "bold")  # 약간 더 굵은 폰트
        )
        save_image_btn.pack(side=tk.TOP, pady=1, fill=tk.X)

        # 하단 버튼 영역 - 취소 버튼을 최하단에 배치하기 위한 프레임
        bottom_frame = ttk.Frame(btn_group2)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # 취소하고 닫기 버튼 - 빨간색, 흰색 텍스트
        cancel_btn = tk.Button(
            bottom_frame, text="취소하고 닫기", width=btn_width,
            command=self.on_close,
            bg="#e74c3c",  # 빨간색 배경
            fg="white",    # 흰색 텍스트
            activebackground="#c0392b",  # 클릭 시 약간 더 어두운 빨간색
            activeforeground="white",    # 클릭 시 흰색 텍스트 유지
            font=("TkDefaultFont", 9, "bold")  # 약간 더 굵은 폰트
        )
        cancel_btn.pack(side=tk.BOTTOM, fill=tk.X)
                
        # 하단 로그 프레임
        log_frame = ttk.LabelFrame(self, text="인식된 텍스트", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 로그 컨트롤 프레임 - 상단에 더 가깝게 배치
        log_ctrl_frame = ttk.Frame(log_frame)
        log_ctrl_frame.pack(fill=tk.X, pady=(0, 2))  # 상단 패딩 0, 하단 패딩 2로 줄임

        # 로그 초기화 버튼을 오른쪽에 배치
        ttk.Button(log_ctrl_frame, text="로그 초기화", command=self.clear_log).pack(side=tk.RIGHT)

        # 텍스트 영역 - 컨트롤 바로 아래에 배치
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))  # 패딩 제거

        # 로그 텍스트 박스
        self.log_text = tk.Text(text_frame, wrap=tk.WORD, height=8)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 스크롤바
        scrollbar = ttk.Scrollbar(text_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def toggle_read_text(self):
        self.reading_text = not self.reading_text
        self.read_text_btn.config(text=CaptureAreaPopup.READTEXT_BUTTON_STOP_TEXT if self.reading_text else CaptureAreaPopup.READTEXT_BUTTON_START_TEXT)
        if self.reading_text:
            self._read_loop_main()

    def _read_loop_main(self):
        if not self.reading_text:
            return
        self.read_text_from_area()
        try:
            interval = Calc_MS(float(self.interval_var.get()))
        except ValueError:
            interval = 2000
        self.after(interval, self._read_loop_main)
        
    def extract_color(self):
        """색상 선택 팝업 표시"""
        # 캡처 영역 미리보기가 있을 때만 색상 추출 가능
        if not hasattr(self, 'preview_image') or self.preview_image is None:
            messagebox.showinfo("알림", "먼저 영역을 선택하고 미리보기를 업데이트해주세요.", parent=self)
            return
        
        # 색상 선택 팝업 열기
        from ui.nodes.color_picker_popup import ColorPickerPopup
        
        # 색상 선택 결과 처리 콜백
        def handle_color_selection(selected_colors, processed_image):
            if selected_colors:
                # 선택된 색상 리스트를 데이터에 저장
                color_hex = selected_colors[0] if selected_colors else "#000000"
                self.selected_color = color_hex
                
                # 상태 업데이트
                self.status_var.set(f"색상이 선택되었습니다: {color_hex}")
        
        # 이미지 객체를 직접 전달
        picker = ColorPickerPopup(self, self.preview_image, callback=handle_color_selection)

    def Callback_PickColor(selected_colors, processed_image):
        # 여기서 선택된 색상과 처리된 이미지를 활용하는 코드 작성
        # 예: 선택된 색상을 저장하거나, 처리된 이미지를 사용
        print(f"사용자가 선택한 색상: {selected_colors}")
        
        # # 색상 파일 저장 예시
        # with open("selected_colors.txt", "w") as f:
        #     for color in selected_colors:
        #         f.write(f"{color}\n")
        
        # # 처리된 이미지 저장 예시
        # if processed_image:
        #     processed_image.save("filtered_image.png")
    # # 색상 선택 결과 처리 콜백
    # def handle_color_selection(selected_colors, processed_image):
    #     if selected_colors:
    #         # 선택된 색상 리스트를 데이터에 저장
    #         color_hex = selected_colors[0] if selected_colors else "#000000"
    #         self.selected_color = color_hex
            
    #         # 상태 업데이트
    #         self.status_var.set(f"색상이 선택되었습니다: {color_hex}")
        
    def add_color(self, color: str):
        """지정한 색상으로 컬러 버튼을 수평 리스트에 추가"""
        btn = tk.Button(
            self.color_frame,
            bg=color,
            width=1,  # 작게
            height=1,
            relief=tk.RAISED,
            command=lambda: self.select_color(color) if hasattr(self, "select_color") else None
        )
        btn.pack(side=tk.LEFT, padx=1, pady=1)
    def Test_AddColors(self):
        self.add_color("red")
        self.add_color("green")
        self.add_color("blue")
        self.add_color("#ff00ff")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("green")
        self.add_color("blue")
        self.add_color("#ff00ff")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("green")
        self.add_color("blue")
        self.add_color("#ff00ff")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("green")
        self.add_color("blue")
        self.add_color("#ff00ff")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("green")
        self.add_color("blue")
        self.add_color("#ff00ff")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("green")
        self.add_color("blue")
        self.add_color("#ff00ff")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("green")
        self.add_color("blue")
        self.add_color("#ff00ff")
        self.add_color("#ffffff")

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def read_text_from_area(self):
        try:
            if not self.window_manager.is_window_valid():
                return
            x, y, width, height = int(self.x_var.get()), int(self.y_var.get()), int(self.width_var.get()), int(self.height_var.get())
            if width <= 0 or height <= 0:
                return
            full_window_img = self.capture_manager.capture_full_window()
            if not full_window_img:
                return
            img_width, img_height = full_window_img.size
            crop_region = (max(0, x), max(0, y), min(img_width, x + width), min(img_height, y + height))
            cropped_img = full_window_img.crop(crop_region)
            from core.ocr_engine import image_to_text
            recognized_text = image_to_text(cropped_img)
            if not recognized_text or recognized_text.strip() == "":
                recognized_text = "(인식된 텍스트 없음)\n"
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {recognized_text}")
            self.log_text.see(tk.END)
            self.status_var.set("영역에서 텍스트 읽기 완료")
        except Exception as e:
            print(f"텍스트 인식 오류: {e}")
            
    def select_capture_area(self):
        """드래그로 캡처 영역 선택"""
        # 창이 연결되어 있고 '창 내부만 선택' 옵션이 활성화된 경우에만 창 내부로 제한
        target_window_only = self.window_only_var.get() and self.window_manager.is_window_valid()
        
        if target_window_only and not self.window_manager.is_window_valid():
            messagebox.showerror("오류", "창 내부 선택을 위해서는 먼저 창에 연결해주세요.")
            return
        
        # 선택 임시 중단을 알림
        self.status_var.set("영역 선택 중... (ESC 키를 누르면 취소)")
        self.update()
        
        # 창 최소화 (선택 화면이 가려지지 않도록)
        self.withdraw()
        self.parent.iconify()
        time.sleep(0.5)  # 창이 최소화될 시간 확보
        
        # 영역 선택 시작
        self.region_selector.start_selection(
            callback=self.handle_region_selection,
            target_window_only=target_window_only
        )
        
        # 창 복원
        self.parent.deiconify()
        self.deiconify()
    
    def apply_settings(self):
        """설정 적용 및 저장"""
        try:
            # 설정값 검증
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, interval_dummy = capture_info
            # print(f"{x}, {y}, {width}, {height}")
            KEY = self.key_var.get()
            if not KEY:
                messagebox.showerror("오류", "KEY 를 입력하세요.", parent=self)
                return
 
            areas.Add_TextArea(KEY, { "x": x, "y": y, "width": width, "height": height }
                            #   , save=True
                              )
                
            # 설정 저장
            self.capture_settings = capture_info
            
            # 메인 창에 성공 메시지 표시
            self.status_var.set("캡처 영역 설정이 저장되었습니다.")
            
            messagebox.showinfo("알림", f"{KEY} 텍스트 데이터를 추가하였습니다.", parent=self)
            # 창 닫기
            self.on_close()
            
        except Exception as e:
            messagebox.showerror("설정 오류", f"설정을 적용하는 중 오류가 발생했습니다: {str(e)}", parent=self)
            
    def save_as_image(self):
        """현재 캡처된 영역을 이미지 파일로 저장"""
        try:
            # 캡처 영역 좌표 가져오기
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, _ = capture_info
            
            # 창이 유효한지 확인
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", "창이 연결되지 않았습니다.", parent=self)
                return
            
            # 전체 창 캡처
            full_window_img = self.capture_manager.capture_full_window()
            if not full_window_img:
                messagebox.showerror("오류", "창 캡처에 실패했습니다.", parent=self)
                return
            
            # 지정된 영역 추출
            img_width, img_height = full_window_img.size
            crop_region = (
                max(0, x),
                max(0, y),
                min(img_width, x + width),
                min(img_height, y + height)
            )
            
            cropped_img = full_window_img.crop(crop_region)
            
            # 저장할 기본 파일명 생성
            key = self.key_var.get().strip()
            if not key:
                # key = "capture"  # 기본 파일명
                messagebox.showerror("오류", "KEY 를 입력하세요.", parent=self)
                return
            
            # # 현재 날짜와 시간 추가
            # from datetime import datetime
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 기본 파일명
            # default_filename = f"{key}_{timestamp}.png"
            default_filename = key
            
            # 기본 저장 경로 가져오기
            from grinder_utils import finder
            default_dir = finder.Get_DataPath()
            
            # 파일 저장 다이얼로그 표시
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                initialdir=default_dir,
                initialfile=default_filename,
                defaultextension=".png",
                filetypes=[
                    ("PNG 이미지", "*.png"),
                    ("JPEG 이미지", "*.jpg;*.jpeg"),
                    ("모든 파일", "*.*")
                ],
                title="이미지 저장"
            )
            
            # 사용자가 취소를 눌렀으면 종료
            if not file_path:
                return
            
            # 이미지 저장
            cropped_img.save(file_path)
            
            # 상대 경로로 변환
            from pathlib import Path
            data_path = Path(finder.Get_DataPath())
            file_path_obj = Path(file_path)
            
            try:
                # 상대 경로 생성 시도
                relative_path = file_path_obj.relative_to(data_path)
                stored_path = str(relative_path)
            except ValueError:
                # 상대 경로 생성 실패 시 전체 경로 사용
                stored_path = file_path
            
            # 이미지 정보를 JSON에 저장
            areas.Add_ImageArea(key, {
                "x": x, "y": y, 
                "width": width, "height": height,
                "file": stored_path
            })
            
            self.status_var.set(f"이미지가 저장되었습니다: {file_path}")
            
            messagebox.showinfo("알림", f"{key} 이미지 데이터를 추가하였습니다.", parent=self)
            # 창 닫기
            self.on_close()
            
        except Exception as e:
            messagebox.showerror("이미지 저장 오류", f"이미지 저장 중 오류가 발생했습니다: {str(e)}", parent=self)
    
    def set_capture_info(self, x, y, width, height, interval):
        """캡처 정보 설정"""
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        self.interval_var.set(str(interval))
        
        # 미리보기 업데이트
        self.update_area_preview()
    
    def get_capture_info(self):
        """캡처 정보 가져오기"""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            interval = float(self.interval_var.get())
            
            if width <= 0 or height <= 0 or interval <= 0:
                raise ValueError("너비, 높이, 간격은 양수여야 합니다.")
                
            return (x, y, width, height, interval)
        except ValueError as e:
            messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}", parent=self)
            return None
    
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
                messagebox.showerror("오류", ERROR_NO_WINDOW, parent=self)
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
                messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}", parent=self)
                return
            
            # 전체 창 캡처
            full_window_img = self.capture_manager.capture_full_window()
            if not full_window_img:
                messagebox.showerror("오류", "창 캡처에 실패했습니다.", parent=self)
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
                        parent=self
                    )
                
                # 캔버스 크기 가져오기
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                # 이미지 크기 계산에 너무 작은 값이 사용되지 않도록 제한
                if canvas_width < 50:
                    canvas_width = 300
                if canvas_height < 50:
                    canvas_height = 200
                    
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
                self.preview_canvas.delete("all")
                
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
                messagebox.showerror("미리보기 오류", f"미리보기 생성 중 오류: {str(e)}", parent=self)
        except Exception as e:
            messagebox.showerror("미리보기 오류", f"미리보기 생성 중 오류: {str(e)}", parent=self)
    
    def on_close(self):
        self.reading_text = False
        if self.on_close_callback:
            # self.on_close_callback(self.capture_settings)
            self.on_close_callback(None)
        self.destroy()
