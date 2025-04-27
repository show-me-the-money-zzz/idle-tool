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
        self.origin_step_key = key
        self.current_step_key = key
        return self.Get_Step()
    def Reset_Step(self): self.Set_StepKey("")
    def ChangeKey_CurrentStep(self, key):
        self.current_step_key = key
    def Get_Step(self): #origin_step_key로 가져오기
        if "" == self.origin_step_key:
            return None
        return self.task.Get_Step(self.origin_step_key)
    def IsExistStep(self, stepkey):
        return (None != self.task.steps.get(stepkey))
    def UpdateStep_NextSteps(self, widget: QListWidget):
        steps = []
        for i in range(widget.count()):
            step = widget.item(i).text()
            steps.append(step)
        print(f"{steps}")