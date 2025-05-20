-- window_control.lua
-- Lua에서 직접 윈도우 이벤트 함수 구현

local ffi = require("ffi")

-- Windows API 함수 정의
ffi.cdef[[
    typedef void* HWND;
    typedef unsigned long DWORD;
    typedef long LONG;
    typedef int BOOL;
    
    typedef struct {
        LONG x;
        LONG y;
    } POINT;
    
    HWND GetForegroundWindow();
    BOOL SetForegroundWindow(HWND hWnd);
    BOOL GetWindowRect(HWND hWnd, RECT* lpRect);
    BOOL SetCursorPos(int X, int Y);
    BOOL GetCursorPos(POINT* lpPoint);
    void mouse_event(DWORD dwFlags, DWORD dx, DWORD dy, DWORD dwData, DWORD dwExtraInfo);
    BOOL ShowWindow(HWND hWnd, int nCmdShow);
    BOOL IsWindow(HWND hWnd);
    BOOL IsIconic(HWND hWnd);
    
    typedef struct {
        LONG left;
        LONG top;
        LONG right;
        LONG bottom;
    } RECT;
    
    short GetAsyncKeyState(int vKey);
    BOOL keybd_event(BYTE bVk, BYTE bScan, DWORD dwFlags, DWORD dwExtraInfo);
]]

-- C 라이브러리 로드
local user32 = ffi.load("user32")
local kernel32 = ffi.load("kernel32")

-- 상수 정의
local SW_RESTORE = 9
local SW_SHOW = 5
local MOUSEEVENTF_LEFTDOWN = 0x0002
local MOUSEEVENTF_LEFTUP = 0x0004
local MOUSEEVENTF_WHEEL = 0x0800
local KEYEVENTF_KEYDOWN = 0x0000
local KEYEVENTF_KEYUP = 0x0002

-- 전역 변수
local target_hwnd = nil
local window_rect = {left = 0, top = 0, right = 0, bottom = 0}

-- 가상 키 코드 매핑
local VK_CODES = {
    ["enter"] = 0x0D,
    ["space"] = 0x20,
    ["tab"] = 0x09,
    ["backspace"] = 0x08,
    ["esc"] = 0x1B,
    -- 추가 키 코드는 필요에 따라 확장
}

-- 윈도우 함수 구현
local window = {}

-- 타겟 윈도우 설정
function window.set_target_window(hwnd)
    target_hwnd = hwnd
    return window.update_window_info()
end

-- 윈도우 정보 업데이트
function window.update_window_info()
    if target_hwnd == nil or user32.IsWindow(target_hwnd) == 0 then
        return false
    end
    
    local rect = ffi.new("RECT")
    if user32.GetWindowRect(target_hwnd, rect) ~= 0 then
        window_rect.left = rect.left
        window_rect.top = rect.top
        window_rect.right = rect.right
        window_rect.bottom = rect.bottom
        return true
    end
    
    return false
end

-- 윈도우 영역 반환
function window.get_window_rect()
    return window_rect.left, window_rect.top, window_rect.right, window_rect.bottom
end

-- 윈도우 해상도 반환
function window.get_resolution()
    return window_rect.right - window_rect.left, window_rect.bottom - window_rect.top
end

-- 윈도우 유효성 확인
function window.is_window_valid()
    return target_hwnd ~= nil and user32.IsWindow(target_hwnd) ~= 0
end

-- 윈도우 활성화
function window.activate_window()
    if not window.is_window_valid() then
        return false
    end
    
    -- 최소화된 경우 복원
    if user32.IsIconic(target_hwnd) ~= 0 then
        user32.ShowWindow(target_hwnd, SW_RESTORE)
        -- 약간의 대기 시간
        os.execute("sleep 0.3")
    end
    
    -- 윈도우 표시
    user32.ShowWindow(target_hwnd, SW_SHOW)
    os.execute("sleep 0.2")
    
    -- 포그라운드로 설정
    user32.SetForegroundWindow(target_hwnd)
    os.execute("sleep 0.3")
    
    return true
end

-- 키 입력 전송
function window.send_key(key)
    if not window.activate_window() then
        return false
    end
    
    -- 키 코드 찾기
    local vk_code
    if #key == 1 then
        -- 단일 문자인 경우 ASCII 값 사용
        vk_code = string.byte(key:upper())
    else
        -- 특수 키인 경우 매핑된 값 사용
        vk_code = VK_CODES[key:lower()]
    end
    
    if not vk_code then
        return false
    end
    
    -- 키 다운 이벤트
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYDOWN, 0)
    os.execute("sleep 0.1")
    
    -- 키 업 이벤트
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    
    return true
end

-- 마우스 클릭
function window.click_at_position(rel_x, rel_y)
    if not window.is_window_valid() then
        return false
    end
    
    -- 윈도우 활성화
    window.activate_window()
    os.execute("sleep 0.1")
    
    -- 절대 좌표 계산
    local abs_x = window_rect.left + rel_x
    local abs_y = window_rect.top + rel_y
    
    -- 현재 마우스 위치 저장
    local orig_pt = ffi.new("POINT")
    user32.GetCursorPos(orig_pt)
    
    -- 커서 이동
    user32.SetCursorPos(abs_x, abs_y)
    os.execute("sleep 0.1")
    
    -- 마우스 다운 이벤트
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    os.execute("sleep 0.1")
    
    -- 마우스 업 이벤트
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    os.execute("sleep 0.1")
    
    -- 원래 커서 위치로 복원
    user32.SetCursorPos(orig_pt.x, orig_pt.y)
    
    return true
end

-- 마우스 휠 스크롤
function window.scroll_mousewheel(amount)
    if not window.is_window_valid() then
        return false
    end
    
    -- 윈도우 활성화
    window.activate_window()
    
    -- 현재 마우스 위치 저장
    local orig_pt = ffi.new("POINT")
    user32.GetCursorPos(orig_pt)
    
    -- 윈도우 중앙 좌표 계산
    local center_x = math.floor((window_rect.left + window_rect.right) / 2)
    local center_y = math.floor((window_rect.top + window_rect.bottom) / 2)
    
    -- 커서를 중앙으로 이동
    user32.SetCursorPos(center_x, center_y)
    os.execute("sleep 0.1")
    
    -- 스크롤 방향 설정
    local direction = 1
    if amount < 0 then
        direction = -1
    end
    
    -- 스크롤 횟수
    local repeat_count = math.abs(amount)
    
    -- 스크롤 수행
    for i = 1, repeat_count do
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, 120 * direction, 0)
        os.execute("sleep 0.05")
    end
    
    -- 원래 커서 위치로 복원
    user32.SetCursorPos(orig_pt.x, orig_pt.y)
    
    return true
end

-- 모듈 반환
return window