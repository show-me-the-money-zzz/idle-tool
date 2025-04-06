import tkinter as tk
import pyautogui
import win32gui
import time
from PIL import Image, ImageTk
import numpy as np
import mss
import mss.tools
import keyboard  # 키보드 입력 감지를 위한 모듈
from zzz.config import *  # 설정 상수 불러오기

class RegionSelector:
    """마우스 드래그로 영역을 선택하는 도구"""
    
    def __init__(self, window_manager=None):
        self.window_manager = window_manager
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.rect_id = None
        self.selected_region = None
        self.callback = None
        self.screenshot = None
        self.target_window_only = False
        self.window_rect = (0, 0, 0, 0)
        
        # 고정 치수 관련 변수
        self.fixed_width = None
        self.fixed_height = None
        self.fixed_aspect_ratio = None
        
        # 확대 뷰 관련 변수
        self.zoom_window = None
        self.zoom_canvas = None
        self.zoom_factor = DRAG_ZOOM_FACTOR  # 확대 배율
        self.zoom_size = 150  # 확대 창 크기
        
        # 키 제어 안내 레이블
        self.info_label = None
    
    def start_selection(self, callback=None, target_window_only=False):
        """영역 선택 시작"""
        self.callback = callback
        self.target_window_only = target_window_only
        
        # 새 tkinter 창 생성 (메인 루트 창이 아닌 Toplevel 사용)
        self.root = tk.Toplevel()
        self.root.withdraw()  # 임시로 숨김
        self.root.title("Region Selector - " + str(id(self)))  # 고유한 제목 사용
        
        # mss 인스턴스 생성
        with mss.mss() as sct:
            # 타겟 윈도우가 있고, 해당 윈도우만 캡처하는 모드라면
            if target_window_only and self.window_manager and self.window_manager.is_window_valid():
                # 창 위치 가져오기
                self.window_rect = self.window_manager.get_window_rect()
                left, top, right, bottom = self.window_rect
                width = right - left
                height = bottom - top
                
                # 전체 화면 스크린샷 (mss 사용)
                monitor = {"top": top, "left": left, "width": width, "height": height}
                sct_img = sct.grab(monitor)
                self.screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            else:
                # 전체 화면 스크린샷 (mss 사용)
                sct_img = sct.grab(sct.monitors[0])
                self.screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                self.window_rect = (0, 0, self.screenshot.width, self.screenshot.height)
        
        # 크기 설정
        if target_window_only and self.window_manager and self.window_manager.is_window_valid():
            left, top, right, bottom = self.window_rect
            width = right - left
            height = bottom - top
            self.root.geometry(f"{width}x{height}+{left}+{top}")
        else:
            # 전체 화면 크기로 설정
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 창 설정
        self.root.attributes('-alpha', 0.9)  # 반투명 설정
        self.root.attributes('-topmost', True)  # 항상 위에 표시
        self.root.overrideredirect(True)  # 창 경계선 제거
        
        # 캔버스 생성
        self.canvas = tk.Canvas(self.root, width=self.screenshot.width, height=self.screenshot.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # PIL 이미지를 PhotoImage로 변환
        photo = ImageTk.PhotoImage(self.screenshot)
        
        # 이미지를 캔버스 아이템으로 추가하고 참조 유지
        self.canvas.image = photo  # 이미지에 대한 참조 유지
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        
        # 키 제어 안내 레이블 추가
        self.info_label = tk.Label(
            self.root, 
            text = f"[{DRAG_FIXED_WIDTH_KEY}] 너비 고정 / [{DRAG_FIXED_HEIGHT_KEY}] 높이 고정 / [{DRAG_KEEP_SQUARE_KEY}] 정사각 비율 / [{DRAG_ASPECT_RATIO_KEY}] {DRAG_ASPECT_RATIO_TEXT} 비율",
            bg="#0000ff",
            fg="#ffffff",

            font=("Arial", 10, "bold"), 
            padx=100, pady=0,
            bd=1,         # 테두리 추가
            relief=tk.SOLID  # 단색 테두리
        )
        self.info_label.place(x=10, y=10)
        
        # 확대 창 생성
        self.create_zoom_window()
        
        # 이벤트 바인딩
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)  # 마우스 움직임 감지
        
        # ESC 키 누르면 취소
        self.root.bind("<Escape>", self.cancel_selection)
        
        # 창 표시
        self.root.deiconify()
        
        # 메인 루프 대기
        self.root.wait_window(self.root)
        
        return self.selected_region
    
    def create_zoom_window(self):
        """확대 창 생성"""
        self.zoom_window = tk.Toplevel()
        self.zoom_window.title("Magnifier")
        self.zoom_window.geometry(f"{self.zoom_size}x{self.zoom_size + 25}")
        
        # 투명도 관련 문제 해결을 위한 설정
        self.zoom_window.attributes('-alpha', 1.0)  # 완전 불투명하게 설정
        self.zoom_window.attributes('-topmost', True)  # 항상 최상위에 표시
        
        # 다른 창들보다 더 위에 표시되도록 zorder 조정
        self.zoom_window.lift()
        
        # 메인 프레임 (배경색 설정)
        main_frame = tk.Frame(self.zoom_window, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 확대 캔버스 (배경색 설정)
        self.zoom_canvas = tk.Canvas(main_frame, width=self.zoom_size, height=self.zoom_size, bg='black')
        self.zoom_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 상태 표시줄 추가
        self.status_frame = tk.Frame(self.zoom_window, height=25, bg="lightgray")
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 상태 레이블
        self.status_label = tk.Label(
            self.status_frame, 
            text="준비됨", 
            font=("Arial", 9), 
            bd=1, relief=tk.SUNKEN, 
            anchor=tk.W,
            bg="lightgray"
        )
        self.status_label.pack(fill=tk.X, padx=2, pady=2)
        
        # 확대 창이 닫히면 선택 취소
        self.zoom_window.protocol("WM_DELETE_WINDOW", lambda: self.cancel_selection())
    
    def update_zoom_view(self, x, y):
        """마우스 위치에 따라 확대 뷰 업데이트"""
        if not hasattr(self, 'screenshot') or self.screenshot is None:
            return
            
        # 확대할 영역 계산
        zoom_radius = self.zoom_size // (2 * self.zoom_factor)
        
        # 확대 영역이 스크린샷 범위를 벗어나지 않도록 보정
        left = max(0, x - zoom_radius)
        top = max(0, y - zoom_radius)
        right = min(self.screenshot.width, x + zoom_radius)
        bottom = min(self.screenshot.height, y + zoom_radius)
        
        # 영역 크롭 및 확대
        try:
            zoom_area = self.screenshot.crop((left, top, right, bottom))
            
            # 이미지 불투명도 향상 (필요한 경우)
            # RGBA로 변환해서 알파 채널을 조정
            if zoom_area.mode != 'RGB':
                zoom_area = zoom_area.convert('RGB')
            
            # 이미지 대비 강화 (선명도 향상)
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(zoom_area)
            zoom_area = enhancer.enhance(1.2)  # 대비 20% 증가
            
            # 밝기 약간 증가
            enhancer = ImageEnhance.Brightness(zoom_area)
            zoom_area = enhancer.enhance(1.1)  # 밝기 10% 증가
            
            # 확대
            zoomed = zoom_area.resize(
                (int(zoom_area.width * self.zoom_factor), 
                int(zoom_area.height * self.zoom_factor)),
                Image.LANCZOS
            )
            
            # 확대 창 이미지 업데이트
            self.zoomed_image = ImageTk.PhotoImage(zoomed)
            self.zoom_canvas.delete("all")
            
            # 배경색 설정 (이미지 가시성 향상)
            self.zoom_canvas.config(bg='black')
            
            self.zoom_canvas.create_image(self.zoom_size//2, self.zoom_size//2, 
                                        image=self.zoomed_image, anchor=tk.CENTER)
            
            # 중심 표시 (십자선)
            self.zoom_canvas.create_line(0, self.zoom_size//2, self.zoom_size, self.zoom_size//2, 
                                        fill="red", width=1)
            self.zoom_canvas.create_line(self.zoom_size//2, 0, self.zoom_size//2, self.zoom_size, 
                                        fill="red", width=1)
            
            # 키 상태 확인 및 상태 표시줄 업데이트
            self.update_status_bar()
            
            # 확대 창 위치 업데이트 (마우스 위치에 따라)
            x_screen, y_screen = pyautogui.position()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # 마우스가 화면 오른쪽/아래에 있으면 확대 창을 왼쪽/위에 배치
            if x_screen > screen_width // 2:
                zoom_x = x_screen - self.zoom_size - 20
            else:
                zoom_x = x_screen + 20
                
            if y_screen > screen_height // 2:
                zoom_y = y_screen - self.zoom_size - 20 - 25  # 상태 표시줄 높이 고려
            else:
                zoom_y = y_screen + 20
                
            self.zoom_window.geometry(f"{self.zoom_size}x{self.zoom_size + 25}+{zoom_x}+{zoom_y}")
    
            # 항상 최상위에 표시되도록 설정
            self.zoom_window.attributes('-topmost', True)
            self.zoom_window.lift()
            
        except Exception as e:
            print(f"확대 뷰 업데이트 오류: {e}")

    def update_status_bar(self):
        """현재 키 상태에 따라 상태 표시줄 업데이트"""
        if not hasattr(self, 'status_label') or not self.status_label:
            return
        
        # 키 상태 확인
        is_square_key_pressed = keyboard.is_pressed(DRAG_KEEP_SQUARE_KEY)
        is_width_key_pressed = keyboard.is_pressed(DRAG_FIXED_WIDTH_KEY)
        is_height_key_pressed = keyboard.is_pressed(DRAG_FIXED_HEIGHT_KEY)
        is_ratio_key_pressed = keyboard.is_pressed(DRAG_ASPECT_RATIO_KEY)
        
        status_text = "준비됨"
        status_bg = "lightgray"
        
        # 활성화된 키에 따라 상태 텍스트와 색상 설정
        if is_square_key_pressed:
            status_text = f"[{DRAG_KEEP_SQUARE_KEY}] 정사각형 비율 유지"
            status_bg = "#ffe6cc"  # 연한 주황색
        elif is_width_key_pressed:
            status_text = f"[{DRAG_FIXED_WIDTH_KEY}] 너비 고정"
            status_bg = "#cce5ff"  # 연한 파란색
        elif is_height_key_pressed:
            status_text = f"[{DRAG_FIXED_HEIGHT_KEY}] 높이 고정"
            status_bg = "#d4edda"  # 연한 녹색
        elif is_ratio_key_pressed:
            ratio_text = f"{DRAG_ASPECT_RATIO:.1f}"
            if DRAG_ASPECT_RATIO == 16/9:
                ratio_text = "16:9"
            elif DRAG_ASPECT_RATIO == 4/3:
                ratio_text = "4:3"
            status_text = f"[{DRAG_ASPECT_RATIO_KEY}] {ratio_text} 비율 유지"
            status_bg = "#f8d7da"  # 연한 빨간색
        
        # 드래그 상태에 따라 추가 정보
        if self.start_x is not None and self.current_x is not None:
            width = abs(self.current_x - self.start_x)
            height = abs(self.current_y - self.start_y)
            status_text += f" | {int(width)}x{int(height)}px"
        
        # 상태 레이블 업데이트
        self.status_label.config(text=status_text, bg=status_bg)
    
    def on_mouse_move(self, event):
        """마우스 이동 시 확대 뷰 업데이트"""
        self.update_zoom_view(event.x, event.y)
    
    def on_press(self, event):
        """마우스 버튼 누를 때"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 새 사각형 생성
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
    
    def on_drag(self, event):
        """마우스 드래그 중"""
        current_x = event.x
        current_y = event.y
        
        # 키보드 상태 확인
        is_square_key_pressed = keyboard.is_pressed(DRAG_KEEP_SQUARE_KEY)
        is_width_key_pressed = keyboard.is_pressed(DRAG_FIXED_WIDTH_KEY)
        is_height_key_pressed = keyboard.is_pressed(DRAG_FIXED_HEIGHT_KEY)
        is_ratio_key_pressed = keyboard.is_pressed(DRAG_ASPECT_RATIO_KEY)
        
        # 첫 드래그 시 고정 치수 설정
        if self.fixed_width is None and is_width_key_pressed:
            self.fixed_width = abs(current_x - self.start_x)
        
        if self.fixed_height is None and is_height_key_pressed:
            self.fixed_height = abs(current_y - self.start_y)
        
        # 키 상태에 따라 좌표 조정
        if is_square_key_pressed:
            # 정사각형 유지
            size = max(abs(current_x - self.start_x), abs(current_y - self.start_y))
            if current_x >= self.start_x:
                current_x = self.start_x + size
            else:
                current_x = self.start_x - size
                
            if current_y >= self.start_y:
                current_y = self.start_y + size
            else:
                current_y = self.start_y - size
        
        elif is_width_key_pressed and self.fixed_width is not None:
            # 너비 고정
            if current_x >= self.start_x:
                current_x = self.start_x + self.fixed_width
            else:
                current_x = self.start_x - self.fixed_width
        
        elif is_height_key_pressed and self.fixed_height is not None:
            # 높이 고정
            if current_y >= self.start_y:
                current_y = self.start_y + self.fixed_height
            else:
                current_y = self.start_y - self.fixed_height
        
        elif is_ratio_key_pressed:
            # 특정 비율 유지 (16:9 등)
            width = abs(current_x - self.start_x)
            height = width / DRAG_ASPECT_RATIO
            
            if current_y >= self.start_y:
                current_y = self.start_y + height
            else:
                current_y = self.start_y - height
        
        # 현재 좌표 업데이트
        self.current_x = current_x
        self.current_y = current_y
        
        # 사각형 크기 업데이트
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.current_x, self.current_y)
        
        # 확대 뷰 업데이트 (이미 상태 표시줄 업데이트를 포함함)
        self.update_zoom_view(event.x, event.y)
        
        # 선택 영역 크기 표시
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        
        # 사각형 크기 업데이트
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        # 이전 크기 텍스트와 반투명 효과 삭제
        self.canvas.delete("size_text")
        self.canvas.delete("overlay")
        
        # 선택 영역 계산
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)
        width = x2 - x1
        height = y2 - y1
        
        # 반투명 검은색 배경과 드래그 영역만 선명하게 보이는 효과 생성
        # 1. 위쪽 사각형
        if y1 > 0:
            self.canvas.create_rectangle(0, 0, self.screenshot.width, y1, 
                                        fill="#000000", stipple="gray50", outline="", tags="overlay")
        
        # 2. 아래쪽 사각형
        if y2 < self.screenshot.height:
            self.canvas.create_rectangle(0, y2, self.screenshot.width, self.screenshot.height, 
                                        fill="#000000", stipple="gray50", outline="", tags="overlay")
        
        # 3. 왼쪽 사각형
        if x1 > 0:
            self.canvas.create_rectangle(0, y1, x1, y2, 
                                        fill="#000000", stipple="gray50", outline="", tags="overlay")
        
        # 4. 오른쪽 사각형
        if x2 < self.screenshot.width:
            self.canvas.create_rectangle(x2, y1, self.screenshot.width, y2, 
                                        fill="#000000", stipple="gray50", outline="", tags="overlay")
        
        # 드래그 영역 테두리 (선명한 빨간색)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.current_x, self.current_y,
            outline='red', width=2
        )
        
        # 확대 뷰 업데이트 (이미 상태 표시줄 업데이트를 포함함)
        self.update_zoom_view(event.x, event.y)
        
        # 중앙에 크기 텍스트 표시
        x = min(self.start_x, self.current_x) + width / 2
        y = min(self.start_y, self.current_y) + height / 2
        
        self.canvas.create_text(
            x, y,
            text=f"{int(width)} x {int(height)}",
            fill="white",
            font=("Arial", 12, "bold"),
            tags="size_text"
        )
    
    def on_release(self, event):
        """마우스 버튼 놓을 때"""
        # 오버레이 삭제
        self.canvas.delete("overlay")

        self.current_x = event.x
        self.current_y = event.y
        
        # 키 상태에 따라 최종 조정 (on_drag와 동일한 로직)
        is_square_key_pressed = keyboard.is_pressed(DRAG_KEEP_SQUARE_KEY)
        is_width_key_pressed = keyboard.is_pressed(DRAG_FIXED_WIDTH_KEY)
        is_height_key_pressed = keyboard.is_pressed(DRAG_FIXED_HEIGHT_KEY)
        is_ratio_key_pressed = keyboard.is_pressed(DRAG_ASPECT_RATIO_KEY)
        
        if is_square_key_pressed:
            # 정사각형 유지
            size = max(abs(self.current_x - self.start_x), abs(self.current_y - self.start_y))
            if self.current_x >= self.start_x:
                self.current_x = self.start_x + size
            else:
                self.current_x = self.start_x - size
                
            if self.current_y >= self.start_y:
                self.current_y = self.start_y + size
            else:
                self.current_y = self.start_y - size
        
        elif is_width_key_pressed and self.fixed_width is not None:
            # 너비 고정
            if self.current_x >= self.start_x:
                self.current_x = self.start_x + self.fixed_width
            else:
                self.current_x = self.start_x - self.fixed_width
        
        elif is_height_key_pressed and self.fixed_height is not None:
            # 높이 고정
            if self.current_y >= self.start_y:
                self.current_y = self.start_y + self.fixed_height
            else:
                self.current_y = self.start_y - self.fixed_height
        
        elif is_ratio_key_pressed:
            # 특정 비율 유지 (16:9 등)
            width = abs(self.current_x - self.start_x)
            height = width / DRAG_ASPECT_RATIO
            
            if self.current_y >= self.start_y:
                self.current_y = self.start_y + height
            else:
                self.current_y = self.start_y - height
        
        # 좌표 정규화 (시작점이 항상 좌상단, 끝점이 항상 우하단이 되도록)
        x1 = min(self.start_x, self.current_x)
        y1 = min(self.start_y, self.current_y)
        x2 = max(self.start_x, self.current_x)
        y2 = max(self.start_y, self.current_y)
        
        width = x2 - x1
        height = y2 - y1
        
        # 창 기준 상대 좌표로 변환
        if self.target_window_only and self.window_manager and self.window_manager.is_window_valid():
            # 이미 타겟 윈도우 기준 좌표
            rel_x1, rel_y1, rel_x2, rel_y2 = x1, y1, x2, y2
            left, top, _, _ = self.window_rect
            abs_x1, abs_y1 = x1 + left, y1 + top
            abs_x2, abs_y2 = x2 + left, y2 + top
        else:
            # 화면 기준 절대 좌표
            abs_x1, abs_y1, abs_x2, abs_y2 = x1, y1, x2, y2
            
            # 창 기준 상대 좌표로 변환
            if self.window_manager and self.window_manager.is_window_valid():
                left, top, _, _ = self.window_manager.get_window_rect()
                rel_x1, rel_y1 = abs_x1 - left, abs_y1 - top
                rel_x2, rel_y2 = abs_x2 - left, abs_y2 - top
            else:
                rel_x1, rel_y1, rel_x2, rel_y2 = abs_x1, abs_y1, abs_x2, abs_y2
        
        # 선택된 영역 정보 저장
        self.selected_region = {
            "abs": (abs_x1, abs_y1, abs_x2, abs_y2),  # 절대 좌표 (화면 기준)
            "rel": (rel_x1, rel_y1, rel_x2, rel_y2),  # 상대 좌표 (창 기준)
            "width": width,
            "height": height
        }
        
        # 고정 치수 변수 초기화
        self.fixed_width = None
        self.fixed_height = None
        
        # 창 닫기
        if self.zoom_window:
            self.zoom_window.destroy()
        self.root.destroy()
        
        # 콜백 함수 호출
        if self.callback:
            self.callback(self.selected_region)
    
    def cancel_selection(self, event=None):
        """ESC 키 눌러 선택 취소"""
        self.selected_region = None
        
        # 고정 치수 변수 초기화
        self.fixed_width = None
        self.fixed_height = None
        
        if self.zoom_window:
            self.zoom_window.destroy()
        self.root.destroy()
        
        # 콜백 함수 호출
        if self.callback:
            self.callback(None)