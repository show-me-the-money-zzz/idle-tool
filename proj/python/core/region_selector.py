# 이 부분을 수정하세요 (region_selector.py 파일)

import tkinter as tk
import pyautogui
import win32gui
import time
from PIL import Image, ImageTk, ImageGrab
import numpy as np

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
    
    def start_selection(self, callback=None, target_window_only=False):
        """영역 선택 시작"""
        self.callback = callback
        self.target_window_only = target_window_only
        
        # 새 tkinter 창 생성 (메인 루트 창이 아닌 Toplevel 사용)
        self.root = tk.Toplevel()
        self.root.withdraw()  # 임시로 숨김
        
        # 타겟 윈도우가 있고, 해당 윈도우만 캡처하는 모드라면
        if target_window_only and self.window_manager and self.window_manager.is_window_valid():
            # 창 위치 가져오기
            self.window_rect = self.window_manager.get_window_rect()
            left, top, right, bottom = self.window_rect
            width = right - left
            height = bottom - top
            
            # 전체 화면 스크린샷
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        else:
            # 전체 화면 스크린샷
            screenshot = ImageGrab.grab()
            self.window_rect = (0, 0, screenshot.width, screenshot.height)
        
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
        self.root.attributes('-alpha', 0.3)  # 반투명 설정
        self.root.attributes('-topmost', True)  # 항상 위에 표시
        self.root.overrideredirect(True)  # 창 경계선 제거
        
        # 캔버스 생성
        self.canvas = tk.Canvas(self.root, width=screenshot.width, height=screenshot.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # PIL 이미지를 PhotoImage로 변환
        # 이 방식은 Tkinter에서 이미지를 안정적으로 유지하기 위한 것입니다
        photo = ImageTk.PhotoImage(screenshot)
        
        # 이미지를 캔버스 아이템으로 추가하고 참조 유지
        self.canvas.image = photo  # 이미지에 대한 참조 유지
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        
        # 이벤트 바인딩
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # ESC 키 누르면 취소
        self.root.bind("<Escape>", self.cancel_selection)
        
        # 창 표시
        self.root.deiconify()
        
        # 메인 루프 대기
        self.root.wait_window(self.root)
        
        return self.selected_region
    
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
        self.current_x = event.x
        self.current_y = event.y
        
        # 사각형 크기 업데이트
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.current_x, self.current_y)
    
    def on_release(self, event):
        """마우스 버튼 놓을 때"""
        self.current_x = event.x
        self.current_y = event.y
        
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
        
        # 창 닫기
        self.root.destroy()
        
        # 콜백 함수 호출
        if self.callback:
            self.callback(self.selected_region)
    
    def cancel_selection(self, event=None):
        """ESC 키 눌러 선택 취소"""
        self.selected_region = None
        self.root.destroy()
        
        # 콜백 함수 호출
        if self.callback:
            self.callback(None)