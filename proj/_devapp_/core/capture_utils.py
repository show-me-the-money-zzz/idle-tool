import mss
import mss.tools
import numpy as np
import time
import threading
import cv2
import os
from datetime import datetime
from PIL import Image
from typing import List, Tuple, Dict, Any
import math

import core.ocr_engine as OcrEngine
# import core.ocr_engine_paddle as PaddleOCREngine
from zzz.config import LOOP_TEXT_KEYWORD
from stores.areas import *
import stores.def_info as DefInfo
import stores.sanner as Scanner
from core.window_utils import WindowUtil

class CaptureManager:
    """화면 캡처 관리 클래스 (mss 라이브러리 기반)"""
    
    def __init__(self, callback_fn=None):
        self.is_capturing = False
        self.capture_thread = None
        self.callback_fn = callback_fn
        self.sct = mss.mss()
    
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

    def _capture_crops(self
                      , sct: mss.mss
                      , areas: List[Tuple[int, int, int, int]]
                      ) -> List[np.ndarray]:
        """다중 영역을 한 번의 전체 창 캡처 후 잘라서 OpenCV 이미지 리스트로 반환"""
        ret: List[np.ndarray] = []

        left, top, right, bottom = WindowUtil.get_window_rect()
        full = self._capture_crop(sct, 0, 0, right - left, bottom - top)
        
        if None == full: return None

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
                if not WindowUtil.update_window_info():
                    if self.callback_fn:
                        self.callback_fn("error", "창이 닫혔습니다.")
                    self.is_capturing = False
                    break
                
                print("")
                matching = self.match_image_in_zone(sct, "좌상단메뉴", "좌상단메뉴-월드맵")
                # matching = self.match_image_in_zone(sct, "좌상단메뉴", "좌상단메뉴-마을이동")
                print(matching)
                # print(self.match_image_in_zone(sct, "좌상단메뉴", "좌상단메뉴-마을이동"))
                
                if matching["matched"] and 85.0 <= matching["score_percent"]:
                    # click = matching["click"]
                    x, y = matching["click"]
                    # print(f"click => {x}, {y}")
                    WindowUtil.click_at_position(x, y)

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
                        text = OcrEngine.image_to_text(img)
                        # textlist = PaddleOCREngine.extract_text_list_from_image(img)
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
                            
                            DefInfo.Update_Value(KEY, text)
                            # DefInfo.Update_Values(KEY, textlist)

                    except Exception as e:
                        DefInfo.Update_Value(KEY, "")
                        # print(f"[캡처 오류] {type(e).__name__}: {str(e)}")
                        # if self.callback_fn:
                        #     self.callback_fn("error", f"오류 발생: {str(e)}")
                
                # texts = OcrEngine.images_to_text_parallel(images)
                # print(texts)
                # for item in texts:
                #     DefInfo.Update_Value("aa", item)

                # self.is_capturing = False   #DEV
                
                # 지정된 간격만큼 대기
                time.sleep(Scanner.Loop_Interval)
    
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
        
    def match_image_in_zone(self, sct: mss.mss, zone_key: str, image_key: str) -> Dict[str, Any]:
        """
        zone 영역 안에 image 이미지가 존재하는지 검사하는 OpenCV 템플릿 매칭

        Args:
            zone_key (str): zone.json 키
            image_key (str): image.json 키

        Returns:
            dict: {
                "matched": bool,
                "score": float,
                "zone": zone dict,
                "image": image dict,
                "position": (x, y)  # 전체 화면 기준 위치 (매칭 성공 시)
            }
        """
        zone = Get_ZoneArea(zone_key)
        image = Get_ImageArea(image_key)
        
        if not zone:
            raise ValueError(f"존재하지 않는 zone 키: {zone_key}")
        if not image:
            raise ValueError(f"존재하지 않는 image 키: {image_key}")
        
        # 이미지 파일이 존재하는지 확인
        if not os.path.exists(image["file"]):
            raise FileNotFoundError(f"템플릿 이미지가 존재하지 않음: {image['file']}")
        
        # 전체 화면 캡처
        full_img = self.capture_full_window_cv2(sct)
        if full_img is None:
            raise ValueError("화면 캡처 실패")
        
        # 템플릿 이미지 로드
        template = cv2.imread(image["file"], cv2.IMREAD_COLOR)        
        # cv2.imwrite("debug_template_saved.png", template)   # 템플릿 이미지 저장 (디버깅용)
        img_w, img_h = image["width"], image["height"]
        
        # zone 영역 잘라내기
        x, y, w, h = zone["x"], zone["y"], zone["width"], zone["height"]
        zone_crop = full_img[y:y+h, x:x+w]
        
        # 템플릿 매칭
        result = cv2.matchTemplate(zone_crop, template, cv2.TM_CCOEFF_NORMED)
        
        # max_val: 유사도 점수(0~1), 1에 가까울수록 정확한 매칭을 의미
        # max_loc: 매칭 점수가 가장 높은 위치의 (x, y) 좌표
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        """
        max_val (최대값):
            템플릿 매칭의 유사도 점수(similarity score)
            범위는 -1 ~ 1 (TM_CCOEFF_NORMED 방식 사용 시), 1에 가까울수록 매칭이 정확함
            템플릿 이미지가 검색 이미지의 특정 위치와 얼마나 유사한지
            보통 이 값에 임계값(threshold)을 적용하여 매칭 여부를 결정
            
        max_loc (최대값 위치):
            매칭 점수가 가장 높은 위치의 좌표(x, y)를 튜플로 제공
            검색 영역(zone_crop) 내에서의 상대적 위치
            전체 화면에서의 절대 위치를 구하려면 zone의 좌표를 더해야 함
        """
        
        threshold = 0.9
        matched = max_val >= threshold
        
        # return {
        #     "matched": matched,
        #     "score": float(max_val),
        #     "zone": zone,
        #     "image": image,
        #     "position": (x + max_loc[0], y + max_loc[1]) if matched else None
        # }
        
        target_x = x + max_loc[0]
        target_y = y + max_loc[1]
        
        score = float(max_val)
        score_2 = math.floor(score * 100) / 100
        score_percent = score_2 * 100.0
        click_x = int(target_x + (img_w * 0.5))
        click_y = int(target_y + (img_h * 0.5))
        return {
            "matched": matched,
            "score": score_2,
            "score_percent": score_percent,
            "zone": zone_key,
            "image": image_key,
            "position": (target_x, target_y) if matched else None,
            "click": (click_x, click_y) if matched else None,   # 소수점으로 클릭 시도하면 에러
        }
    
    def match_image_in_zone_with_screenshot(self, zone_key: str, image_key: str, screenshot_path: str) -> Dict[str, Any]:
        """
        저장된 스크린샷에서 zone 영역 안에 image 이미지가 존재하는지 검사

        Args:
            zone_key (str): zone.json 키
            image_key (str): image.json 키
            screenshot_path (str): 전체 캡처 이미지 경로

        Returns:
            dict: 매칭 결과
        """
        zone = Get_ZoneArea(zone_key)
        image = Get_ImageArea(image_key)
        
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"스크린샷 파일이 존재하지 않음: {screenshot_path}")
        if not os.path.exists(image["file"]):
            raise FileNotFoundError(f"템플릿 이미지가 존재하지 않음: {image['file']}")
        
        full_img = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        template = cv2.imread(image["file"], cv2.IMREAD_COLOR)
        
        # zone 영역 잘라내기
        x, y, w, h = zone["x"], zone["y"], zone["width"], zone["height"]
        zone_crop = full_img[y:y+h, x:x+w]
        
        # 템플릿 매칭
        result = cv2.matchTemplate(zone_crop, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        threshold = 0.9
        matched = max_val >= threshold
        
        return {
            "matched": matched,
            "score": float(max_val),
            "zone": zone,
            "image": image,
            "position": (x + max_loc[0], y + max_loc[1]) if matched else None
        }
        
    def __del__(self):
        """소멸자: mss 자원 해제"""
        if hasattr(self, 'sct'):
            self.sct.close()