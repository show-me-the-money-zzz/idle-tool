import mss
import mss.tools
import numpy as np
import time
import threading
from datetime import datetime
from PIL import Image
from core.ocr_engine import image_to_text

from zzz.config import LOOP_TEXT_KEYWORD
from stores.areas import *
from stores.def_info import Update_Value
import core.sanner as Scanner

class CaptureManager:
    """화면 캡처 관리 클래스 (mss 라이브러리 기반)"""
    
    def __init__(self, window_manager, callback_fn=None):
        self.window_manager = window_manager
        self.is_capturing = False
        self.capture_thread = None
        self.callback_fn = callback_fn
        # mss 인스턴스 생성
        self.sct = mss.mss()
    
    # , x, y, width, height,
    def start_capture(self):
        """캡처 시작"""
        if self.is_capturing:
            return False
        
        self.is_capturing = True
        
        # # 캡처 파라미터 저장
        # self.capture_params = {
        #     'x': 0,
        #     'y': 0,
        #     'width': 0,
        #     'height': 0
        # }
        
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
                # 창이 여전히 존재하는지 확인
                if not self.window_manager.update_window_info():
                    if self.callback_fn:
                        self.callback_fn("error", "창이 닫혔습니다.")
                    self.is_capturing = False
                    break

                for n in range(len(LOOP_TEXT_KEYWORD)):
                    KEY = LOOP_TEXT_KEYWORD[n];
                    
                    try:
                        area = Get_TextArea(KEY)
                        if area is None:
                            continue

                        # 윈도우 위치 가져오기
                        left, top, _, _ = self.window_manager.get_window_rect()
                        x = left + area['x']
                        y = top + area['y']
                        width = area['width']
                        height = area['height']

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
                        if img is None:
                            raise ValueError("캡처된 이미지가 None입니다.")
                        text = image_to_text(img)
                        del img
                        import gc; gc.collect()
                        # test = "" # DEV.. ORC 처리 주석 처리시 사용
                    
                        # 디버깅 정보 출력
                        # print(f"인식된 텍스트: {text}")
                        
                        # 콜백 함수 호출
                        if self.callback_fn:
                            timestamp = time.strftime("%H:%M:%S", time.localtime())
                        # self.callback_fn("result", f"[{timestamp}] 인식 결과:\n{text}\n{'='*50}\n")
                            logtext = f"[{timestamp}] {KEY}: {text}"
                            if not text:
                                logtext += "\n"
                            # self.callback_fn("result", logtext)
                            
                            Update_Value(KEY, text)

                    except Exception as e:
                        Update_Value(KEY, "")
                        # print(f"[캡처 오류] {type(e).__name__}: {str(e)}")
                        # if self.callback_fn:
                        #     self.callback_fn("error", f"오류 발생: {str(e)}")
                
                # 지정된 간격만큼 대기
                # print(f"Loop_Interval= {Scanner.Loop_Interval}")
                time.sleep(Scanner.Loop_Interval)
    
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