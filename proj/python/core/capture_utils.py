from PIL import ImageGrab
import time
import threading
from datetime import datetime
from core.ocr_engine import image_to_text

class CaptureManager:
    """화면 캡처 관리 클래스"""
    
    def __init__(self, window_manager, callback_fn=None):
        self.window_manager = window_manager
        self.is_capturing = False
        self.capture_thread = None
        self.capture_interval = 1.0
        self.callback_fn = callback_fn
    
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
                
                # 화면 캡처
                screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
                
                # OCR 실행
                text = image_to_text(screenshot)
                
                # 콜백 함수 호출
                if self.callback_fn:
                    timestamp = time.strftime("%H:%M:%S", time.localtime())
                    self.callback_fn("result", f"[{timestamp}] 인식 결과:\n{text}\n{'='*50}\n")
                
            except Exception as e:
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
        
        # 화면 캡처
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        return screenshot