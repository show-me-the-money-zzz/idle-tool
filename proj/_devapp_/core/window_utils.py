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
        
        self.force_resolution = True

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
            
            if checkresolution and self.force_resolution:
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
        return self.click_at_position_original(rel_x, rel_y)
        # return self.click_at_position_post_message(rel_x, rel_y)
        # return self.click_at_position_send_message(rel_x, rel_y)
        # return self.click_at_position_uia(rel_x, rel_y)
    
    def Get_CursorPos(self):
        class POINT(Structure):
            _fields_ = [("x", c_long), ("y", c_long)]
        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        return pt

    def click_at_position_original(self, rel_x, rel_y):
        print(f"click_at_position_original({rel_x}, {rel_y})")
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

            # class POINT(Structure):
            #     _fields_ = [("x", c_long), ("y", c_long)]
                
            # self.Print_DEV(f"click_at_position2({rel_x}, {rel_y})")

            pt = self.Get_CursorPos()
            # windll.user32.GetCursorPos(byref(pt))
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
        
    def click_hardware_injection(self, rel_x, rel_y):
        """하드웨어 수준 마우스 입력 시뮬레이션"""
        try:
            import ctypes
            from ctypes import wintypes
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            print(f"하드웨어 수준 클릭: ({abs_x}, {abs_y})")
            
            # 저수준 하드웨어 입력을 위한 구조체
            class HARDWAREINPUT(ctypes.Structure):
                _fields_ = [
                    ("uMsg", wintypes.DWORD),
                    ("wParamL", wintypes.WORD),
                    ("wParamH", wintypes.WORD)
                ]
            
            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [
                    ("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
                ]
            
            class INPUT_UNION(ctypes.Union):
                _fields_ = [
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT)
                ]
            
            class INPUT(ctypes.Structure):
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("union", INPUT_UNION)
                ]
            
            # 필요한 상수들
            INPUT_MOUSE = 0
            INPUT_HARDWARE = 2
            MOUSEEVENTF_MOVE = 0x0001
            MOUSEEVENTF_LEFTDOWN = 0x0002
            MOUSEEVENTF_LEFTUP = 0x0004
            MOUSEEVENTF_ABSOLUTE = 0x8000
            
            # 화면 해상도 가져오기
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # 좌표를 0-65535 범위로 변환
            normalized_x = int(65535 * abs_x / screen_width)
            normalized_y = int(65535 * abs_y / screen_height)
            
            # 하드웨어 입력으로 마우스 이동
            hardware_input = INPUT()
            hardware_input.type = INPUT_HARDWARE
            hardware_input.union.hi.uMsg = 0x0200  # WM_MOUSEMOVE
            hardware_input.union.hi.wParamL = normalized_x & 0xFFFF
            hardware_input.union.hi.wParamH = normalized_y & 0xFFFF
            
            # 마우스 이동
            user32.SendInput(1, ctypes.byref(hardware_input), ctypes.sizeof(INPUT))
            time.sleep(0.1)
            
            # 하드웨어 클릭 다운
            hardware_click_down = INPUT()
            hardware_click_down.type = INPUT_HARDWARE
            hardware_click_down.union.hi.uMsg = 0x0201  # WM_LBUTTONDOWN
            hardware_click_down.union.hi.wParamL = 0x0001  # MK_LBUTTON
            hardware_click_down.union.hi.wParamH = 0
            
            user32.SendInput(1, ctypes.byref(hardware_click_down), ctypes.sizeof(INPUT))
            time.sleep(0.05)
            
            # 하드웨어 클릭 업
            hardware_click_up = INPUT()
            hardware_click_up.type = INPUT_HARDWARE
            hardware_click_up.union.hi.uMsg = 0x0202  # WM_LBUTTONUP
            hardware_click_up.union.hi.wParamL = 0
            hardware_click_up.union.hi.wParamH = 0
            
            user32.SendInput(1, ctypes.byref(hardware_click_up), ctypes.sizeof(INPUT))
            
            print("하드웨어 수준 클릭 완료")
            return True
        except Exception as e:
            print(f"하드웨어 수준 클릭 오류: {e}")
            return False
        
    def click_raw_input(self, rel_x, rel_y):
        """Raw Input을 사용한 클릭"""
        try:
            import ctypes
            from ctypes import wintypes
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            print(f"Raw Input 클릭: ({abs_x}, {abs_y})")
            
            # Raw Input 구조체 정의
            class RAWINPUTHEADER(ctypes.Structure):
                _fields_ = [
                    ("dwType", wintypes.DWORD),
                    ("dwSize", wintypes.DWORD),
                    ("hDevice", wintypes.HANDLE),
                    ("wParam", wintypes.WPARAM)
                ]
            
            class RAWMOUSE(ctypes.Structure):
                _fields_ = [
                    ("usFlags", wintypes.USHORT),
                    ("ulButtons", wintypes.ULONG),
                    ("usButtonFlags", wintypes.USHORT),
                    ("usButtonData", wintypes.USHORT),
                    ("ulRawButtons", wintypes.ULONG),
                    ("lLastX", wintypes.LONG),
                    ("lLastY", wintypes.LONG),
                    ("ulExtraInformation", wintypes.ULONG)
                ]
            
            class RAWINPUT(ctypes.Structure):
                _fields_ = [
                    ("header", RAWINPUTHEADER),
                    ("mouse", RAWMOUSE)
                ]
            
            # 현재 마우스 위치 저장
            current_pos = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(current_pos))
            
            # 마우스 이동
            ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
            time.sleep(0.1)
            
            # Raw Input으로 클릭 시뮬레이션
            raw_input = RAWINPUT()
            raw_input.header.dwType = 0  # RIM_TYPEMOUSE
            raw_input.header.dwSize = ctypes.sizeof(RAWINPUT)
            raw_input.header.hDevice = None
            
            # 마우스 버튼 다운
            raw_input.mouse.usButtonFlags = 0x0001  # RI_MOUSE_LEFT_BUTTON_DOWN
            raw_input.mouse.lLastX = 0
            raw_input.mouse.lLastY = 0
            
            # 직접 창에 Raw Input 메시지 전송
            # 이 부분은 실제로는 더 복잡한 구현이 필요할 수 있습니다
            result1 = ctypes.windll.user32.SendMessageW(
                self.target_hwnd,
                0x00FF,  # WM_INPUT
                0,
                ctypes.byref(raw_input)
            )
            
            time.sleep(0.05)
            
            # 마우스 버튼 업
            raw_input.mouse.usButtonFlags = 0x0002  # RI_MOUSE_LEFT_BUTTON_UP
            result2 = ctypes.windll.user32.SendMessageW(
                self.target_hwnd,
                0x00FF,  # WM_INPUT
                0,
                ctypes.byref(raw_input)
            )
            
            # 원래 위치로 복원
            ctypes.windll.user32.SetCursorPos(current_pos.x, current_pos.y)
            
            print(f"Raw Input 클릭 완료: {result1}, {result2}")
            return True
        except Exception as e:
            print(f"Raw Input 클릭 오류: {e}")
            return False
        
    def click_with_global_hook(self, rel_x, rel_y):
        """글로벌 마우스 훅을 사용한 클릭"""
        try:
            import ctypes
            from ctypes import wintypes
            import time
            import threading
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            print(f"글로벌 훅 클릭: ({abs_x}, {abs_y})")
            
            # 훅 프로시저 정의
            def low_level_mouse_proc(nCode, wParam, lParam):
                if nCode >= 0:
                    # 여기서 마우스 이벤트를 조작할 수 있습니다
                    pass
                return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
            
            # 훅 프로시저 타입 정의
            HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
            hook_proc = HOOKPROC(low_level_mouse_proc)
            
            # 현재 스레드 ID 가져오기
            thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
            
            # 마우스 훅 설치
            hook_id = ctypes.windll.user32.SetWindowsHookExW(
                14,  # WH_MOUSE_LL (Low-level mouse input events)
                hook_proc,
                ctypes.windll.kernel32.GetModuleHandleW(None),
                0
            )
            
            if not hook_id:
                print("훅 설치 실패")
                return False
            
            try:
                # 마우스 이동 및 클릭
                ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
                time.sleep(0.1)
                
                # 직접적인 하드웨어 시뮬레이션
                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
                time.sleep(0.05)
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
                
                print("글로벌 훅 클릭 완료")
                return True
            finally:
                # 훅 제거
                ctypes.windll.user32.UnhookWindowsHookEx(hook_id)
                
        except Exception as e:
            print(f"글로벌 훅 클릭 오류: {e}")
            return False
        
    def click_at_position_pyautogui(self, rel_x, rel_y):
        """PyAutoGUI를 사용한 클릭 구현"""
        print(f"click_at_position_pyautogui({rel_x}, {rel_y})")
        try:
            # # PyAutoGUI 설치 확인 및 설치
            # try:
            #     import pyautogui
            # except ImportError:
            #     import pip
            #     pip.main(['install', 'pyautogui'])
            #     import pyautogui
            import pyautogui
            
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            print(pyautogui.size())
                        
            # # 창 활성화
            # self.activate_window()
            # time.sleep(1.0)
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            # 현재 마우스 위치 저장
            # current_x, current_y = pyautogui.position()
            # pyautogui.moveTo(abs_x, abs_y)
            # print(f"click_at_position_pyautogui00({pyautogui.position()}): {abs_x}, {abs_y}")

            # 창 활성화
            # self.activate_window()
            # time.sleep(0.01)
            
            # 마우스 이동 및 클릭
            pyautogui.moveTo(abs_x, abs_y, 1)
            self.activate_window()
            time.sleep(1.0)
            # windll.user32.SetCursorPos(abs_x, abs_y)
            # time.sleep(0.01)
            # print(f"click_at_position_pyautogui11({pyautogui.position()})")
            # pt = self.Get_CursorPos()
            # windll.user32.SetCursorPos(abs_x, abs_y)
            # print(f"click_at_position_pyautogui22({abs_x}, {abs_y})")
            # time.sleep(0.1)

            pyautogui.click()
            
            # 원래 위치로 돌아가기 (선택 사항)
            # pyautogui.moveTo(current_x, current_y)
            
            return True
        except Exception as e:
            print(f"PyAutoGUI 클릭 오류: {e}")
            return False
        
    def click_with_win32_api(self, rel_x, rel_y):
        """Win32 API를 직접 사용한 클릭 (PyAutoGUI 우회)"""
        try:
            import win32api
            import win32con
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            print(f"Win32 API로 클릭: ({abs_x}, {abs_y})")
            
            # 현재 마우스 위치 저장
            orig_x, orig_y = win32api.GetCursorPos()
            
            # 빠르게 이동하고 즉시 클릭
            win32api.SetCursorPos((abs_x, abs_y))
            time.sleep(0.01)  # 매우 짧은 지연
            
            # 마우스 클릭
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # 빠르게 원래 위치로 복원
            win32api.SetCursorPos((orig_x, orig_y))
            
            print("Win32 API 클릭 완료")
            return True
        except Exception as e:
            print(f"Win32 API 클릭 오류: {e}")
            return False
        
    def click_with_sendinput(self, rel_x, rel_y):
        """SendInput을 사용한 클릭 (더 낮은 수준)"""
        try:
            import ctypes
            from ctypes import wintypes
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            print(f"SendInput으로 클릭: ({abs_x}, {abs_y})")
            
            # 필요한 구조체 및 상수 정의
            MOUSEEVENTF_MOVE = 0x0001
            MOUSEEVENTF_LEFTDOWN = 0x0002
            MOUSEEVENTF_LEFTUP = 0x0004
            MOUSEEVENTF_ABSOLUTE = 0x8000
            
            # 화면 해상도 가져오기
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # 좌표를 0-65535 범위로 변환
            normalized_x = int(65535 * abs_x / screen_width)
            normalized_y = int(65535 * abs_y / screen_height)
            
            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [
                    ("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
                ]
            
            class INPUT(ctypes.Structure):
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("mi", MOUSEINPUT)
                ]
            
            # 현재 마우스 위치 저장
            current_pos = ctypes.wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(current_pos))
            orig_x, orig_y = current_pos.x, current_pos.y
            
            # 마우스 이동 입력 설정
            move_input = INPUT(0, MOUSEINPUT(
                normalized_x, normalized_y, 0, 
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 
                0, None
            ))
            
            # 마우스 다운 입력 설정
            down_input = INPUT(0, MOUSEINPUT(
                0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, None
            ))
            
            # 마우스 업 입력 설정
            up_input = INPUT(0, MOUSEINPUT(
                0, 0, 0, MOUSEEVENTF_LEFTUP, 0, None
            ))
            
            # 연속으로 빠르게 실행
            user32.SendInput(1, ctypes.byref(move_input), ctypes.sizeof(INPUT))
            time.sleep(0.01)
            user32.SendInput(1, ctypes.byref(down_input), ctypes.sizeof(INPUT))
            time.sleep(0.01)
            user32.SendInput(1, ctypes.byref(up_input), ctypes.sizeof(INPUT))
            
            # 원래 위치로 복원
            orig_normalized_x = int(65535 * orig_x / screen_width)
            orig_normalized_y = int(65535 * orig_y / screen_height)
            restore_input = INPUT(0, MOUSEINPUT(
                orig_normalized_x, orig_normalized_y, 0, 
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 
                0, None
            ))
            user32.SendInput(1, ctypes.byref(restore_input), ctypes.sizeof(INPUT))
            
            print("SendInput 클릭 완료")
            return True
        except Exception as e:
            print(f"SendInput 클릭 오류: {e}")
            return False
        
    def click_with_postmessage(self, rel_x, rel_y):
        """PostMessage를 사용한 창 직접 클릭 (물리적 마우스 이동 없음)"""
        try:
            import win32gui
            import win32con
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            print(f"PostMessage로 클릭: ({rel_x}, {rel_y})")
            
            # MAKELPARAM 매크로 구현
            def MAKELPARAM(low, high):
                return ((high << 16) | (low & 0xFFFF))
            
            # 창을 포그라운드로 설정
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.1)
            
            # 마우스 다운 메시지 전송
            win32gui.PostMessage(
                self.target_hwnd, 
                win32con.WM_LBUTTONDOWN, 
                win32con.MK_LBUTTON, 
                MAKELPARAM(rel_x, rel_y)
            )
            time.sleep(0.05)
            
            # 마우스 업 메시지 전송
            win32gui.PostMessage(
                self.target_hwnd, 
                win32con.WM_LBUTTONUP, 
                0, 
                MAKELPARAM(rel_x, rel_y)
            )
            
            print("PostMessage 클릭 완료")
            return True
        except Exception as e:
            print(f"PostMessage 클릭 오류: {e}")
            return False
        
    def click_stealth(self, rel_x, rel_y):
        """완전히 은밀한 클릭 - 마우스 이동 없이 창에 직접 메시지 전송"""
        try:
            import win32gui
            import win32con
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            print(f"은밀한 클릭: ({rel_x}, {rel_y}) - 마우스 이동 없음")
            
            # MAKELPARAM 매크로 구현
            def MAKELPARAM(low, high):
                return ((high << 16) | (low & 0xFFFF))
            
            # 창 활성화 (필요한 경우)
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.2)
            
            # 마우스 hover 메시지 먼저 전송 (일부 앱에서 필요)
            win32gui.PostMessage(
                self.target_hwnd, 
                win32con.WM_MOUSEMOVE, 
                0, 
                MAKELPARAM(rel_x, rel_y)
            )
            time.sleep(0.01)
            
            # 마우스 다운 메시지 전송
            win32gui.PostMessage(
                self.target_hwnd, 
                win32con.WM_LBUTTONDOWN, 
                win32con.MK_LBUTTON, 
                MAKELPARAM(rel_x, rel_y)
            )
            time.sleep(0.05)
            
            # 마우스 업 메시지 전송
            win32gui.PostMessage(
                self.target_hwnd, 
                win32con.WM_LBUTTONUP, 
                0, 
                MAKELPARAM(rel_x, rel_y)
            )
            
            print("은밀한 클릭 완료")
            return True
        except Exception as e:
            print(f"은밀한 클릭 오류: {e}")
            return False
        
    def click_hybrid_approach(self, rel_x, rel_y):
        """하이브리드 접근법: 다른 앱으로 덮은 상태에서 이동 후 PostMessage 클릭"""
        try:
            import win32api
            import win32gui
            import win32con
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 1단계: 다른 앱이 덮고 있는 상태에서 마우스만 이동
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            print(f"1단계: 다른 앱이 덮고 있는 상태에서 마우스 이동: ({abs_x}, {abs_y})")
            
            # 현재 활성 창을 기록 (나중에 복원용)
            current_active_window = win32gui.GetForegroundWindow()
            
            # 마우스를 목표 위치로 이동 (다른 앱이 덮고 있는 상태)
            win32api.SetCursorPos((abs_x, abs_y))
            time.sleep(0.1)
            
            # 2단계: 타겟 앱 활성화
            print("2단계: 타겟 앱 활성화")
            self.activate_window()
            time.sleep(0.3)  # 앱이 올라오는 시간 대기
            
            # 3단계: PostMessage로 클릭 (물리적 마우스 이동 없음)
            print("3단계: PostMessage로 클릭")
            
            def MAKELPARAM(low, high):
                return ((high << 16) | (low & 0xFFFF))
            
            # 마우스 다운 메시지 전송
            win32gui.PostMessage(
                self.target_hwnd, 
                win32con.WM_LBUTTONDOWN, 
                win32con.MK_LBUTTON, 
                MAKELPARAM(rel_x, rel_y)
            )
            time.sleep(0.05)
            
            # 마우스 업 메시지 전송
            win32gui.PostMessage(
                self.target_hwnd, 
                win32con.WM_LBUTTONUP, 
                0, 
                MAKELPARAM(rel_x, rel_y)
            )
            
            # 4단계: 원래 활성 창으로 복원 (선택사항)
            # time.sleep(0.5)
            # win32gui.SetForegroundWindow(current_active_window)
            
            print("하이브리드 클릭 완료")
            return True
        except Exception as e:
            print(f"하이브리드 클릭 오류: {e}")
            return False
    
    def click_at_position_post_message(self, rel_x, rel_y):
        """PostMessage를 사용한 클릭 구현"""
        print(f"click_at_position_post_message({rel_x}, {rel_y})")
        # LORDNINE 불가
        try:
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # pt = self.Get_CursorPos()

            self.activate_window()
            time.sleep(0.1)

            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            
            # 좌표를 LPARAM으로 변환 (하위 16비트: x, 상위 16비트: y)
            lParam = rel_y << 16 | rel_x
            
            # WM_LBUTTONDOWN, WM_LBUTTONUP 메시지 전송
            win32gui.PostMessage(self.target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            time.sleep(0.05)
            win32gui.PostMessage(self.target_hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            
            # time.sleep(1.0)
            # # auto.SetCursorPos(pt.x, pt.y)
            # windll.user32.SetCursorPos(pt.x, pt.y)

            return True
        except Exception as e:
            print(f"PostMessage 클릭 오류: {e}")
            return False
    
    def click_at_position_send_message(self, rel_x, rel_y):
        """SendMessage를 사용한 클릭 구현 (동기식)"""
        print(f"click_at_position_send_message({rel_x}, {rel_y})")
        # LORDNINE 불가
        try:
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            pt = self.Get_CursorPos()

            self.activate_window()
            
            # 좌표를 LPARAM으로 변환
            lParam = rel_y << 16 | rel_x
            
            # WM_LBUTTONDOWN, WM_LBUTTONUP 메시지 전송
            win32gui.SendMessage(self.target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            win32gui.SendMessage(self.target_hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            
            time.sleep(1.0)
            # auto.SetCursorPos(pt.x, pt.y)
            windll.user32.SetCursorPos(pt.x, pt.y)

            return True
        except Exception as e:
            print(f"SendMessage 클릭 오류: {e}")
            return False
    
    def click_at_position_uia(self, rel_x, rel_y):
        """UI Automation을 사용한 클릭 구현"""
        print(f"click_at_position_uia({rel_x}, {rel_y})")
        try:
            import uiautomation as auto
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            pt = self.Get_CursorPos()
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            # 창을 활성화
            # auto.WindowControl(Handle=self.target_hwnd).SetFocus()
            time.sleep(0.2)
            
            # 특정 위치를 클릭
            auto.Click(abs_x, abs_y)
            
            time.sleep(0.01)
            # auto.SetCursorPos(pt.x, pt.y)
            windll.user32.SetCursorPos(pt.x, pt.y)
            
            return True
        except ImportError:
            print("UIAutomation 라이브러리가 설치되지 않았습니다. pip install uiautomation")
            return False
        except Exception as e:
            print(f"UIA 클릭 오류: {e}")
            return False
        
    def click_at_position_interception(self, rel_x, rel_y):
        """interception-python을 사용한 간단한 클릭 구현"""
        print(f"click_at_position_interception({rel_x}, {rel_y})")
        try:
            # interception-python 모듈 임포트 (실제 임포트 이름 확인 필요)
            import interception as ip
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 창 활성화
            self.activate_window()
            time.sleep(0.2)
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            # 인터셉션 초기화 (실제 API에 맞게 수정 필요)
            context = ip.create_context()
            
            try:
                # 마우스 이동 및 클릭 (실제 API에 맞게 수정 필요)
                ip.move_mouse(context, abs_x, abs_y)
                time.sleep(0.1)
                ip.click_mouse(context)
                
                return True
            finally:
                # 리소스 정리 (실제 API에 맞게 수정 필요)
                ip.destroy_context(context)
            
        except ImportError as e:
            print(f"interception-python 모듈을 가져올 수 없습니다: {e}")
            return False
        except Exception as e:
            print(f"interception-python 클릭 오류: {e}")
            return False
        
    def click_at_position_win32(self, rel_x, rel_y):
        """Win32 API를 사용한 클릭 구현 (좌표 범위 확인 추가)"""
        try:
            import win32api
            import win32con
            import time
            
            # 화면 해상도 가져오기
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 창 활성화
            self.activate_window()
            time.sleep(0.2)
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            # 좌표가 화면 영역 내에 있는지 확인
            abs_x = max(0, min(abs_x, screen_width - 1))
            abs_y = max(0, min(abs_y, screen_height - 1))
            
            print(f"화면 해상도: {screen_width}x{screen_height}")
            print(f"클릭 좌표: ({abs_x}, {abs_y})")
            
            # 현재 마우스 위치 저장
            try:
                orig_x, orig_y = win32api.GetCursorPos()
                print(f"현재 마우스 위치: ({orig_x}, {orig_y})")
            except Exception as e:
                print(f"GetCursorPos 오류: {e}")
                orig_x, orig_y = 0, 0
            
            # 마우스 이동
            result = win32api.SetCursorPos((abs_x, abs_y))
            print(f"SetCursorPos 결과: {result}")
            time.sleep(0.1)
            
            # 마우스 클릭
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # 마우스 위치 복원
            try:
                win32api.SetCursorPos((orig_x, orig_y))
            except:
                pass  # 위치 복원 실패 무시
            
            return True
        except Exception as e:
            print(f"Win32 API 클릭 오류: {e}")
            return False
        
    def click_at_position_pynput(self, rel_x, rel_y):
        """pynput을 사용한 클릭 구현"""
        try:
            # pynput 설치 확인 및 설치
            try:
                from pynput.mouse import Button, Controller
            except ImportError:
                import pip
                pip.main(['install', 'pynput'])
                from pynput.mouse import Button, Controller
            
            import time
            
            if not self.is_window_valid():
                print("창이 유효하지 않습니다.")
                return False
            
            # 창 활성화
            self.activate_window()
            time.sleep(0.2)
            
            # 상대 좌표 계산
            left, top, _, _ = self.window_rect
            abs_x = left + rel_x
            abs_y = top + rel_y
            
            # 마우스 컨트롤러 생성
            mouse = Controller()
            
            # 원래 위치 저장
            original_position = mouse.position
            
            # 마우스 이동
            mouse.position = (abs_x, abs_y)
            time.sleep(0.1)
            
            # 클릭
            mouse.press(Button.left)
            time.sleep(0.1)
            mouse.release(Button.left)
            
            # 원래 위치로 복원
            mouse.position = original_position
            
            return True
        except Exception as e:
            print(f"pynput 클릭 오류: {e}")
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
            
            # 스크롤 이벤트 상수
            MOUSEEVENTF_WHEEL = 0x0800
            
            # 스크롤 방향 설정 (부호 유지)
            direction = 1 if amount > 0 else -1
            
            # 절대값으로 반복 횟수 계산
            repeat_count = abs(amount)
            # print(f"repeat_count= {repeat_count}")
            
            # 단일 스크롤 값
            single_scroll = 120 * direction # 120은 한 노치의 표준값
            
            # 여러 번 반복하여 스크롤 수행
            for _ in range(repeat_count):
                windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, single_scroll, 0)
                time.sleep(0.05)  # 각 스크롤 사이에 짧은 지연 추가
            
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