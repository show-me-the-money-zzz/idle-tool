from dataclasses import dataclass
from typing import Optional
from PySide6.QtWidgets import QListWidget

import copy

from stores.task_base_step import BaseStep, TaskStep_Matching, TaskStep_MouseWheel, TaskStep_TeltegramNoti
import stores.task_manager as TaskMan

@dataclass
class SelectedTask:
    origin_key: str #task의 이름 변경 대비 (사냥1이 origin_key / 사냥XX current_key)
    current_key: str    
    task: Optional[TaskMan.Task]    # deepcopy(task) 컨트롤 변경을 일일이 업데이트
    # task: TaskMan.Task | None
    origin_step_key: str    #step의 이름 변경 대비 (잡화상점찾기 origin_step_key / 잡화상점찾기가기 current_step_key)
    current_step_key: str
    
    # # 변경 전에 저장된 데이터 있는지 확인
    # ## selected_originkey 가 원본에 없는 key이면 추가
    # ## 있는 key면 selected_currentkey / selected_currenttask으로 비교해서 변경사항 추적
    def Set_Task(self, key, task: TaskMan.Task | None):
        # print(f"Set_Task({key})")
        self.origin_key = key
        self.current_key = key
        if task:
            self.task = copy.deepcopy(task)
            # print(f"{task}")
        else: self.task = None
    def Reset_Task(self):
        self.Set_Task("", None)
        self.Reset_Step()
    def ChangeKey_CurrentTask(self, key):
        self.current_key = key
    def Get_Keys(self):
        return ( self.origin_key, self.current_key )
        
    def Get_StartKey(self): return self.task.start_key
    def Get_Commnet(self): return self.task.comment

    def IsSelect(self): return "" != self.origin_key
    def IsSame_Key(self): return (self.origin_key == self.current_key)

    def Set_StepKey(self, key):
        # print(f"SelectedTask.Set_StepKey({key})")
        self.origin_step_key = key
        self.current_step_key = key
        return self.Get_Step()
    def Get_StepKeys(self):
        return ( self.origin_step_key, self.current_step_key )
    def Reset_Step(self): self.Set_StepKey("")
    def ChangeKey_CurrentStep(self, key):
        self.current_step_key = key
    def Get_Step(self): #origin_step_key로 가져오기
        if "" == self.origin_step_key:
            return None
        return self.task.Get_Step(self.origin_step_key)
    def IsSelectStep(self): return "" != self.origin_step_key
    def IsExistStep(self, stepkey):
        return (None != self.task.steps.get(stepkey))
    def IsSame_StepKey(self):
        return (self.origin_step_key == self.current_step_key)
    def Swap_StepKey(self):
        # 키가 존재하는지 확인
        if self.origin_step_key in self.task.steps:
            # 시작 키 업데이트
            if self.origin_step_key == self.task.start_key:
                self.task.start_key = self.current_step_key
                
            # 순서 유지를 위해 순서대로 복사할 새 딕셔너리 생성
            newdata = {}
            
            # 먼저 원본 딕셔너리의 키 목록을 가져옴
            original_keys = list(self.task.steps.keys())
            # print(f"{original_keys}")
            
            # 다른 단계의 참조(fail_step, next_step) 업데이트
            for key, value in self.task.steps.items():
                if self.origin_step_key == value.fail_step:
                    value.fail_step = self.current_step_key
                    
                for nextIdx, nextVal in enumerate(value.next_step):
                    if self.origin_step_key == nextVal:
                        value.next_step[nextIdx] = self.current_step_key
            
            # 원래 순서대로 새 딕셔너리 생성
            for key in original_keys:
                if key == self.origin_step_key:
                    # 변경할 키는 새 키로 대체
                    newdata[self.current_step_key] = self.task.steps[key]
                else:
                    # 다른 키는 그대로 복사
                    newdata[key] = self.task.steps[key]
            
            # 새 딕셔너리로 교체
            self.task.steps = newdata
            # print(f"{list(newdata.keys())}")
            return self.task.steps
        return None
    
    def RemoveTask(self, key):
        # print(f"RemoveTask({key})")
        self.Reset_Task()
    
    def UpdateTask_Key(self, key):
        if "" == self.origin_key:
            return
        self.ChangeKey_CurrentTask(key)
        # print(f"task key: {self.origin_key} vs {self.current_key}")
    def UpdateTask_Comment(self, text):
        if "" == self.origin_key:
            return
        self.task.comment = text
        # print(f"{self.task}")
    def UpdateTask_StartStepKey(self, checked):
        # print(f"StartStepKey({checked})")
        if "" == self.origin_key or "" == self.origin_step_key:
            return ""
        # print(f"StartStepKey({checked}): {self.origin_step_key}")
        self.task.start_key = self.origin_step_key
        return self.task.start_key
    
    def Get_Step_LastSeq(self):
        seq = -1
        if 0 < len(self.task.steps):
            for k, step in self.task.steps.items():
                if seq < step.seq: seq = step.seq
        return seq
    
    def NewStep(self, key, step_type="matching", seq=0):
        """새 단계 생성"""
        self.task.steps[key] = TaskMan.Create_Empty_Step(step_type, seq)
        return seq
    
    def RemoveStep(self, key):
        # print(f"RemoveStep({key})")
        if "" != key:
            self.task.steps.pop(key)

            for _, stepvalue in self.task.steps.items():
                if key == stepvalue.fail_step:
                    stepvalue.fail_step = ""

                next_step = []
                for next in stepvalue.next_step:
                    if key != next:
                        next_step.append(next)
                stepvalue.next_step = next_step
            return True
        return False
    
    def UpdateStep_Type(self, type_str):
        """단계 타입 변경 - 타입이 변경되면 새 객체를 생성해야 함"""
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        
        current_step = self.Get_Step()
        if current_step.type == type_str:
            return  # 타입이 같으면 아무것도 하지 않음
            
        # 현재 단계의 공통 속성 추출
        base_params = {
            "seq": current_step.seq,
            "waiting": current_step.waiting,
            "type": type_str,
            "next_step": current_step.next_step,
            "fail_step": current_step.fail_step,
            "comment": current_step.comment,
        }
        
        # 새 타입의 객체 생성
        new_step = None
        if type_str == "matching":
            new_step = TaskStep_Matching(
                **base_params,
                zone="",
                image="",
                score="<=85.0",
                finded_click="",
            )
        elif type_str == "mousewheel":
            new_step = TaskStep_MouseWheel(
                **base_params,
                amount=0,
            )
        elif type_str == "telegramNoti":
            new_step = TaskStep_TeltegramNoti(
                **base_params,
                dummy=False,
            )
        else:
            new_step = BaseStep(**base_params)
            
        # 새 단계로 교체
        self.task.steps[self.origin_step_key] = new_step
    
    def UpdateStep_Waiting(self, sec):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().waiting = sec
        
    def UpdateStep_Key(self, key):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.ChangeKey_CurrentStep(key)
        # print(f"step key: {self.origin_step_key} vs {self.current_step_key}")
    
    # --------- TaskStep_Matching 전용 메서드 ---------
    def UpdateStep_Zone(self, zone):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
            
        step = self.Get_Step()
        if isinstance(step, TaskStep_Matching):
            step.zone = zone
            
    def UpdateStep_Image(self, image):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
            
        step = self.Get_Step()
        if isinstance(step, TaskStep_Matching):
            step.image = image
            
    def UpdateStep_ScoreVal(self, score):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
            
        step = self.Get_Step()
        if isinstance(step, TaskStep_Matching):
            val, op_str, desc = step.parse_score()
            scorestr = TaskStep_Matching.desc_to_operator(desc) + str(score)
            step.score = scorestr
            
    def UpdateStep_ScoreDesc(self, scoredesc):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
            
        step = self.Get_Step()
        if isinstance(step, TaskStep_Matching):
            val, op_str, desc = step.parse_score()
            scorestr = TaskStep_Matching.desc_to_operator(scoredesc) + str(val)
            step.score = scorestr
            
    def UpdateStep_ClickType(self, type):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
            
        step = self.Get_Step()
        if isinstance(step, TaskStep_Matching):
            save_click = ""
            if "이미지" == type: save_click = "image"
            elif "영역" == type: save_click = "zone"
            step.finded_click = save_click
    
    # --------- TaskStep_MouseWheel 전용 메서드 ---------
    def UpdateStep_MouseWheel_Amount(self, amount):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
            
        step = self.Get_Step()
        if isinstance(step, TaskStep_MouseWheel):
            step.amount = amount
    
    # --------- TaskStep_TeltegramNoti 전용 메서드 ---------
    def UpdateStep_TelegramNoti_Dummy(self, dummy):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
            
        step = self.Get_Step()
        if isinstance(step, TaskStep_TeltegramNoti):
            step.dummy = dummy
    
    # --------- 공통 메서드 ---------
    def UpdateStep_FailStep(self, step):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().fail_step = step
        
    def UpdateStep_NextSteps(self, widget: QListWidget):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        steps = []
        for i in range(widget.count()):
            step = widget.item(i).text()
            steps.append(step)
        # print(f"{steps}")
        self.Get_Step().next_step = steps
        # print(f"{self.task}")
        
    def UpdateStep_Comment(self, text):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().comment = text