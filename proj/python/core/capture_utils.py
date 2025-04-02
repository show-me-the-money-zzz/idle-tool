import mss
import mss.tools
import numpy as np
import time
import threading
from datetime import datetime
from PIL import Image
from core.ocr_engine import image_to_text

class CaptureManager:
    """화면 캡처 관리 클래스 (mss 라이브러리 기반)"""
    
    def __init__(self, window_manager, callback_fn=None):
        self.window_manager = window_manager
        self.is_capturing = False
        self.capture_thread = None
        self.capture_interval = 1.0
        self.callback_fn = callback_fn
        # mss 인스턴스 생성
        self.sct = mss.mss()
    
    def start_capture(self, x, y, width, height, interval=1.0):
        """캡처 시작"""
        if self.is_capturing:
            return False
        
        self.capture_interval = interval
        self.is_capturing = True
        
        # 캡처 파라미터 저장
        self.capture_params = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        
        # 새 스레드에서 캡처 실행
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        return True
    
    def stop_capture(self):
        """캡처 중지"""
        self.is_capturing = False
        return True
    
    def capture_loop(self):
        """캡처 루프 실행"""
        # 각 스레드에서 새로운 MSS 인스턴스를 생성
        with mss.mss() as sct:
            while self.is_capturing:
                try:
                    # 창이 여전히 존재하는지 확인
                    if not self.window_manager.update_window_info():
                        if self.callback_fn:
                            self.callback_fn("error", "창이 닫혔습니다.")
                        self.is_capturing = False
                        break
                    
                    # 윈도우 위치 가져오기
                    left, top, _, _ = self.window_manager.get_window_rect()
                    
                    # 상대 좌표로 입력된 값을 절대 좌표로 변환
                    x = self.capture_params['x'] + left
                    y = self.capture_params['y'] + top
                    width = self.capture_params['width']
                    height = self.capture_params['height']
                    
                    # 디버깅 정보 출력
                    # print(f"캡처 영역: x={x}, y={y}, width={width}, height={height}")
                    
                    # 화면 캡처 (스레드 로컬 MSS 인스턴스 사용)
                    monitor = {
                        "top": y,
                        "left": x,
                        "width": width,
                        "height": height
                    }
                    screenshot = sct.grab(monitor)
                    
                    # mss의 결과를 PIL Image로 변환
                    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                    
                    # OCR 실행
                    text = image_to_text(img)
                    
                    # 디버깅 정보 출력
                    # print(f"인식된 텍스트: {text}")
                    
                    # 콜백 함수 호출
                    if self.callback_fn:
                        timestamp = time.strftime("%H:%M:%S", time.localtime())
                        # self.callback_fn("result", f"[{timestamp}] 인식 결과:\n{text}\n{'='*50}\n")
                        logtext = f"[{timestamp}] {text}";
                        if not text:
                            logtext += "\n";
                        self.callback_fn("result", logtext)
                    
                except Exception as e:
                    # print(f"캡처 오류 발생: {str(e)}")
                    if self.callback_fn:
                        self.callback_fn("error", f"오류 발생: {str(e)}")
                
                # 지정된 간격만큼 대기
                time.sleep(self.capture_interval)
    
    def capture_full_window(self):
        """연결된 창 전체를 캡처"""
        if not self.window_manager.is_window_valid():
            return None
        
        # 창 활성화
        self.window_manager.activate_window()
        
        # 창 위치와 크기 가져오기
        left, top, right, bottom = self.window_manager.get_window_rect()
        width = right - left
        height = bottom - top
        
        # mss로 화면 캡처 영역 정의
        monitor = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        
        # 화면 캡처
        screenshot = self.sct.grab(monitor)
        
        # mss의 결과를 PIL Image로 변환
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img
    
    def __del__(self):
        """소멸자: mss 자원 해제"""
        if hasattr(self, 'sct'):
            self.sct.close()