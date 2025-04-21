# tasker.py
from PySide6.QtCore import QObject, QTimer, Signal
import mss
import time
import cv2
import os
import math
import numpy as np
from typing import Dict, Any

from core.window_utils import WindowUtil
from stores.areas import *
import stores.sanner as Scanner
from zzz.config import LOOP_TEXT_KEYWORD

class Tasker(QObject):
    """
    정기적인 작업 처리를 담당하는 클래스
    스레드 대신 QTimer를 사용하여 메인 이벤트 루프에서 처리
    """
    # 시그널 정의
    status_changed = Signal(str)
    
    def __init__(self, parent, capture_manager):
        super().__init__(parent)
        
        self.capture_manager = capture_manager
        
        # 작업 상태 변수
        self.is_running = False
        
        # 이미지 매칭 및 UI 작업 타이머
        self.matching_timer = QTimer(self)
        self.matching_timer.timeout.connect(self.process_image_matching)
        
        # 공유 MSS 인스턴스
        self.sct = mss.mss()
    
    def start_tasks(self):
        """모든 작업 시작"""
        if self.is_running:
            return False
            
        self.is_running = True
        
        # 이미지 매칭 시작 (0.5초마다)
        self.matching_timer.start(Scanner.Get_LoopInterval_MS())
        
        self.status_changed.emit("Tasker: 작업이 시작되었습니다.")
        return True
    
    def stop_tasks(self):
        """모든 작업 중지"""
        if not self.is_running:
            return False
            
        self.is_running = False
        
        # 타이머 중지
        self.matching_timer.stop()
        
        self.status_changed.emit("Tasker: 작업이 중지되었습니다.")
        return True
    
    def process_image_matching(self):
        """이미지 매칭 및 UI 작업 - 매칭 타이머 콜백"""
        if not self.is_running:
            return
            
        if not WindowUtil.update_window_info():
            self.stop_tasks()
            self.status_changed.emit("창이 닫혔습니다.")
            return
        
        try:
            matching = self.match_image_in_zone(self.sct, "좌상단메뉴", "좌상단메뉴-월드맵")
            # matching = self.match_image_in_zone(self.sct, "우상단메뉴", "우상단메뉴-인벤")
            print(matching)
            
            if matching["matched"] and 85.0 <= matching["score_percent"]:
                x, y = matching["click"]
                # 클릭 요청 시그널 발생 (UI 스레드에서 처리)
                WindowUtil.click_at_position(x, y)
            
        except Exception as e:
            self.status_changed.emit(f"Tasker: 이미지 매칭 오류: {str(e)}")
    
    def match_image_in_zone(self, sct, zone_key, image_key):
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
        zoneitem = Get_ZoneArea(zone_key)
        imageitem = Get_ImageArea(image_key)
        
        if not zoneitem:
            raise ValueError(f"존재하지 않는 zone 키: {zone_key}")
        if not imageitem:
            raise ValueError(f"존재하지 않는 image 키: {image_key}")
        
        # 이미지 파일이 존재하는지 확인
        if not os.path.exists(imageitem.file):
            raise FileNotFoundError(f"템플릿 이미지가 존재하지 않음: {imageitem.file}")
        
        # 전체 화면 캡처
        full_img = self.capture_manager.capture_full_window_cv2(sct)
        if full_img is None:
            raise ValueError("화면 캡처 실패")
        
        # 템플릿 이미지 로드
        template = cv2.imread(imageitem.file, cv2.IMREAD_COLOR)
        # cv2.imwrite("debug_template_saved.png", template)   # 템플릿 이미지 저장 (디버깅용)
        
        # zone 영역 잘라내기
        zone_crop = full_img[zoneitem.y:zoneitem.y+zoneitem.height, zoneitem.x:zoneitem.x+zoneitem.width]
        
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
        
        target_x = zoneitem.x + max_loc[0]
        target_y = zoneitem.y + max_loc[1]
        
        score = float(max_val)
        score_2 = math.floor(score * 100) / 100
        score_percent = score_2 * 100.0
        
        return {
            "matched": matched,
            "score": score_2,
            "score_percent": score_percent,
            "zone": zone_key,
            "image": image_key,
            
            # "position": (target_x, target_y) if matched else None,
            # "click": (imageitem.ClickX, imageitem.ClickY) if matched else None,
            "position": (target_x, target_y),
            "click": imageitem.ClickPoint,
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
        zoneitem = Get_ZoneArea(zone_key)
        imageitem = Get_ImageArea(image_key)
        
        if None == zoneitem:
            print(f"[{zone_key}] 키에 해당하는 Zone 아이템 없음")
        if None == imageitem:
            print(f"[{image_key}] 키에 해당하는 Image 아이템 없음")
        
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"스크린샷 파일이 존재하지 않음: {screenshot_path}")
        if not os.path.exists(imageitem.file):
            raise FileNotFoundError(f"템플릿 이미지가 존재하지 않음: {imageitem.file}")
        
        full_img = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        template = cv2.imread(imageitem.file, cv2.IMREAD_COLOR)
        
        # zone 영역 잘라내기
        zone_crop = full_img[zoneitem.y:zoneitem.y+zoneitem.height, zoneitem.x:zoneitem.x+zoneitem.width]
        
        # 템플릿 매칭
        result = cv2.matchTemplate(zone_crop, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        threshold = 0.9
        matched = max_val >= threshold
        
        return {
            "matched": matched,
            "score": float(max_val),
            "zone": zone_key,
            "image": image_key,
            "position": (zoneitem.x + max_loc[0], zoneitem.y + max_loc[1]) if matched else None
        }
    
    def __del__(self):
        """소멸자"""
        self.stop_tasks()
        if hasattr(self, 'sct'):
            self.sct.close()