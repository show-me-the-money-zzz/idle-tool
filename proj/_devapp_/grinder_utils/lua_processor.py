import os
import sys
import time
import lupa
from lupa import LuaRuntime

class LuaWindowController:
    def __init__(self):
        lua = LuaRuntime()
        lua_version = lua.eval("_VERSION")
        print(f"lua_version= {lua_version}")

        # Lua 런타임 초기화
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        
        # 모듈 경로 추가
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        scripts_dir = os.path.join(base_dir, "scripts")
        
        # Lua에 Python 함수 노출
        self.lua.globals()['py_print'] = print
        self.lua.globals()['py_sleep'] = time.sleep
        
        # Lua 스크립트 로드
        try:
            script_path = os.path.join(scripts_dir, "window_control.lua")
            
            # 스크립트 존재 확인
            if not os.path.exists(script_path):
                print(f"오류: Lua 스크립트 파일이 존재하지 않습니다: {script_path}")
                self.window_module = None
                return
                
            # 스크립트 로드
            with open(script_path, "r", encoding="utf-8") as f:
                script = f.read()
                
            # window 모듈 로드
            self.window_module = self.lua.execute(script)
            print("Lua 윈도우 컨트롤 모듈이 로드되었습니다.")
            
        except Exception as e:
            print(f"Lua 스크립트 로드 오류: {e}")
            self.window_module = None
    
    def set_target_window(self, hwnd):
        """Lua: 타겟 윈도우 설정"""
        if self.window_module is None:
            return False
        return self.window_module.set_target_window(hwnd)
    
    def is_window_valid(self):
        """Lua: 윈도우 유효성 확인"""
        if self.window_module is None:
            return False
        return self.window_module.is_window_valid()
    
    def activate_window(self):
        """Lua: 윈도우 활성화"""
        if self.window_module is None:
            return False
        return self.window_module.activate_window()
    
    def send_key(self, key):
        """Lua: 키 입력 전송"""
        if self.window_module is None:
            return False
        return self.window_module.send_key(key)
    
    def click_at_position(self, x, y):
        """Lua: 마우스 클릭"""
        if self.window_module is None:
            return False
        return self.window_module.click_at_position(x, y)
    
    def scroll_mousewheel(self, amount):
        """Lua: 마우스 휠 스크롤"""
        if self.window_module is None:
            return False
        return self.window_module.scroll_mousewheel(amount)
    
    def get_window_rect(self):
        """Lua: 윈도우 영역 반환"""
        if self.window_module is None:
            return (0, 0, 0, 0)
        return self.window_module.get_window_rect()
    
    def get_resolution(self):
        """Lua: 윈도우 해상도 반환"""
        if self.window_module is None:
            return (0, 0)
        return self.window_module.get_resolution()

# 싱글톤 인스턴스 생성
lua_window_controller = LuaWindowController()

def Test_Lua_Window_Control():
    """Lua 윈도우 컨트롤 테스트"""
    # 여기에서는 기존의 WindowUtil에서 타겟 윈도우 핸들을 가져와서 설정
    from core.window_utils import WindowUtil
    
    if WindowUtil.is_window_valid():
        # Lua 컨트롤러에 현재 타겟 윈도우 핸들 설정
        lua_window_controller.set_target_window(WindowUtil.target_hwnd)
        
        print("---------- Lua 윈도우 컨트롤 테스트 ----------")
        
        # 윈도우 활성화
        print("윈도우 활성화:", lua_window_controller.activate_window())
        
        # 해상도 정보
        width, height = lua_window_controller.get_resolution()
        print(f"윈도우 해상도: {width}x{height}")
        
        # 마우스 클릭 (중앙)
        center_x = width // 2
        center_y = height // 2
        print(f"중앙 클릭 ({center_x}, {center_y}):", lua_window_controller.click_at_position(center_x, center_y))
        
        # 키보드 입력
        print("스페이스 키 입력:", lua_window_controller.send_key("space"))
        
        # 스크롤
        print("마우스 휠 스크롤 (2):", lua_window_controller.scroll_mousewheel(2))
        
        print("----------------------------------------------")
        return True
    else:
        print("유효한 타겟 창이 없습니다. 먼저 창을 선택하세요.")
        return False
    
def Test_Lua():
    # from lupa import LuaRuntime
    # lua = LuaRuntime(unpack_returned_tuples=True)

    # # 실행 파일이든 소스 실행이든 상관없이 현재 실행 위치 기준
    # base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # script_path = os.path.join(base_dir, "scripts", "logger.lua")

    # with open(script_path, "r", encoding="utf-8") as f:
    #     logger = f.read()

    # lua.execute(logger)
    # run_print = lua.eval("Print_Lua")
    # run_print("하하호호즐겁다")

    print("사용X")