import tkinter as tk
from tkinter import messagebox, ttk
import time
from PIL import Image, ImageTk

from zzz.config import *

class CaptureAreaFrame(ttk.LabelFrame):
    """캡처 영역 설정 프레임"""
    
    def __init__(self, parent, window_manager, region_selector, capture_manager, status_var):
        super().__init__(parent, text="캡처 영역 설정 (창 내부 좌표)", padding="10")
        
        self.window_manager = window_manager
        self.region_selector = region_selector
        self.capture_manager = capture_manager
        self.status_var = status_var
        
        # 미리보기 이미지 저장 변수
        self.preview_image = None
        self.preview_photo = None
        self.preview_image_id = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # 왼쪽(설정) 및 오른쪽(미리보기) 영역을 나누기 위한 프레임
        main_frame = ttk.Frame(self)
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
        self.winfo_toplevel().iconify()
        time.sleep(0.5)  # 창이 최소화될 시간 확보
        
        # 영역 선택 시작
        self.region_selector.start_selection(
            callback=self.handle_region_selection,
            target_window_only=target_window_only
        )
        
        # 창 복원
        self.winfo_toplevel().deiconify()
    
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
                        parent=self.winfo_toplevel()
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
                messagebox.showerror("미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
        except Exception as e:
            messagebox.showerror("미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
    
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
            messagebox.showerror("입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            return None