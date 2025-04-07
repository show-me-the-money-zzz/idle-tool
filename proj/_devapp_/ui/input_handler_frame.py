import tkinter as tk
from tkinter import messagebox, ttk
import pyautogui

from zzz.config import *

class InputHandlerFrame(ttk.LabelFrame):
    """입력 처리 프레임 (이전의 자동화 영역)"""
    
    def __init__(self, parent, window_manager, status_var):
        super().__init__(parent, text="입력 처리", padding="10")
        
        self.window_manager = window_manager
        self.status_var = status_var
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # 키 입력 관련 프레임
        key_frame = ttk.Frame(self)
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
        ttk.Label(self, text="클릭 X (창 내부):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.click_x_var = tk.StringVar(value=DEFAULT_CLICK_X)
        click_x_entry = ttk.Entry(self, textvariable=self.click_x_var, width=10)
        click_x_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 마우스 클릭 버튼
        self.click_btn = ttk.Button(self, text="마우스 클릭", command=self.mouse_click)
        self.click_btn.grid(row=1, column=2, padx=5, pady=2)
        
        ttk.Label(self, text="클릭 Y (창 내부):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.click_y_var = tk.StringVar(value=DEFAULT_CLICK_Y)
        click_y_entry = ttk.Entry(self, textvariable=self.click_y_var, width=10)
        click_y_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 탭 순서 설정 - 클릭 X에서 클릭 Y로 이동하도록
        click_x_entry.bind('<Tab>', lambda e: click_y_entry.focus_set() or 'break')
        
        # 현재 마우스 위치 표시 레이블 (절대 좌표와 상대 좌표)
        self.mouse_pos_label = ttk.Label(self, text="마우스 위치: 절대(X=0, Y=0) / 상대(X=0, Y=0)")
        self.mouse_pos_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 마우스 위치 복사 버튼
        copy_pos_btn = ttk.Button(self, text="현재 위치 복사", command=self.copy_current_mouse_position)
        copy_pos_btn.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
    
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
                self.update()  # UI 업데이트
                
                # 상대 좌표 위치 클릭
                if self.window_manager.click_at_position(rel_x, rel_y):
                    self.status_var.set(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                else:
                    messagebox.showerror("오류", "클릭 작업에 실패했습니다.")
            else:
                messagebox.showinfo("알림", "클릭할 좌표를 설정해주세요.")
                
        except Exception as e:
            messagebox.showerror("마우스 클릭 오류", f"마우스 클릭 중 오류가 발생했습니다: {str(e)}")
    
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
    
    def update_mouse_position(self):
        """마우스 위치 업데이트"""
        x, y = pyautogui.position()
        rel_x, rel_y = x, y
        
        # 연결된 창이 있으면 상대 좌표 계산
        if self.window_manager.is_window_valid():
            rel_x, rel_y = self.window_manager.get_relative_position(x, y)
        
        self.mouse_pos_label.config(text=f"마우스 위치: 절대(X={x}, Y={y}) / 상대(X={rel_x}, Y={rel_y})")