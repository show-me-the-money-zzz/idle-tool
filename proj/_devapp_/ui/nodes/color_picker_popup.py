import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import numpy as np
import os

from zzz.config import COLOR_EXTRACT_MODE_SWAP_KEY

class ColorPickerPopup(tk.Toplevel):
    """색상 선택 팝업 창"""
    
    PIPETTE_OFF_TEXT = "💉"
    PIPETTE_OFF_COLOR_BG = "#f0f0f0"
    PIPETTE_OFF_COLOR_TEXT = "black"
    PIPETTE_ON_TEXT = "💢"
    PIPETTE_ON_COLOR_BG = "#ff6347"
    PIPETTE_ON_COLOR_TEXT = "white"
    
    DEFAULT_ZOOM = 1.5

    def __init__(self, parent, image, callback=None):
        super().__init__(parent)
        self.title("색상 추출")
        self.geometry("900x800")  # 창 크기를 900x800으로 변경
        self.transient(parent)
        self.grab_set()  # 모달 창으로 설정
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.parent = parent
        self.callback = callback
        
        self.parent = parent
        self.callback = callback

        # 이미지 로드 (PIL Image 직접 사용)
        if isinstance(image, str):
            # 파일 경로인 경우
            if os.path.exists(image):
                self.original_image = Image.open(image)
            else:
                messagebox.showerror("오류", "이미지 파일을 찾을 수 없습니다.")
                self.destroy()
                return
        elif isinstance(image, Image.Image):
            # PIL Image 객체인 경우
            self.original_image = image.copy()
        else:
            messagebox.showerror("오류", "지원되지 않는 이미지 형식입니다.")
            self.destroy()
            return

        self.processed_image = self.original_image.copy()

        # 상태 변수
        self.is_picking = False  # 색상 추출 모드 상태
        self.selected_colors = []  # 선택된 색상 목록
        self.zoom_factor = ColorPickerPopup.DEFAULT_ZOOM    # 확대/축소 비율
        self.image_position = [0, 0]  # 이미지 드래그 위치
        self.drag_start = None    # 드래그 시작 위치
        self.show_grid = False     # 그리드 표시 여부

        # UI 컴포넌트
        self._setup_ui()

        # 키 이벤트 바인딩
        self.bind("<Configure>", self.on_resize)
        # Z 키를 바인딩하여 색상 추출 모드 토글 (전체 창에 바인딩)
        self.bind_all(f"<{COLOR_EXTRACT_MODE_SWAP_KEY}>", self.toggle_picking_mode_key)
        self.bind_all(f"<{COLOR_EXTRACT_MODE_SWAP_KEY.lower()}>", self.toggle_picking_mode_key)

        # 처음 이미지 로드
        self.update_top_image()
        self.update_bottom_image()

        # # 스타일 정의 (init 메서드에 추가)
        # style = ttk.Style()
        # style.configure("Bold.TCheckbutton", font=("TkDefaultFont", 9, "bold"))
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 스포이드 버튼 (왼쪽) - 기본 tk.Button 사용하여 색상 지정
        self.eyedropper_btn = tk.Button(
            control_frame, 
            text=ColorPickerPopup.PIPETTE_OFF_TEXT,  # 기본 상태: 주사기 아이콘
            width=2,    # 버튼 너비
            bg=ColorPickerPopup.PIPETTE_OFF_COLOR_BG,  # 기본 배경색
            fg=ColorPickerPopup.PIPETTE_OFF_COLOR_TEXT,    # 기본 글자색
            command=self.toggle_picking_mode
        )
        self.eyedropper_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 색상 팔레트 프레임 (중앙)
        palette_frame = ttk.Frame(control_frame)
        palette_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 색상 스크롤 영역
        self.palette_canvas = tk.Canvas(palette_frame, height=30, highlightthickness=0)
        self.palette_canvas.pack(side=tk.TOP, fill=tk.X)
        
        scrollbar = ttk.Scrollbar(palette_frame, orient=tk.HORIZONTAL, command=self.palette_canvas.xview)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.palette_canvas.configure(xscrollcommand=scrollbar.set)
        
        self.color_frame = ttk.Frame(self.palette_canvas)
        self.color_window = self.palette_canvas.create_window((0, 0), window=self.color_frame, anchor=tk.NW)
        
        # 스크롤 영역 자동 조정
        def update_scroll_region(event=None):
            self.palette_canvas.configure(scrollregion=self.palette_canvas.bbox("all"))
            self.palette_canvas.itemconfig(self.color_window, width=self.palette_canvas.winfo_width())
        
        self.color_frame.bind("<Configure>", update_scroll_region)
        self.palette_canvas.bind("<Configure>", lambda e: self.palette_canvas.itemconfig(
            self.color_window, width=self.palette_canvas.winfo_width()))
        
        # "Esc 키 OFF" 레이블 제거됨
        
        # 상단 이미지 프레임
        top_image_frame = ttk.Frame(main_frame)
        top_image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 좌측 확대/축소 컨트롤
        zoom_control = ttk.Frame(top_image_frame)
        zoom_control.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Entry 대신 Spinbox로 변경
        ttk.Label(zoom_control, text="확대율").pack(side=tk.TOP, pady=(0, 2))
        self.zoom_var = tk.StringVar(value=str(ColorPickerPopup.DEFAULT_ZOOM))
        
        # Spinbox 설정
        self.zoom_spinbox = ttk.Spinbox(
            zoom_control, 
            textvariable=self.zoom_var, 
            width=4, 
            from_=1.0,
            to=10.0, 
            increment=0.5,
            command=self.update_zoom_from_spinbox
        )
        self.zoom_spinbox.pack(side=tk.TOP, pady=2)
        self.zoom_spinbox.bind("<Return>", self.update_zoom_from_spinbox)
        self.zoom_spinbox.bind("<FocusOut>", self.update_zoom_from_spinbox)
        
        # 그리드 표시 체크박스. 선 굵기 때문에 x1 에서는 이미지가 다 덮여서 안 보임
        self.grid_var = tk.BooleanVar(value=False)
        grid_check = ttk.Checkbutton(
            zoom_control, 
            text="Grid", 
            variable=self.grid_var,
            command=self.toggle_grid,
            style="Bold.TCheckbutton"
        )
        grid_check.pack(side=tk.TOP, pady=(10, 5))

        # 이미지 초기 위치로 리셋 버튼
        reset_pos_btn = tk.Button(
            zoom_control,
            text="📌",
            width=2,
            command=self.reset_image_position,
            bg="#f0f0f0",
            fg="black"
        )
        reset_pos_btn.pack(side=tk.TOP, pady=(0, 5))
        
        # 상단 이미지 캔버스
        self.top_canvas = tk.Canvas(top_image_frame, bg="lightgray", highlightthickness=1, highlightbackground="gray")
        self.top_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 캔버스 이벤트 바인딩
        self.top_canvas.bind("<Button-1>", self.on_canvas_click)
        self.top_canvas.bind("<ButtonPress-1>", self.start_drag)
        self.top_canvas.bind("<B1-Motion>", self.drag_image)
        self.top_canvas.bind("<ButtonRelease-1>", self.stop_drag)
        
        # 안내 메시지 - 여러 줄로 나누어 표시하여 잘리지 않게 함
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = f"<{COLOR_EXTRACT_MODE_SWAP_KEY}> 키로 모드를 변경할 수 있습니다. 그리드는 1.5 이상부터 보입니다.\n이미지 드래그는 모드 OFF 에만 가능합니다. 드래그 한 이미지의 위치를 초기화 하려면 📌 버튼을 누르세요."
        self.info_label = ttk.Label(info_frame, text=info_text, wraplength=850)
        self.info_label.pack(fill=tk.X)
        
        # Spinbox에 Z 키가 입력되지 않도록 추가 바인딩
        self.zoom_spinbox.bind("<Key>", self.filter_spinbox_key)
        
        # 하단 이미지 캔버스
        self.bottom_canvas = tk.Canvas(main_frame, bg="lightgray", highlightthickness=1, highlightbackground="gray")
        self.bottom_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="적용", command=self.apply).pack(side=tk.RIGHT)
    
    def toggle_picking_mode_key(self, event=None):
        """Z 키로 색상 추출 모드 토글"""
        # 이벤트가 Spinbox에서 발생했으면 무시 (Spinbox에 Z가 입력되지 않도록)
        if event and event.widget == self.zoom_spinbox:
            return "break"
        self.toggle_picking_mode()
        return "break"  # 이벤트 전파 중지
    
    def toggle_picking_mode(self):
        """색상 추출 모드 토글"""
        self.is_picking = not self.is_picking
        if self.is_picking:
            self.eyedropper_btn.config(
                text=ColorPickerPopup.PIPETTE_ON_TEXT,
                bg=ColorPickerPopup.PIPETTE_ON_COLOR_BG,
                fg=ColorPickerPopup.PIPETTE_ON_COLOR_TEXT
            )
            self.top_canvas.config(cursor="crosshair")  # 십자 커서로 변경
        else:
            self.eyedropper_btn.config(
                text=ColorPickerPopup.PIPETTE_OFF_TEXT,
                bg=ColorPickerPopup.PIPETTE_OFF_COLOR_BG,
                fg=ColorPickerPopup.PIPETTE_OFF_COLOR_TEXT
            )
            self.top_canvas.config(cursor="")  # 기본 커서로 복원
    
    def toggle_grid(self):
        """그리드 표시 토글"""
        self.show_grid = self.grid_var.get()
        self.update_top_image()

    # Esc 키로 모드 해제 기능 삭제
    
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
                
                # 자동으로 색상 추출 모드 해제
                self.is_picking = False
                self.eyedropper_btn.config(
                    text=ColorPickerPopup.PIPETTE_OFF_TEXT,
                    bg=ColorPickerPopup.PIPETTE_OFF_COLOR_BG,
                    fg=ColorPickerPopup.PIPETTE_OFF_COLOR_TEXT
                )
                self.top_canvas.config(cursor="")
    
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
        
        # 컬러 정보 표시
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        color_info = ttk.Label(self.color_frame, text=f"RGB({r},{g},{b})")
        color_info.pack(side=tk.LEFT, padx=(0, 10))
    
    def remove_color(self, color_hex):
        """색상 팔레트에서 색상 제거"""
        if color_hex in self.selected_colors:
            self.selected_colors.remove(color_hex)
            
            # 해당 색상 버튼과 라벨 제거
            to_remove = []
            found_btn = False
            
            for child in self.color_frame.winfo_children():
                if hasattr(child, 'color') and child.color == color_hex:
                    to_remove.append(child)
                    found_btn = True
                elif found_btn and isinstance(child, ttk.Label):
                    to_remove.append(child)
                    found_btn = False
            
            for widget in to_remove:
                widget.destroy()
            
            # 하단 이미지 업데이트
            self.update_bottom_image()
    
    def update_top_image(self):
        """상단 이미지 캔버스 업데이트 (픽셀 확대 지원)"""
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
        
        # 픽셀 단위로 확대하기 위해 새 이미지 생성
        resized_img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(resized_img)
        
        # 원본 이미지의 각 픽셀을 확대하여 그리기
        for y in range(self.original_image.height):
            for x in range(self.original_image.width):
                # 원본 픽셀 색상 가져오기
                pixel = self.original_image.getpixel((x, y))
                
                # RGB 또는 RGBA 포맷 처리
                if isinstance(pixel, int):  # 그레이스케일
                    color = (pixel, pixel, pixel)
                elif len(pixel) >= 3:  # RGB 또는 RGBA
                    color = pixel[:3]
                else:
                    color = (0, 0, 0)  # 기본값
                
                # 확대된 픽셀 좌표 계산
                x1 = int(x * self.zoom_factor)
                y1 = int(y * self.zoom_factor)
                x2 = int((x + 1) * self.zoom_factor)
                y2 = int((y + 1) * self.zoom_factor)
                
                # 픽셀 그리기
                draw.rectangle([x1, y1, x2-1, y2-1], fill=color)
        
        if self.show_grid and self.zoom_factor >= 1.5:
            grid_color = (100, 100, 100)
            grid_width = max(1, int(self.zoom_factor / 10))  # 확대율에 따라 선 굵기만 유동

            for y in range(self.original_image.height + 1):
                y_pos = int(y * self.zoom_factor)
                draw.line([(0, y_pos), (img_width, y_pos)], fill=grid_color, width=grid_width)

            for x in range(self.original_image.width + 1):
                x_pos = int(x * self.zoom_factor)
                draw.line([(x_pos, 0), (x_pos, img_height)], fill=grid_color, width=grid_width)
        
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
        
        # 확대 비율 업데이트
        self.zoom_var.set(f"{self.zoom_factor:.1f}")
    
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

    def reset_image_position(self):
        """이미지 위치를 초기 상태로 리셋"""
        self.image_position = [0, 0]
        self.update_top_image()

    def update_zoom_from_spinbox(self, event=None):
        """Spinbox에서 확대/축소 값 업데이트"""
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
    
    def filter_spinbox_key(self, event):
        """Spinbox에 특정 키 입력 필터링"""
        if event.char.lower() == COLOR_EXTRACT_MODE_SWAP_KEY.lower():
            self.toggle_picking_mode()
            return "break"
        return None
        
    def apply(self):
        """적용 버튼 클릭 처리"""
        # 콜백 함수 호출
        if self.callback:
            self.callback(self.selected_colors, self.processed_image)
        
        self.destroy()