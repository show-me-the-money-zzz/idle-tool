from dataclasses import dataclass
from typing import Optional
from PySide6.QtWidgets import QListWidget

import copy

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
        self.origin_key = key
        self.current_key = key
        if task:
            self.task = copy.deepcopy(task)
        else: self.task = None
    def Reset_Task(self):
        self.Set_Task("", None)
        self.Reset_Step()
    def ChangeKey_CurrentTask(self, key):
        self.current_key = key
        
    def Get_StartKey(self): return self.task.start_key
    def Get_Commnet(self): return self.task.comment

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
        # print(f"step key: {self.origin_step_key} vs {self.current_step_key}")
        if self.origin_step_key in self.task.steps: # 키 있는지 확인
            # print(f"{self.task.steps}")
            if self.origin_step_key == self.task.start_key: # 시작키이면 변경
                self.task.start_key = self.current_step_key
            newdata = {}
            for key, value in self.task.steps.items():
                if self.origin_step_key == value.fail_step: # 실패 단계
                    value.fail_step = self.current_step_key
                for nextIdx, nextVal in enumerate(value.next_step): # 다음 단계
                    if self.origin_step_key == nextVal:
                        value.next_step[nextIdx] = self.current_step_key
                        break

                # 변경 키로 데이터 맵핑해서 변경
                if self.origin_step_key == key: newdata[self.current_step_key] = value
                else: newdata[key] = value
            self.task.steps = newdata
            # print(f"{self.task.steps}")
            return self.task.steps
        return None
    
    def UpdateTask_Key(self, key):
        if "" == self.origin_key:
            return
        self.current_key = key
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
    
    def UpdateStep_Waiting(self, sec):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().waiting = sec
    def UpdateStep_Key(self, key):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.ChangeKey_CurrentStep(key)
        # print(f"step key: {self.origin_step_key} vs {self.current_step_key}")
    def UpdateStep_Zone(self, zone):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().zone = zone
    def UpdateStep_Image(self, image):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().image = image
    def UpdateStep_ScoreVal(self, score):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        val, op_str, desc = self.Get_Step().parse_score()
        # print(f"{val}, {op_str}, {desc}")
        scorestr = TaskMan.TaskStep.desc_to_operator(desc) + str(score)
        # print(f"{scorestr}")
        self.Get_Step().score = scorestr
        # print(f"{self.task}")
    def UpdateStep_ScoreDesc(self, scoredesc):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        val, op_str, desc = self.Get_Step().parse_score()
        scorestr = TaskMan.TaskStep.desc_to_operator(scoredesc) + str(val)
        # print(f"{scorestr}")
        self.Get_Step().score = scorestr
        # print(f"{self.task}")
    def UpdateStep_ClickType(self, type):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().finded_click = type
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
        
        # from stores.task_manager import Get_Task
        # print(f"{self.task.Get_Step(self.origin_step_key)}")
    def UpdateStep_Comment(self, text):
        if "" == self.origin_key or "" == self.origin_step_key:
            return
        self.Get_Step().comment = text
        