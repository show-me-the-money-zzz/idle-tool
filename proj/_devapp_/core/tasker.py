# tasker.py
from PySide6.QtCore import QObject, QTimer, Signal
import mss
import time
import cv2
import os
import math
import numpy as np
from typing import Dict, Any
from datetime import datetime

import asyncio
from asyncio import Future

from core.window_utils import WindowUtil
from stores.areas import *
import stores.sanner as Scanner
from core.config import LOOP_TEXT_KEYWORD
import stores.task_manager as TaskMan
from stores.task_base_step import BaseStep, TaskStep_Matching, TaskStep_MouseWheel, TaskStep_TeltegramNoti
from grinder_utils.system import GetText_NoticeLog
from core.telegram_notifier import TelegramNotifier
from core.discord_notifier import DiscordNotifier

class Tasker(QObject):
    """
    정기적인 작업 처리를 담당하는 클래스
    스레드 대신 QTimer를 사용하여 메인 이벤트 루프에서 처리
    """
    # 시그널 정의
    status_changed = Signal(str)
    
    # 로그 메시지 시그널 추가
    logframe_addlog = Signal(str)
    logframe_addlog_matching = Signal(str, str, TaskStep_Matching, float, bool)
    logframe_addlog_notmatching = Signal(str)
    logframe_addwarning = Signal(str)
    logframe_adderror = Signal(str)
    logframe_addnotice = Signal(str)
    logframe_addchnagetaskstep = Signal(str)
    
    def __init__(self, parent, toggle_capture_callback, stop_capture_callback, capture_manager):
        super().__init__(parent)
        self.async_helper = AsyncHelper(self)
        
        self.toggle_capture_callback = toggle_capture_callback
        self.stop_capture_callback = stop_capture_callback
        self.capture_manager = capture_manager
        
        # 작업 상태 변수
        self.is_running = False
        self.current_task = None
        self.noti_task = None
        
        # 공유 MSS 인스턴스
        self.sct = mss.mss()
    
    def start_tasks(self):
        """모든 작업 시작"""
        if self.is_running:
            return False
            
        self.is_running = True
        
        self.current_task = self.async_helper.run_task(self.Loop())
        self.noti_task = self.async_helper.run_task(self.Run_Notice())
        
        self.logframe_addnotice.emit("Tasker: 작업이 시작되었습니다.")
        return True
    
    def stop_tasks(self):
        """모든 작업 중지"""
        if not self.is_running:
            return False
            
        self.is_running = False
        self.running_task = None
        self.running_task_steps = []
        self.recently_stopped = True
        
        # Set a timer to clear this flag after a while
        QTimer.singleShot(2000, lambda: setattr(self, 'recently_stopped', False))
        
        # 현재 실행 중인 작업 취소
        if self.current_task:
            self.async_helper.cancel_task(self.current_task)
            # 취소된 작업이 완료될 때까지 짧게 대기 (비동기 방식)
            QTimer.singleShot(100, lambda: self._complete_stop_tasks())
            self.current_task = None
        else:
            self._complete_stop_tasks()
            
        self.Cancel_Noti()
        
        return True
    
    def _complete_stop_tasks(self):
        """작업 중지 완료 후 처리"""
        self.logframe_addnotice.emit("⛔ 작업이 중지되었습니다.")
            
    def Make_Task_GS23_RF(self): return {}
                
    def Append_RunningSteps(self, steps: list[str], logging = True):
        isupdate = False
        for step in steps:
            if step not in self.running_task_steps:
                self.running_task_steps.append(step)
                isupdate = True
        if logging and isupdate: self.Print_RunningSteps()
    
    def Print_RunningSteps(self):
        if 0 >= len(self.running_task_steps): return
        
        log = f"🎯 단계 변경: {' / '.join(self.running_task_steps)}"
        self.logframe_addchnagetaskstep.emit(log)
    
    async def Loop(self):
        task_key, task = Scanner.Get_RunningTask()
        # print(f"Tasker.Loop(): [{task_key}] {task}")
        self.running_task = task
        self.running_task_steps = [ Scanner.GetKey_StartStep() ]
        self.Print_RunningSteps()
        
        try:
            while self.is_running:
                # Check at the top of each loop if we should still be running
                if not self.is_running:
                    break
                
                if not WindowUtil.update_window_info():
                    self.logframe_addwarning.emit("창이 닫혔습니다.")
                    self.toggle_capture_callback()
                    break
                # await self.Task_GS23_RF()	# DEV TEST
				
                # 현재 실행 중인 단계 처리
                for step_key in self.running_task_steps:
                    step = self.running_task.Get_Step(step_key)
                    # print(f"step.name= {step.name}")
                    if None == step:
                        self.logframe_adderror.emit(f"{task_key}-{step_key} 단계가 유효하지 않습니다.")
                        self.toggle_capture_callback()
                        break
                    
                    # BaseStep 타입에 따라 적절한 처리 메서드 호출
                    if isinstance(step, TaskStep_Matching):
                        await self.Execute_Matching(step, task_key, step_key)
                    elif isinstance(step, TaskStep_MouseWheel):
                        await self.Execute_MouseWheel(step, task_key, step_key)
                    # elif isinstance(step, TaskStep_TeltegramNoti):
                    #     await self.Execute_TelegramNoti(step, task_key, step_key)
                    else:
                        # 기본 대기 처리 (타입에 관계없이 대기 시간이 있으면 처리)
                        await self.Execute_Waiting(step, task_key, step_key)
                
                # self.logframe_addlog.emit("foo~~")
                await self.async_helper.sleep(0)
                
            # self.logframe_adderror.emit("끝")
                
        except asyncio.CancelledError:
            # 작업 취소 처리
            self.logframe_addwarning.emit("🚫 작업이 취소되었습니다.")
            self.toggle_capture_callback()
        except Exception as e:
            # 예외 처리
            self.logframe_adderror.emit(f"🚨 오류 발생: {str(e)}")
            self.toggle_capture_callback()

    # async def Execute_Waiting(self, step: BaseStep, task_key, step_key):
    async def Execute_Waiting(self, waiting: float):
        """모든 BaseStep 공통 대기 처리"""
        if waiting > 0:
            # self.logframe_addlog.emit(f"[[[대기]]] {waiting} 초")
            await self.async_helper.sleep(waiting)
        
        # # 다음 단계 결정
        # if step.next_step and len(step.next_step) > 0:
        #     self.running_task_steps = step.next_step
        # else:
        #     self.logframe_addwarning.emit(f"다음 단계가 없어 [{task_key} - {step_key}] 에서 종료합니다.")
        #     self.toggle_capture_callback()

    async def Execute_Matching(self, step: TaskStep_Matching, task_key, step_key):
        """매칭 타입 단계 실행"""
        
        if 0 < step.waiting:
            await self.Execute_Waiting(step.waiting)
        
        # 이미지 매칭 수행
        matched = self.match_image_in_zone(step.zone, step.image)
        matched_score = matched["score_percent"]
        isSuccess = step.evaluate_score_condition(matched_score)

        self.logframe_addlog_matching.emit(task_key, step_key, step, matched_score, isSuccess)

        self.running_task_steps.remove(step_key)        
        
        # 결과에 따른 처리
        if isSuccess:
            self.Print_RunningSteps()   # 실패는 패스
            # 클릭 처리
            if step.finded_click:
                click_key = "click_image" if step.finded_click == "image" else "click_zone"
                x, y = matched[click_key]
                self.Click(x, y, f"{task_key}-{step_key}")
            
            # 다음 단계 설정
            if 0 >= len(step.next_step):
                # print(f"not next: running_task_steps= {self.running_task_steps}")
                self.logframe_addwarning.emit(f"🛑 성공 후 다음 단계가 없어 [{task_key} - {step_key}] 에서 종료합니다.")
                self.toggle_capture_callback()
            else:
                self.Append_RunningSteps(step.next_step)
        else:
            # 실패 시 처리
            if "" == step.fail_step:
                # print(f"not fail: running_task_steps= {self.running_task_steps}")
                self.logframe_addwarning.emit(f"🛑 실패 단계가 없어 [{task_key} - {step_key}] 에서 종료합니다.")
                self.toggle_capture_callback()
            else:
                self.Append_RunningSteps([ step.fail_step ], False)
                # self.Print_RunningSteps()

    async def Execute_MouseWheel(self, step: TaskStep_MouseWheel, task_key, step_key):
        """마우스휠 타입 단계 실행"""
        logtext = "🖲️ 마우스 휠: "
        
        if 0 < step.waiting:
            await self.Execute_Waiting(step.waiting)
            logtext += f"(잠깐만 {step.waiting} 초) "
        
        # 마우스 휠 동작 수행
        WindowUtil.scroll_mousewheel(step.amount)

        logtext += f"{step.amount} 만큼 스크롤"
        self.logframe_addlog_notmatching.emit(logtext)

        self.running_task_steps.remove(step_key)
        self.Print_RunningSteps()
        
        # 다음 단계 설정
        if 0 >= len(step.next_step):
            self.logframe_addwarning.emit(f"🛑 다음 단계가 없어 [{task_key} - {step_key}] 에서 종료합니다.")
            self.toggle_capture_callback()
        else:
            self.Append_RunningSteps(step.next_step)

    # async def Execute_TelegramNoti(self, step: TaskStep_TeltegramNoti, task_key, step_key):
    #     """텔레그램 알림 타입 단계 실행"""
        
    #     await self.Execute_Waiting(step.waiting)
        
    #     if step.dummy:
    #         self.logframe_addlog_notmatching.emit(f"[[[텔레그램 알림]]] 더미 모드 - 실제 전송 안함")
    #     else:
    #         self.logframe_addlog_notmatching.emit(f"[[[텔레그램 알림]]] 메시지 전송")
    #         # 실제 텔레그램 메시지 전송 코드 (구현 필요)
    #         # TODO: 텔레그램 API 연동 코드 추가

    #     self.running_task_steps.remove(step_key)
    #     self.Print_RunningSteps()
        
    #     # 다음 단계 설정
    #     if step.next_step and len(step.next_step) > 0:
    #         self.Append_RunningSteps(step.next_step)
    #     else:
    #         self.logframe_addwarning.emit(f"🛑 다음 단계가 없어 [{task_key} - {step_key}] 에서 종료합니다.")
    #         self.toggle_capture_callback()
        
    repeat_timer = None
    telenoti = None
    discordnoti = None
    async def Run_Notice(self):
        return
    
        # print(datetime.now())
        if not self.repeat_timer:
            from grinder_utils.repeat_timer import RepeatTimer
            # self.repeat_timer = RepeatTimer(10 * 60)
            # self.repeat_timer = RepeatTimer(5)
            self.repeat_timer = RepeatTimer(1 * 60)
        self.send_noti()
        
        try: #pass
            while self.is_running:
                # 알림 항목마다 제각각의 대기시간으로 알리기
                
                if self.repeat_timer.is_due():
                    # print("tick")
                    # # break
                    self.send_noti()
                # else: print(self.repeat_timer.get_remaining_time())
                
                await self.async_helper.sleep(0.1)
            
        except asyncio.CancelledError:
            # 작업 취소 처리
            self.logframe_addwarning.emit("🚫 작업이 취소되었습니다.")
        except Exception as e:
            # 예외 처리
            # print(f"fail: error= {e}")
            self.Cancel_Noti()
            
    def send_noti(self):
        # print(f"send_noti()1: {self.telenoti} / {self.discordnoti}")
        if not self.telenoti:            
            self.telenoti = TelegramNotifier("7734048311:AAHa9GsavYBMAOOpMVXnzF9gsfqWOH7tWKc", "-1002515704043")
            
        if not self.discordnoti:            
            self.discordnoti = DiscordNotifier("https://discord.com/api/webhooks/1371429465825218591/cgDpAInWxdAO3FCHBHLPkdH-1Cvyvm_n2RTnKpAaxsOqGR4CJb6C4IEqzqGj2OgqC5Lj")
        # print(f"send_noti()2: {self.telenoti} / {self.discordnoti}")
      
        title = "스탯 알림" # 다이아 알림 / 스탯 알림
        zone = "캐릭 스탯 정보" # 텔레그램알림용-다이아 / 캐릭 스탯 정보
        server = "엘머5"    # 웰즈5 / 엘머5
        nickname = "마루이모"   # 멜라닝 / 마루이모
        comment = "부캐입니다요"  # 본계정입니다 / 부캐입니다요
        
        message_teltgram = TelegramNotifier.Make_Message(title, server, nickname, comment)
        self.telenoti.send_area_screenshot(zone, message_teltgram)
        self.logframe_addnotice.emit(GetText_NoticeLog("텔레그램", title))
        
        message_discord = DiscordNotifier.Make_Message(title, server, nickname, comment)
        self.discordnoti.send_area_screenshot(zone, message_discord)
        self.logframe_addnotice.emit(GetText_NoticeLog("디스코드", title))
        
        self.repeat_timer.update_next_time()
    
    def Cancel_Noti(self):
        if self.noti_task:
            self.async_helper.cancel_task(self.noti_task)
            self.noti_task = None
    
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
        
        # zone 영역 잘라내기
        zone_crop = full_img[
            zoneitem.y : zoneitem.y + zoneitem.height,
            zoneitem.x : zoneitem.x + zoneitem.width
        ]

        # # 템플릿 이미지 저장 (디버깅용)
        # cv2.imwrite("match_full.png", full_img)
        # cv2.imwrite("match_zone.png", zone_crop)
        # cv2.imwrite("match_image.png", template)
        
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
        # print(f"target position: {target_x}, {target_y}")
        
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
            "click_image": imageitem.GetClickPoint_byApp(target_x, target_y),
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
        logtext = f"🖱️ 마우스 클릭: ({x}, {y})"
        if "" != caller: logtext += f" {caller}"
        self.logframe_addlog_notmatching.emit(logtext)
    
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
            # 콜백 추가하지 않음 (타이밍 문제 해결)
            # future.add_done_callback(lambda f: self.process_asyncio())
        
    async def sleep(self, seconds):
        """비동기 대기 - 재구현"""
        try:
            # QTimer 대신 asyncio.sleep 사용
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            # 취소 처리
            raise