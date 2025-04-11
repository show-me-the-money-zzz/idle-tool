import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageGrab
import cv2
import numpy as np
import sys

class ColorPickerPopup(tk.Toplevel):
    """색상 선택 팝업 창"""
    
    def __init__(self, parent, image_path, callback=None):
        super().__init__(parent)
        self.title("색상 추출")
        self.geometry("800x700")
        self.transient(parent)
        self.grab_set()  # 모달 창으로 설정
        
        self.parent = parent
        self.callback = callback
        self.original_image = Image.open(image_path)
        self.processed_image = self.original_image.copy()
        
        # 상태 변수
        self.is_picking = False  # 색상 추출 모드 상태
        self.selected_colors = []  # 선택된 색상 목록
        self.zoom_factor = 1.0    # 확대/축소 비율
        self.image_position = [0, 0]  # 이미지 드래그 위치
        self.drag_start = None    # 드래그 시작 위치
        
        # UI 컴포넌트
        self._setup_ui()
        
        # 키 이벤트 바인딩
        self.bind("<Escape>", self.cancel_picking)
        self.bind("<Configure>", self.on_resize)
        
        # 처음 이미지 로드
        self.update_top_image()
        self.update_bottom_image()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 스포이드 버튼 (왼쪽)
        # 실제 앱에서는 이미지로 대체할 것
        self.eyedropper_btn = ttk.Button(
            control_frame, 
            text="🔍", 
            width=3,
            command=self.toggle_picking_mode
        )
        self.eyedropper_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 색상 팔레트 프레임 (중앙)
        palette_frame = ttk.Frame(control_frame)
        palette_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 색상 스크롤 영역
        palette_canvas = tk.Canvas(palette_frame, height=30, highlightthickness=0)
        palette_canvas.pack(side=tk.TOP, fill=tk.X)
        
        scrollbar = ttk.Scrollbar(palette_frame, orient=tk.HORIZONTAL, command=palette_canvas.xview)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        palette_canvas.configure(xscrollcommand=scrollbar.set)
        
        self.color_frame = ttk.Frame(palette_canvas)
        self.color_window = palette_canvas.create_window((0, 0), window=self.color_frame, anchor=tk.NW)
        
        # 스크롤 영역 자동 조정
        def update_scroll_region(event=None):
            palette_canvas.configure(scrollregion=palette_canvas.bbox("all"))
            palette_canvas.itemconfig(self.color_window, width=palette_canvas.winfo_width())
        
        self.color_frame.bind("<Configure>", update_scroll_region)
        palette_canvas.bind("<Configure>", lambda e: palette_canvas.itemconfig(
            self.color_window, width=palette_canvas.winfo_width()))
        
        # 상태 레이블 (Esc 키 안내)
        self.status_label = ttk.Label(control_frame, text="Esc 키 OFF")
        self.status_label.pack(side=tk.RIGHT)
        
        # 상단 이미지 프레임
        top_image_frame = ttk.Frame(main_frame)
        top_image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 좌측 확대/축소 컨트롤
        zoom_control = ttk.Frame(top_image_frame)
        zoom_control.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.zoom_in_btn = ttk.Button(zoom_control, text="+", width=2, command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.TOP, pady=(0, 2))
        
        self.zoom_var = tk.StringVar(value="1.0")
        zoom_entry = ttk.Entry(zoom_control, textvariable=self.zoom_var, width=4)
        zoom_entry.pack(side=tk.TOP, pady=2)
        zoom_entry.bind("<Return>", self.update_zoom_from_entry)
        zoom_entry.bind("<FocusOut>", self.update_zoom_from_entry)
        
        self.zoom_out_btn = ttk.Button(zoom_control, text="-", width=2, command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.TOP, pady=(2, 0))
        
        # 상단 이미지 캔버스
        self.top_canvas = tk.Canvas(top_image_frame, bg="lightgray", highlightthickness=1, highlightbackground="gray")
        self.top_canvas.pack(fill=tk.BOTH, expand=True)
        self.top_canvas.bind("<Button-1>", self.on_canvas_click)
        self.top_canvas.bind("<ButtonPress-1>", self.start_drag)
        self.top_canvas.bind("<B1-Motion>", self.drag_image)
        self.top_canvas.bind("<ButtonRelease-1>", self.stop_drag)
        
        # 안내 메시지
        self.info_label = ttk.Label(main_frame, text="색상을 선택하려면 스포이드 버튼을 클릭한 후 이미지를 클릭하세요. 색상 박스를 클릭하면 삭제됩니다.")
        self.info_label.pack(fill=tk.X, pady=(0, 10))
        
        # 하단 이미지 캔버스
        self.bottom_canvas = tk.Canvas(main_frame, bg="lightgray", highlightthickness=1, highlightbackground="gray")
        self.bottom_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="적용", command=self.apply).pack(side=tk.RIGHT)
    
    def toggle_picking_mode(self):
        """색상 추출 모드 토글"""
        self.is_picking = not self.is_picking
        if self.is_picking:
            self.status_label.config(text="Esc 키 ON")
            self.eyedropper_btn.config(style="Accent.TButton")  # 강조 스타일 적용 (ttk 테마에 따라 다름)
            self.top_canvas.config(cursor="crosshair")  # 십자 커서로 변경
        else:
            self.status_label.config(text="Esc 키 OFF")
            self.eyedropper_btn.config(style="")  # 기본 스타일로 복원
            self.top_canvas.config(cursor="")  # 기본 커서로 복원
    
    def cancel_picking(self, event=None):
        """Esc 키를 눌러 색상 추출 모드 취소"""
        if self.is_picking:
            self.is_picking = False
            self.status_label.config(text="Esc 키 OFF")
            self.eyedropper_btn.config(style="")
            self.top_canvas.config(cursor="")
    
    def on_canvas_click(self, event):
        """캔버스 클릭 이벤트 처리"""
        if self.is_picking:
            # 클릭한 위치의 픽셀 색상 가져오기
            x, y = self.get_image_coordinates(event.x, event.y)
            
            if 0 <= x < self.original_image.width and 0 <= y < self.original_image.height:
                color = self.original_image.getpixel((x, y))
                
                # RGB 형식으로 변환
                if isinstance(color, int):  # 그레이스케일
                    hex_color = f"#{color:02x}{color:02x}{color:02x}"
                elif len(color) >= 3:  # RGB 또는 RGBA
                    hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                else:
                    return
                
                # 색상 추가
                self.add_color(hex_color)
                
                # 하단 이미지 업데이트
                self.update_bottom_image()
    
    def get_image_coordinates(self, canvas_x, canvas_y):
        """캔버스 좌표를 이미지 좌표로 변환"""
        # 확대/축소 및 위치 오프셋 고려
        image_x = int((canvas_x - self.image_position[0]) / self.zoom_factor)
        image_y = int((canvas_y - self.image_position[1]) / self.zoom_factor)
        return image_x, image_y
    
    def add_color(self, color_hex):
        """색상 팔레트에 색상 추가"""
        if color_hex in self.selected_colors:
            return  # 이미 있는 색상이면 추가하지 않음
        
        # 색상을 목록에 추가
        self.selected_colors.append(color_hex)
        
        # 색상 버튼 생성
        color_btn = tk.Button(
            self.color_frame,
            bg=color_hex,
            width=3, height=1,
            bd=1, relief=tk.RAISED,
            command=lambda c=color_hex: self.remove_color(c)
        )
        color_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 버튼에 색상 정보 저장
        color_btn.color = color_hex
    
    def remove_color(self, color_hex):
        """색상 팔레트에서 색상 제거"""
        if color_hex in self.selected_colors:
            self.selected_colors.remove(color_hex)
            
            # 해당 색상 버튼 제거
            for child in self.color_frame.winfo_children():
                if hasattr(child, 'color') and child.color == color_hex:
                    child.destroy()
                    break
            
            # 하단 이미지 업데이트
            self.update_bottom_image()
    
    def update_top_image(self):
        """상단 이미지 캔버스 업데이트"""
        if not hasattr(self, 'original_image'):
            return
        
        # 캔버스 크기 가져오기
        canvas_width = self.top_canvas.winfo_width()
        canvas_height = self.top_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # 아직 캔버스가 렌더링되지 않은 경우
            self.top_canvas.after(100, self.update_top_image)
            return
        
        # 원본 이미지 리사이징 (확대/축소 비율 적용)
        img_width = int(self.original_image.width * self.zoom_factor)
        img_height = int(self.original_image.height * self.zoom_factor)
        resized_img = self.original_image.resize((img_width, img_height), Image.LANCZOS)
        
        # 이미지를 캔버스에 표시
        self.top_photo = ImageTk.PhotoImage(resized_img)
        
        # 이전 이미지 삭제하고 새 이미지 표시
        self.top_canvas.delete("all")
        self.top_canvas.create_image(
            self.image_position[0], self.image_position[1],
            image=self.top_photo,
            anchor=tk.NW,
            tags=("image",)
        )
    
    def update_bottom_image(self):
        """하단 이미지 캔버스 업데이트 (선택된 색상만 표시)"""
        if not hasattr(self, 'original_image') or not self.selected_colors:
            # 선택된 색상이 없으면 빈 이미지 표시
            self.bottom_canvas.delete("all")
            self.bottom_canvas.create_text(
                self.bottom_canvas.winfo_width() // 2,
                self.bottom_canvas.winfo_height() // 2,
                text="영역을 선택하면\n미리보기가 표시됩니다",
                fill="darkgray",
                justify=tk.CENTER
            )
            return
        
        # 원본 이미지를 NumPy 배열로 변환
        img_array = np.array(self.original_image)
        
        # 마스크 초기화 (모든 픽셀 검은색)
        mask = np.zeros_like(img_array)
        
        # 선택된 각 색상에 대해 마스크 업데이트
        for color_hex in self.selected_colors:
            # 16진수 색상을 RGB로 변환
            r = int(color_hex[1:3], 16)
            g = int(color_hex[3:5], 16)
            b = int(color_hex[5:7], 16)
            
            # 색상 임계값 설정 (유사한 색상도 포함)
            threshold = 10
            color_mask = (
                (np.abs(img_array[:,:,0] - r) <= threshold) &
                (np.abs(img_array[:,:,1] - g) <= threshold) &
                (np.abs(img_array[:,:,2] - b) <= threshold)
            )
            
            # 마스크 업데이트 (해당 색상 부분만 원본 이미지 값 사용)
            mask[color_mask] = img_array[color_mask]
        
        # NumPy 배열을 PIL Image로 변환
        processed_img = Image.fromarray(mask)
        self.processed_image = processed_img
        
        # 캔버스 크기 가져오기
        canvas_width = self.bottom_canvas.winfo_width()
        canvas_height = self.bottom_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # 아직 캔버스가 렌더링되지 않은 경우
            self.bottom_canvas.after(100, self.update_bottom_image)
            return
        
        # 이미지 리사이징 (1:1 비율 유지하며 캔버스에 맞추기)
        img_width, img_height = processed_img.size
        scale = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        resized_img = processed_img.resize((new_width, new_height), Image.LANCZOS)
        
        # 이미지를 캔버스에 표시
        self.bottom_photo = ImageTk.PhotoImage(resized_img)
        
        # 이전 이미지 삭제하고 새 이미지 표시
        self.bottom_canvas.delete("all")
        
        # 이미지 중앙 배치
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        self.bottom_canvas.create_image(x, y, image=self.bottom_photo, anchor=tk.NW)
    
    def zoom_in(self):
        """확대 (+0.5)"""
        self.zoom_factor += 0.5
        self.zoom_var.set(f"{self.zoom_factor:.1f}")
        self.update_top_image()
    
    def zoom_out(self):
        """축소 (-0.5)"""
        if self.zoom_factor > 0.5:
            self.zoom_factor -= 0.5
            self.zoom_var.set(f"{self.zoom_factor:.1f}")
            self.update_top_image()
    
    def update_zoom_from_entry(self, event=None):
        """입력 필드에서 확대/축소 값 업데이트"""
        try:
            value = float(self.zoom_var.get())
            if value >= 0.5:  # 최소 0.5 이상
                self.zoom_factor = value
                self.update_top_image()
            else:
                self.zoom_var.set(f"{self.zoom_factor:.1f}")  # 원래 값으로 복원
        except ValueError:
            self.zoom_var.set(f"{self.zoom_factor:.1f}")  # 숫자가 아닌 경우 원래 값으로 복원
    
    def start_drag(self, event):
        """이미지 드래그 시작"""
        if not self.is_picking:  # 색상 추출 모드가 아닐 때만 드래그 가능
            self.drag_start = (event.x, event.y)
    
    def drag_image(self, event):
        """이미지 드래그 중"""
        if self.drag_start and not self.is_picking:
            # 드래그 거리 계산
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            
            # 이미지 위치 업데이트
            self.image_position[0] += dx
            self.image_position[1] += dy
            
            # 드래그 시작점 업데이트
            self.drag_start = (event.x, event.y)
            
            # 이미지 위치 업데이트
            self.update_top_image()
    
    def stop_drag(self, event):
        """이미지 드래그 종료"""
        self.drag_start = None
    
    def on_resize(self, event=None):
        """창 크기 변경 시 이미지 업데이트"""
        # 창 크기가 변경될 때 이미지 업데이트
        self.update_top_image()
        self.update_bottom_image()
    
    def cancel(self):
        """취소 버튼 클릭 처리"""
        self.destroy()
    
    def apply(self):
        """적용 버튼 클릭 처리"""
        # 콜백 함수 호출
        if self.callback:
            self.callback(self.selected_colors, self.processed_image)
        
        self.destroy()