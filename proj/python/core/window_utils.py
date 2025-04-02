import win32gui
import win32process
import win32con
import psutil
import time
import pyautogui
from tkinter import messagebox

class WindowManager:
    """윈도우 창 관리 및 제어 클래스"""
    
    def __init__(self):
        self.target_hwnd = None
        self.window_rect = (0, 0, 0, 0)  # (left, top, right, bottom)
    
    def find_window_by_pid(self, pid):
        """PID로 윈도우 찾기"""
        # PID가 유효한지 확인
        process = psutil.Process(pid)
        
        # 해당 프로세스의 창 찾기
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    text = win32gui.GetWindowText(hwnd)
                    if text:  # 타이틀이 있는 창만 처리
                        hwnds.append((hwnd, text))
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if not windows:
            return None, None
        
        # 첫 번째 창 선택
        return windows[0]
    
    def find_windows_by_name(self, app_name):
        """앱 이름(창 제목)으로 창 검색"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if app_name.lower() in title.lower():
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        proc_name = process.name()
                        windows.append((hwnd, title, pid, proc_name))
                    except:
                        pass
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows
    
    def set_target_window(self, hwnd):
        """대상 윈도우 설정"""
        self.target_hwnd = hwnd
        self.update_window_info()
    
    def update_window_info(self):
        """타겟 윈도우의 현재 위치와 크기 정보를 업데이트"""
        if self.target_hwnd and win32gui.IsWindow(self.target_hwnd):
            self.window_rect = win32gui.GetWindowRect(self.target_hwnd)
            return True
        return False
    
    def get_window_rect(self):
        """윈도우의 위치와 크기 반환"""
        return self.window_rect
    
    def is_window_valid(self):
        """창이 유효한지 확인"""
        return self.target_hwnd is not None and win32gui.IsWindow(self.target_hwnd)
    
    def activate_window(self):
        """창 활성화"""
        if self.is_window_valid():
            # 창이 최소화되어 있으면 복원
            if win32gui.IsIconic(self.target_hwnd):
                win32gui.ShowWindow(self.target_hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)  # 창이 복원되기를 기다림
            
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.1)  # 창이 활성화되기를 기다림
            return True
        return False
    
    def send_key(self, key):
        """키 입력 전송"""
        if self.activate_window():
            pyautogui.press(key)
            return True
        return False
    
    def click_at_position(self, rel_x, rel_y):
        """상대 좌표 위치 클릭"""
        if not self.activate_window():
            return False
        
        left, top, _, _ = self.window_rect
        abs_x = left + rel_x
        abs_y = top + rel_y
        
        pyautogui.click(abs_x, abs_y)
        return True
    
    def get_relative_position(self, abs_x, abs_y):
        """절대 좌표를 창 기준 상대 좌표로 변환"""
        if not self.is_window_valid():
            return abs_x, abs_y
        
        left, top, _, _ = self.window_rect
        return abs_x - left, abs_y - top