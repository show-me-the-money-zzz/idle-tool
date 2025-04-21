import mss
import mss.tools
import numpy as np
# import time
# import threading
# import cv2
# import os
# from datetime import datetime
from PIL import Image
from typing import Any
import math

# import core.ocr_engine_paddle as PaddleOCREngine
from stores.areas import *
from core.window_utils import WindowUtil

class CaptureManager:
    """화면 캡처 관리 클래스 (mss 라이브러리 기반)"""
    
    def __init__(self, callback_fn=None):
        self.is_capturing = False
        self.capture_thread = None
        self.callback_fn = callback_fn
        self.sct = mss.mss()
        
        # # 색상 추출 캡처 RND
        # from core.capture_util_extract import Test_Extract
        # Test_Extract()
    
    def _capture_crop(self
                    , sct: mss.mss
                    , x: int, y: int, width: int, height: int
                    ) -> np.ndarray:
        """단일 영역을 캡처하여 OpenCV 이미지로 반환"""
        left, top, _, _ = WindowUtil.get_window_rect()

        monitor = {
            "left": left + x,
            "top": top + y,
            "width": width,
            "height": height
        }
        
        try:
            screenshot = sct.grab(monitor)
        except Exception as e:
            print(f"[캡처 실패] {type(e).__name__}: {e} (monitor: {monitor})")
            return None
        
        img = np.array(screenshot)[:, :, :3]  # BGRA → BGR
        return img

    def _capture_crop_AllTextArea(self
                      , sct: mss.mss
                      ):
        """다중 영역을 한 번의 전체 창 캡처 후 잘라서 OpenCV 이미지 리스트로 반환"""
        # ret: List[np.ndarray] = []

        left, top, right, bottom = WindowUtil.get_window_rect()
        full = self._capture_crop(sct, 0, 0, right - left, bottom - top)
        
        # if None == full: return None
        
        ret = {}
        for key, item in GetAll_TextArea().items():
            cropped = full[item.y:item.y+item.height, item.x:item.x+item.width].copy()
            ret[key] = cropped
        return ret
    
    def capture_full_window(self):
        """연결된 창 전체를 캡처"""
        if not WindowUtil.is_window_valid():
            return None
        
        # 창 활성화
        WindowUtil.activate_window()
        
        # 창 위치와 크기 가져오기
        left, top, right, bottom = WindowUtil.get_window_rect()
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
    
    def capture_full_window_cv2(self, sct: mss.mss) -> np.ndarray:
        """
        연결된 창 전체를 OpenCV 형식(np.ndarray)으로 캡처합니다.
        
        이 메서드의 주요 이점:
        1. OpenCV 호환성: 이미지를 OpenCV 함수에서 바로 사용 가능한 형식(numpy 배열)으로 반환
        2. 형식 변환 최소화: PIL Image 변환 과정 없이 직접 numpy 배열 사용 가능
        3. 메모리 효율성: 불필요한 형식 변환으로 인한 추가 메모리 할당 방지
        4. 처리 속도: 이미지 처리 파이프라인에서 변환 단계를 줄여 성능 개선
        5. 일관성: 템플릿 매칭 등의 OpenCV 기반 이미지 처리에 일관된 형식 제공
        
        Returns:
            np.ndarray: OpenCV 형식의 이미지 배열(BGR 색상 순서)
            유효한 창이 없는 경우 None 반환
        """
        if not WindowUtil.is_window_valid():
            return None
        
        # 창 활성화
        WindowUtil.activate_window()
        
        # 창 위치와 크기 가져오기
        left, top, right, bottom = WindowUtil.get_window_rect()
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
        screenshot = sct.grab(monitor)
        
        # mss의 결과를 numpy 배열로 변환 (OpenCV 형식)
        img = np.array(screenshot)[:, :, :3]  # BGRA → BGR
        return img
        
    def __del__(self):
        """소멸자: mss 자원 해제"""
        if hasattr(self, 'sct'):
            self.sct.close()