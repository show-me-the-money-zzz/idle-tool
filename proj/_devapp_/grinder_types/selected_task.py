from dataclasses import dataclass
from typing import Optional
from PySide6.QtWidgets import QListWidget

import copy

from stores.task_base_step import BaseStep, TaskStep_Matching, TaskStep_MouseWheel, TaskStep_TeltegramNoti
import stores.task_manager as TaskMan

@dataclass
class SelectedTask:
    origin_key: str #task의 이름 변경 대비 (사냥1이 origin_key / 사냥XX current_key)
    task: Optional[TaskMan.Task]    # deepcopy(task) 컨트롤 변경을 일일이 업데이트
    # task: TaskMan.Task | None
    origin_step_key: str    #step의 이름 변경 대비 (잡화상점찾기 origin_step_key / 잡화상점찾기가기 current_step_key)
    
    # # 변경 전에 저장된 데이터 있는지 확인
    # ## selected_originkey 가 원본에 없는 key이면 추가
    # ## 있는 key면 selected_currentkey / selected_currenttask으로 비교해서 변경사항 추적
    def Set_Task(self, key, task: TaskMan.Task | None):
        # print(f"Set_Task({key})")
        self.origin_key = key
        if task:
            self.task = copy.deepcopy(task)
            # print(f"{task}")
        else: self.task = None
    def Reset_Task(self):
        self.Set_Task("", None)
        self.Reset_Step()
    def GetKey_Task(self): return self.origin_key
        
    def Get_StartKey(self): return self.task.start_key
    def Get_Commnet(self): return self.task.comment

    def IsSelect(self): return "" != self.origin_key

    def Set_StepKey(self, key):
        # print(f"SelectedTask.Set_StepKey({key})")
        self.origin_step_key = key
        return self.Get_Step()
    def Get_StepKey(self): return self.origin_step_key
    def Reset_Step(self): self.Set_StepKey("")
    
    def Get_Step(self): #origin_step_key로 가져오기
        if "" == self.origin_step_key:
            return None
        return self.task.Get_Step(self.origin_step_key)
    def IsSelectStep(self): return "" != self.origin_step_key
    def IsExistStep(self, stepkey):
        return (None != self.task.steps.get(stepkey))
    def IsExistStep_byName(self, name):
        ret = ""
        for stepkey, step in self.task.steps.items():
            if step.name == name:
                ret = stepkey
                break
        return ret
    
    def RemoveTask(self, name):
        # print(f"RemoveTask(name= {name})")
        ret = self.origin_key
        self.Reset_Task()
        return ret
    
    def UpdateTask_Name(self, name):
        if "" == self.origin_key:
            return
        self.task.name = name
        # print(f"task key: {self.origin_key} vs {self.current_key}")
    def UpdateTask_Comment(self, text):
        if "" == self.origin_key:
            return
        self.task.comment = text
        # print(f"{self.task}")
    def UpdateTask_StartStepKey(self, checked):
        # print(f"StartStepKey({checked})")
        if "" == self.origin_key or "" == self.origin_step_key:
            return ("", None)
        # print(f"StartStepKey({checked}): {self.origin_step_key}")
        self.task.start_key = self.origin_step_key
        return (self.task.start_key, self.GetStep_Start())
    def GetStep_Start(self):
        ret = None
        if self.origin_step_key:
            for stepkey, step in self.task.steps.items():
                if self.origin_step_key == stepkey:
                    ret = step
                    break
        return ret
    
    def NewStep(self, key, name, step_type="matching"):
        """새 단계 생성"""
        self.task.steps[key] = TaskMan.Create_Empty_Step(name, step_type)
        # print(name)
        # print(self.task)
    
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
    def RemoveStep_byName(self, name):
        key = self.IsExistStep_byName(name)
        return self.RemoveStep(key)
    
    def UpdateStep_Type(self, type_str):
        """단계 타입 변경 - 타입이 변경되면 새 객체를 생성해야 함"""
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        
        current_step = self.Get_Step()
        if current_step.type == type_str:
            return  # 타입이 같으면 아무것도 하지 않음
            
        # 현재 단계의 공통 속성 추출
        base_params = {
            "name": current_step.name,
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
        
    def UpdateStep_Name(self, name):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().name = name
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