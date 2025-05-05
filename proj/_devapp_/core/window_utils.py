import win32gui
import win32process
import win32con
import psutil
import time
# import win32api
from ctypes import windll, Structure, c_ulong, POINTER, sizeof, byref, c_long

from pynput.keyboard import Key, Controller
from PySide6.QtWidgets import QMessageBox

from stores.data_setting import DataSetting
from grinder_utils.system import PrintDEV

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
    
    def Get_Resolution(self):
        left, top, right, bottom = self.window_rect
        return [ right - left, bottom - top ]

    def is_window_valid(self):
        return self.target_hwnd is not None and win32gui.IsWindow(self.target_hwnd)

    def activate_window(self, checkresolution = True):
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
            
            if checkresolution:
                self.Check_Reoslution()

            return True
        except Exception as e:
            print(f"창 활성화 오류: {e}")
            return False
        
    def Check_Reoslution(self):
        setting_resol = DataSetting.Get_Resolution()
        # PrintDEV(f"WindowManager.Check_Reoslution(): resol= {setting_resol}")
        
        if None != setting_resol:
            width, height = self.Get_Resolution()
            resol_w, resol_h = setting_resol
            if width != resol_w or height != resol_h:
                QMessageBox.warning(None, "경고",
                    f"저장된 해상도({resol_w}x{resol_h})와 불일치({width}x{height})\n"
                    "게임을 저장된 해상도로 변경함"
                )
                self.resize_window(resol_w, resol_h)
                self.activate_window(False)
        else:
            temp = 0
            
            # # DEV 코드
            # width, height = self.Get_Resolution()
            # DataSetting.Set_Resolution(width, height)
        
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
                'esc': Key.esc,
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

            self.Print_DEV(f"WindowManager.click_at_position({rel_x}, {rel_y})")
            self.activate_window()
            time.sleep(0.1)

            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            self.Print_DEV(f"click_at_position1({rel_x}, {rel_y})")

            class POINT(Structure):
                _fields_ = [("x", c_long), ("y", c_long)]
                
            self.Print_DEV(f"click_at_position2({rel_x}, {rel_y})")

            pt = POINT()
            windll.user32.GetCursorPos(byref(pt))
            self.Print_DEV(f"click_at_position3({rel_x}, {rel_y})")

            windll.user32.SetCursorPos(abs_x, abs_y)
            time.sleep(0.1)
            self.Print_DEV(f"click_at_position4({rel_x}, {rel_y})")

            windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            self.Print_DEV(f"click_at_position5({rel_x}, {rel_y})")
            time.sleep(0.1)
            windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
            self.Print_DEV(f"click_at_position6({rel_x}, {rel_y})")

            time.sleep(0.1)
            windll.user32.SetCursorPos(pt.x, pt.y)
            self.Print_DEV(f"click_at_position7({rel_x}, {rel_y})")

            return True
        except Exception as e:
            print(f"클릭 오류 (SendInput): {e}")
            return False
    def Print_DEV(self, log):
        return
        print(log)
        
    def scroll_mousewheel(self, amount):
        """
        타겟 윈도우의 중앙에서 마우스 휠 스크롤을 수행한 후 원래 마우스 위치로 돌아갑니다.
        
        Args:
            amount (int): 스크롤 양(양수: 위로, 음수: 아래로)
        
        Returns:
            bool: 성공 여부
        """
        try:
            if not self.is_window_valid():
                print("유효한 창이 없습니다.")
                return False
            
            # 현재 마우스 커서 위치 저장
            class POINT(Structure):
                _fields_ = [("x", c_long), ("y", c_long)]
            
            original_pos = POINT()
            windll.user32.GetCursorPos(byref(original_pos))
            
            # 타겟 창 중앙 좌표 계산
            left, top, right, bottom = self.window_rect
            center_x = int((left + right) / 2)
            center_y = int((top + bottom) / 2)
            
            # 마우스 커서를 중앙으로 이동
            windll.user32.SetCursorPos(center_x, center_y)
            time.sleep(0.1)
            
            # 스크롤 수행
            # 필요한 scroll_wheel 함수 정의가 없으므로 직접 구현
            MOUSEEVENTF_WHEEL = 0x0800
            wheel_amount = amount * 120  # 양수는 위로, 음수는 아래로
            
            # 스크롤 이벤트 발생
            windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, wheel_amount, 0)
            time.sleep(0.1)
            
            # 원래 마우스 위치로 복원
            windll.user32.SetCursorPos(original_pos.x, original_pos.y)
            
            return True
        except Exception as e:
            print(f"스크롤 오류: {e}")
            return False

    def get_relative_position(self, abs_x, abs_y):
        if not self.is_window_valid():
            return abs_x, abs_y

        left, top, _, _ = self.window_rect
        return abs_x - left, abs_y - top
    
    def resize_window(self, width, height):
        if not self.is_window_valid():
            print("타겟 윈도우가 유효하지 않습니다.")
            return False

        left, top, _, _ = self.window_rect

        try:
            win32gui.MoveWindow(self.target_hwnd, left, top, width, height, True)
            self.update_window_info()
            return True
        except Exception as e:
            print(f"창 크기 변경 실패: {e}")
            return False
        
    def Resize_HD(self, name, game = ""):
        """
        지정된 이름(name)에 따라 해상도를 변경합니다.
        name 예시: "nHD", "qHD", "HD", "HD+", "FHD", "QHD"
        
        Games
            LORDNINE: 중간 FHD | 낮음 HD
        """

        # 기본 해상도 매핑
        resolutions = {
            "nHD": (640, 360),
            "qHD": (960, 540),
            "HD": (1280, 720),
            "HD+": (1600, 900),
            "FHD": (1920, 1080),
            "QHD": (2560, 1440)
        }

        if name not in resolutions:
            print(f"[오류] 지원하지 않는 해상도 이름: {name}")
            return False

        w, h = resolutions[name]

        # 윈도우 테두리/타이틀바 보정
        margin_w = 14  # 좌우 여백 합
        margin_h = 7 + 30  # 30: 상단 타이틀 바
        
        if "LORDNINE" == game:
            margin_w += 2
            margin_h += 2

        w += margin_w
        h += margin_h

        return self.resize_window(w, h)

WindowUtil = WindowManager()