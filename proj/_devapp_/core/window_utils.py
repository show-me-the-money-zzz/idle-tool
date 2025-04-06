import win32gui
import win32process
import win32con
import psutil
import time
from tkinter import messagebox
import win32api
from ctypes import windll, Structure, c_ulong, POINTER, sizeof, byref, c_long

from pynput.keyboard import Key, Controller

class WindowManager:
    """윈도우 창 관리 및 제어 클래스"""

    def __init__(self):
        self.target_hwnd = None
        self.window_rect = (0, 0, 0, 0)  # (left, top, right, bottom)

    def find_window_by_pid(self, pid):
        process = psutil.Process(pid)

        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    text = win32gui.GetWindowText(hwnd)
                    if text:
                        hwnds.append((hwnd, text))
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if not windows:
            return None, None

        return windows[0]

    def find_windows_by_name(self, app_name):
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
        self.target_hwnd = hwnd
        self.update_window_info()

    def update_window_info(self):
        if self.target_hwnd and win32gui.IsWindow(self.target_hwnd):
            self.window_rect = win32gui.GetWindowRect(self.target_hwnd)
            return True
        return False

    def get_window_rect(self):
        return self.window_rect

    def is_window_valid(self):
        return self.target_hwnd is not None and win32gui.IsWindow(self.target_hwnd)

    def activate_window(self):
        if not self.is_window_valid():
            return False

        try:
            if win32gui.IsIconic(self.target_hwnd):
                win32gui.ShowWindow(self.target_hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)

            win32gui.ShowWindow(self.target_hwnd, win32con.SW_SHOW)
            time.sleep(0.2)

            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.3)

            return True
        except Exception as e:
            print(f"창 활성화 오류: {e}")
            return False
        
    def send_key(self, key):
        # print(f"send_key_with_pynput({key})")
        """pynput을 사용한 키 입력"""
        try:
            if not self.activate_window():
                print("창 활성화에 실패했습니다.")
                return False
                
            # 활성화 대기
            time.sleep(0.2)
            
            # 키보드 컨트롤러 생성
            keyboard = Controller()
            
            # 특수키 매핑
            special_keys = {
                'enter': Key.enter,
                'space': Key.space,
                'tab': Key.tab,
                'backspace': Key.backspace,
                'esc': Key.esc
            }
            
            # 키 전송
            if key in special_keys:
                keyboard.press(special_keys[key])
                time.sleep(0.1)
                keyboard.release(special_keys[key])
            else:
                # 일반 문자 키
                keyboard.press(key)
                time.sleep(0.1)
                keyboard.release(key)
                
            return True
        except Exception as e:
            print(f"pynput 키 입력 오류: {e}")
            return False

    def click_at_position(self, rel_x, rel_y):
        try:
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False

            self.activate_window()
            time.sleep(0.1)

            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y

            class POINT(Structure):
                _fields_ = [("x", c_long), ("y", c_long)]

            pt = POINT()
            windll.user32.GetCursorPos(byref(pt))

            windll.user32.SetCursorPos(abs_x, abs_y)
            time.sleep(0.1)

            windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            time.sleep(0.1)
            windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP

            time.sleep(0.1)
            windll.user32.SetCursorPos(pt.x, pt.y)

            return True
        except Exception as e:
            print(f"클릭 오류 (SendInput): {e}")
            return False

    def get_relative_position(self, abs_x, abs_y):
        if not self.is_window_valid():
            return abs_x, abs_y

        left, top, _, _ = self.window_rect
        return abs_x - left, abs_y - top
