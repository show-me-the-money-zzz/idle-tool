# tasker.py
from PySide6.QtCore import QObject, QTimer, Signal
import mss
import time
import cv2
import os
import math
import numpy as np
from typing import Dict, Any

import asyncio
from asyncio import Future

from core.window_utils import WindowUtil
from stores.areas import *
import stores.sanner as Scanner
from zzz.config import LOOP_TEXT_KEYWORD
import zzz.hotkey as HotKey
import stores.task_manager as TaskMan

class Tasker(QObject):
    """
    정기적인 작업 처리를 담당하는 클래스
    스레드 대신 QTimer를 사용하여 메인 이벤트 루프에서 처리
    """
    # 시그널 정의
    status_changed = Signal(str)
    
    # 로그 메시지 시그널 추가
    logframe_addlog = Signal(str)
    logframe_addwarning = Signal(str)
    logframe_adderror = Signal(str)
    logframe_addnotice = Signal(str)
    
    def __init__(self, parent, capture_manager):
        super().__init__(parent)
        self.async_helper = AsyncHelper(self)
        
        self.capture_manager = capture_manager
        
        # 작업 상태 변수
        self.is_running = False
        self.current_task = None
        
        # 공유 MSS 인스턴스
        self.sct = mss.mss()
    
    def start_tasks(self):
        """모든 작업 시작"""
        if self.is_running:
            return False
            
        self.is_running = True
        
        self.current_task = self.async_helper.run_task(self.Loop())
        
        self.logframe_addnotice.emit("Tasker: 작업이 시작되었습니다.")
        return True
    
    def stop_tasks(self):
        """모든 작업 중지"""
        if not self.is_running:
            return False
            
        self.is_running = False
        
        # 현재 실행 중인 작업 취소
        if self.current_task:
            self.async_helper.cancel_task(self.current_task)
            self.current_task = None
        
        self.logframe_addnotice.emit("Tasker: 작업이 중지되었습니다.")
        return True
    
    async def Task_GS23_RF(self):
        limit_score = 50
        
        try:
            matched = self.match_image_in_zone("메뉴_좌상", "메뉴_좌상-맵")
            # matching = self.match_image_in_zone("우상단메뉴", "우상단메뉴-인벤")
            # print(matched)
            score = matched["score_percent"]
            if limit_score <= score:
                self.logframe_addlog.emit(f"ZONE:{matched['zone']}에서 IMG:{matched['image']} 찾음 ({score:.1f}%)")
            
            # if matching["matched"] and limit_score <= score:
            if limit_score <= score:
                x, y = matched["click"]
                # 클릭 요청 시그널 발생 (UI 스레드에서 처리)
                WindowUtil.click_at_position(x, y)
                self.logframe_addlog.emit(f"마우스 클릭 ({x}, {y})")
                
            # matched = self.match_image_in_zone("메뉴_마을", "메뉴_마을-잡화")
            # # matched = self.match_image_in_zone(self.sct, "우상단메뉴", "우상단메뉴-인벤")
            # self.logframe_addlog.emit(f"{matched}")
            # # score = matched["score_percent"]
            # # self.logframe_addnotice.emit("ㅋㅋㅋ")
            
            # if 50 <= score:

            # matched = self.match_image_in_zone("마을상인메뉴", "마을상인-잡화")
            # # print(matched)
            # self.logframe_addlog.emit(f"{matched}")
            # matched = self.match_image_in_zone("마을상인메뉴", "마을상인-창고")
            # self.logframe_addlog.emit(f"{matched}")
        
        except Exception as e:
            self.logframe_adderror.emit(f"이미지 매칭 오류: {str(e)}")
            
    def Make_Task_GS23_RF(self): return {}
    
    running_task = None
    running_task_steps = []
    async def Loop(self):
        # self.logframe_adderror.emit("시작")
        task_key = "사냥1"
        hunting_tasks = TaskMan.Get_Task(task_key)
        # print(f"{hunting_tasks}")
        self.running_task = hunting_tasks
        self.running_task_steps = [ hunting_tasks.start_key ]
        
        try:
            while self.is_running:
                if not WindowUtil.update_window_info():
                    self.stop_tasks()
                    self.status_changed.emit("창이 닫혔습니다.")
                    return
                
                # await self.Task_GS23_RF()

                for step_key in self.running_task_steps:
                    step = self.running_task.Get_Step(step_key)
                    if None == step:
                        self.stop_tasks()
                        self.logframe_adderror.emit(f"{task_key}-{step_key} 단계가 유효하지 않습니다.")

                    if "matching" == step.type: await self.Matching(step, task_key, step_key)
                    elif "waiting" == step.type: await self.Waiting(step)
                
                # self.logframe_addlog.emit("foo~~")
                await self.async_helper.sleep(0)
                
            # self.logframe_adderror.emit("끝")
                
        except asyncio.CancelledError:
            # 작업 취소 처리
            self.logframe_addwarning.emit("작업이 취소되었습니다.")
        except Exception as e:
            # 예외 처리
            self.logframe_adderror.emit(f"작업 중 오류 발생: {str(e)}")
            
    async def Matching(self, step: TaskMan.TaskStep, taskkey, stepkey):
        if 0.0 < step.waiting:
            self.logframe_addlog.emit(f"[[잠깐]] {step.waiting} 초")
            await self.async_helper.sleep(step.waiting)
        
        matched = self.match_image_in_zone(step.zone, step.image)
        matched_score = matched["score_percent"]
        isSuccess = step.evaluate_score_condition(matched_score)
        
        resulttext = "성공" if isSuccess else "실패"
        self.logframe_addlog.emit(f"[[매칭]] {step.zone} ZONE의 {step.image} IMAGE 근접도 {step.Print_Score()}: {matched_score}%로 {resulttext}")
        
        if isSuccess:
            if "" != step.finded_click:
                click_key = "click_image" if "image" == step.finded_click else "click_zone"
                x, y = matched[click_key]
                # 클릭 요청 시그널 발생 (UI 스레드에서 처리)
                self.Click(x, y, f"{taskkey}-{stepkey}")

            self.running_task_steps = step.next_step
        else:
            self.running_task_steps = [ step.fail_step ]
            
    async def Waiting(self, step: TaskMan.TaskStep):
        self.logframe_addlog.emit(f"<잠깐대기> {step.waiting} 초")
        
        await self.async_helper.sleep(step.waiting)
    
    def match_image_in_zone(self, zone_key, image_key):
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
        full_img = self.capture_manager.capture_full_window_cv2(self.sct)
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
        
        # threshold = limit_score * 0.01
        # matched = max_val >= threshold
        
        target_x = zoneitem.x + max_loc[0]
        target_y = zoneitem.y + max_loc[1]
        
        score = float(max_val)
        score_2 = math.floor(score * 100) / 100
        score_percent = score_2 * 100.0
        
        return {
            # "matched": matched,
            "score": score_2,
            "score_percent": score_percent,
            "zone": zone_key,
            "image": image_key,
            
            # "position": (target_x, target_y) if matched else None,
            # "click": (imageitem.ClickX, imageitem.ClickY) if matched else None,
            "position": (target_x, target_y),
            
            "click_zone": zoneitem.ClickPoint,
            "click_image": imageitem.ClickPoint,
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

    def Click(self, x, y, caller=""):
        WindowUtil.click_at_position(x, y)
        logtext = f"[[마우스 클릭]] ({x}, {y})"
        if "" != caller: logtext += f" {caller}"
        self.logframe_addlog.emit(logtext)
    
    def __del__(self):
        """소멸자"""
        self.stop_tasks()
        if hasattr(self, 'sct'):
            self.sct.close()
            
class AsyncHelper(QObject):
    """PySide6와 asyncio 통합을 돕는 헬퍼 클래스"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loop = asyncio.get_event_loop()
        
        # 비동기 작업을 처리할 타이머
        self.async_timer = QTimer(self)
        self.async_timer.timeout.connect(self.process_asyncio)
        self.async_timer.start(10)  # 10ms 간격으로 asyncio 이벤트 루프 처리
        
    def process_asyncio(self):
        """asyncio 이벤트 루프 처리"""
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        
    def run_task(self, coro):
        """코루틴 실행"""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)
    
    def cancel_task(self, future):
        """안전하게 작업 취소"""
        if future and not future.done():
            future.cancel()
            # 취소 후 처리를 위한 콜백 추가
            future.add_done_callback(lambda f: self.process_asyncio())
        
    async def sleep(self, seconds):
        """비동기 대기 - 재구현"""
        try:
            # QTimer 대신 asyncio.sleep 사용
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            # 취소 처리
            raise