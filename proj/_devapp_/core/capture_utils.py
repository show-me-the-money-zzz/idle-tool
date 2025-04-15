import mss
import mss.tools
import numpy as np
import time
import threading
from datetime import datetime
from PIL import Image
from typing import List, Tuple

import core.ocr_engine as OcrEngine
import core.ocr_engine_paddle as PaddleOCREngine
from zzz.config import LOOP_TEXT_KEYWORD
from stores.areas import *
import stores.def_info as DefInfo
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
    
    def _capture_crop(self
                    , sct: mss.mss
                    , x: int, y: int, width: int, height: int
                    ) -> np.ndarray:
        """단일 영역을 캡처하여 OpenCV 이미지로 반환"""
        left, top, _, _ = self.window_manager.get_window_rect()

        monitor = {
            "left": left + x,
            "top": top + y,
            "width": width,
            "height": height
        }
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)[:, :, :3]  # BGRA → BGR
        return img

    def _capture_crops(self
                      , sct: mss.mss
                      , areas: List[Tuple[int, int, int, int]]
                      ) -> List[np.ndarray]:
        """다중 영역을 한 번의 전체 창 캡처 후 잘라서 OpenCV 이미지 리스트로 반환"""
        ret: List[np.ndarray] = []

        left, top, right, bottom = self.window_manager.get_window_rect()
        full = self._capture_crop(sct, 0, 0, right - left, bottom - top)

        for x, y, width, height in areas:
            cropped = full[y:y+height, x:x+width].copy()
            ret.append(cropped)

        return ret
    
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

                # images = []
                for n in range(len(LOOP_TEXT_KEYWORD)):
                    KEY = LOOP_TEXT_KEYWORD[n]
                    
                    try:
                        area = Get_TextArea(KEY)
                        if area is None:
                            continue

                        img = self._capture_crop(sct, area['x'], area['y'], area['width'], area['height'])
                        # imgs = self._capture_crops(sct, [ [area['x'], area['y'], area['width'], area['height']] ])
                        # img = imgs[0]

                        # OCR 실행
                        if img is None:
                            raise ValueError("캡처된 이미지가 None입니다.")
                        # text = OcrEngine.image_to_text(img)
                        textlist = PaddleOCREngine.extract_text_list_from_image(img)
                        # print(textlist)
                        del img
                        import gc; gc.collect()
                        # text = "" # DEV.. ORC 처리 주석 처리시 사용
                        # images.append(img)
                    
                        # 디버깅 정보 출력
                        # print(f"인식된 텍스트: {text}")
                        
                        # 콜백 함수 호출
                        if self.callback_fn:
                            timestamp = time.strftime("%H:%M:%S", time.localtime())
                        # self.callback_fn("result", f"[{timestamp}] 인식 결과:\n{text}\n{'='*50}\n")
                            # logtext = f"[{timestamp}] {KEY}: {text}"
                            # if not text:
                            #     logtext += "\n"
                            # # self.callback_fn("result", logtext)
                            
                            # DefInfo.Update_Value(KEY, text)
                            DefInfo.Update_Values(KEY, textlist)

                    except Exception as e:
                        DefInfo.Update_Value(KEY, "")
                        # print(f"[캡처 오류] {type(e).__name__}: {str(e)}")
                        # if self.callback_fn:
                        #     self.callback_fn("error", f"오류 발생: {str(e)}")
                
                # texts = OcrEngine.images_to_text_parallel(images)
                # print(texts)
                # for item in texts:
                #     DefInfo.Update_Value("aa", item)

                # 지정된 간격만큼 대기
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