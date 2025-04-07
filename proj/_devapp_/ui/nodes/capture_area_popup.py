import tkinter as tk
from tkinter import messagebox, ttk
import time
from PIL import Image, ImageTk
from datetime import datetime

from zzz.config import *

class CaptureAreaPopup(tk.Toplevel):
    """캡처 영역 설정 팝업 창"""
    
    def __init__(self, parent, window_manager, region_selector, capture_manager, status_var, on_close_callback=None):
        super().__init__(parent)
        
        # 기본 창 설정
        self.title("캡처 영역 설정")
        self.geometry("700x500")  # 크기 증가
        
        # 상위 창보다 항상 위에 표시
        self.transient(parent)
        
        # 팝업 종료 시 콜백함수
        self.on_close_callback = on_close_callback
        
        # 창이 닫힐 때 이벤트 처리
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 필요한 객체 참조 저장
        self.parent = parent
        self.window_manager = window_manager
        self.region_selector = region_selector
        self.capture_manager = capture_manager
        self.status_var = status_var
        
        # 미리보기 이미지 저장 변수
        self.preview_image = None
        self.preview_photo = None
        self.preview_image_id = None
        
        # 설정된 값 저장 변수
        self.capture_settings = None
        
        # UI 구성요소 초기화
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # 상단 프레임 (설정 영역)
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X)
        
        # 좌측 설정 프레임
        settings_frame = ttk.Frame(top_frame)
        settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # 좌표 설정 그룹
        coords_frame = ttk.LabelFrame(settings_frame, text="위치 및 크기", padding="10")
        coords_frame.pack(fill=tk.X, pady=5)
        
        # X 좌표 (상대적)
        ttk.Label(coords_frame, text="X 좌표:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_var = tk.StringVar(value=DEFAULT_CAPTURE_X)
        ttk.Entry(coords_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Y 좌표 (상대적)
        ttk.Label(coords_frame, text="Y 좌표:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.y_var = tk.StringVar(value=DEFAULT_CAPTURE_Y)
        ttk.Entry(coords_frame, textvariable=self.y_var, width=10).grid(row=0, column=3, sticky=tk.W, pady=2)
        
        # 너비
        ttk.Label(coords_frame, text="너비:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.StringVar(value=DEFAULT_CAPTURE_WIDTH)
        ttk.Entry(coords_frame, textvariable=self.width_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 높이
        ttk.Label(coords_frame, text="높이:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.height_var = tk.StringVar(value=DEFAULT_CAPTURE_HEIGHT)
        ttk.Entry(coords_frame, textvariable=self.height_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=2)
        
        # 캡처 간격 설정
        ttk.Label(coords_frame, text="캡처 간격(초):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar(value=DEFAULT_CAPTURE_INTERVAL)
        ttk.Entry(coords_frame, textvariable=self.interval_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 창 내 영역만 선택 체크박스
        self.window_only_var = tk.BooleanVar(value=True)
        window_only_check = ttk.Checkbutton(
            coords_frame, 
            text="창 내부만 선택", 
            variable=self.window_only_var
        )
        window_only_check.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=2)
        
        # 버튼 그룹 프레임
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        # 영역 선택 버튼
        select_area_btn = ttk.Button(buttons_frame, text="드래그로 영역 선택", command=self.select_capture_area)
        select_area_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # 미리보기 업데이트 버튼
        update_btn = ttk.Button(buttons_frame, text="미리보기 갱신", command=self.update_area_preview)
        update_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # 글자 읽기 버튼
        read_text_btn = ttk.Button(buttons_frame, text="글자 읽기", command=self.read_text_from_area)
        read_text_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # 설정 적용 및 저장 버튼 프레임
        action_buttons_frame = ttk.Frame(settings_frame)
        action_buttons_frame.pack(fill=tk.X, pady=5)
        
        apply_btn = ttk.Button(action_buttons_frame, text="적용", command=self.apply_settings)
        apply_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        cancel_btn = ttk.Button(action_buttons_frame, text="취소", command=self.on_close)
        cancel_btn.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # 우측 미리보기 프레임
        preview_frame = ttk.LabelFrame(top_frame, text="영역 미리보기")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 미리보기 캔버스 (이미지 표시용)
        self.preview_canvas = tk.Canvas(preview_frame, width=300, height=200, bg='lightgray')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 미리보기 없음 텍스트
        self.preview_canvas.create_text(
            150, 100, 
            text="영역을 선택하면\n미리보기가 표시됩니다", 
            fill="darkgray", 
            justify=tk.CENTER
        )
        
        # 하단 로그 프레임 (OCR 결과 표시)
        log_frame = ttk.LabelFrame(self, text="인식된 텍스트", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 로그 텍스트 영역 및 스크롤바
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(text_frame, wrap=tk.WORD, height=8)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 로그 컨트롤 프레임
        log_ctrl_frame = ttk.Frame(log_frame)
        log_ctrl_frame.pack(fill=tk.X, pady=5)
        
        # 로그 초기화 버튼
        clear_log_btn = ttk.Button(log_ctrl_frame, text="로그 초기화", command=self.clear_log)
        clear_log_btn.pack(side=tk.RIGHT)
    
    def clear_log(self):
        """로그 초기화"""
        self.log_text.delete(1.0, tk.END)
    
    def read_text_from_area(self):
        """현재 설정된 영역에서 텍스트 읽기"""
        try:
            if not self.window_manager.is_window_valid():
                messagebox.showerror("오류", "먼저 창에 연결해주세요.", parent=self)
                return
                
            # 현재 설정된 영역 좌표 가져오기
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
                
            # 지정된 영역 추출
            img_width, img_height = full_window_img.size
            crop_region = (
                max(0, x),
                max(0, y),
                min(img_width, x + width),
                min(img_height, y + height)
            )
            
            cropped_img = full_window_img.crop(crop_region)
            
            # OCR로 텍스트 인식
            from core.ocr_engine import image_to_text
            recognized_text = image_to_text(cropped_img)
            
            # 인식된 텍스트가 없을 경우
            if not recognized_text or recognized_text.strip() == "":
                recognized_text = "(인식된 텍스트 없음)\n"
            
            # 타임스탬프 추가
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # 로그에 텍스트 추가
            self.log_text.insert(tk.END, f"[{timestamp}] {recognized_text}")
            self.log_text.see(tk.END)  # 스크롤 맨 아래로
            
            # 상태 업데이트
            self.status_var.set(f"영역에서 텍스트 읽기 완료")
            
        except Exception as e:
            messagebox.showerror("텍스트 인식 오류", f"텍스트 인식 중 오류가 발생했습니다: {str(e)}", parent=self)
            
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
                
            # 설정 저장
            self.capture_settings = capture_info
            
            # 메인 창에 성공 메시지 표시
            self.status_var.set("캡처 영역 설정이 저장되었습니다.")
            
            # 창 닫기
            self.on_close()
            
        except Exception as e:
            messagebox.showerror("설정 오류", f"설정을 적용하는 중 오류가 발생했습니다: {str(e)}", parent=self)
    
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
        """창이 닫힐 때 처리"""
        # 콜백 함수가 있으면 호출
        if self.on_close_callback:
            self.on_close_callback(self.capture_settings)
        
        # 창 닫기
        self.destroy()