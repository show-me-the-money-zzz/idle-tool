import json
from pathlib import Path
from typing import Optional, Dict, Union, Type
from dataclasses import dataclass, field
import operator
import re

from grinder_utils import finder, system
from stores.task_base_step import BaseStep, TaskStep_Matching, TaskStep_MouseWheel, TaskStep_TeltegramNoti

# Dictionary mapping type strings to step classes
STEP_TYPE_MAP = {
    "matching": TaskStep_Matching,
    "mousewheel": TaskStep_MouseWheel,
    "telegramNoti": TaskStep_TeltegramNoti,
    
    # "waiting": TaskStep_Waiting,
}

@dataclass
class Task:
    steps: dict[str, BaseStep]  # Now using BaseStep instead of TaskStep
    start_key: str
    comment: str

    def Get_Step(self, key, default=None):
        return self.steps.get(key, default)

class TaskManager:
    def __init__(self, name: str, filename: str):
        self.name = name
        self.filename = filename
        self.tasks = {}
        self.store_path = self._resolve_path()
        # print(self.store_path)

        success = self._load()
        if not success:
            system.PrintDEV(f"{self.name} 데이터를 로드할 수 없습니다. 새 데이터 저장소를 생성합니다.")

    def _resolve_path(self) -> Path:
        base = Path(__file__).parent / "data"
        base = finder.Get_DataPath()
        base.mkdir(parents=True, exist_ok=True)
        return base / self.filename

    def _load(self) -> bool:
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                system.PrintDEV(f"[{self.name}] 로드됨: {len(self.tasks)}개 태스크")
                return True
            except Exception as e:
                system.PrintDEV(f"[{self.name}] 로딩 오류: {e}")
                self.tasks = {}
        return False

    def save(self):
        try:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            # system.PrintDEV(f"[{self.name}] 저장 완료")
        except Exception as e:
            system.PrintDEV(f"[{self.name}] 저장 실패: {e}")

    def add(self, key: str, data: dict, save: bool = True):
        self.tasks[key] = data
        if save:
            self.save()

    def delete(self, key: str, save: bool = True) -> bool:
        if key in self.tasks:
            del self.tasks[key]
            if save:
                self.save()
            return True
        return False

    def get(self, key: str, default=None) -> Optional[dict]:
        return self.tasks.get(key, default)

    def all(self) -> dict:
        return self.tasks.copy()

    def add_task(self, key: str, task: Task, save: bool = True):
        """Task 객체를 직접 받아 저장하는 함수"""
        # Task 객체를 딕셔너리로 변환
        task_dict = {
            "steps": {},
            "start_key": task.start_key,
            "comment": task.comment
        }
        
        # 각 BaseStep을 딕셔너리로 변환
        for step_key, step in task.steps.items():
            step_dict = {
                "seq": step.seq,
                "waiting": step.waiting,
                "type": step.type,
                "next_step": step.next_step,
                "fail_step": step.fail_step,
                "comment": step.comment
            }
            
            # 해당 타입에 따라 추가 필드 저장
            if step.type == "matching" and isinstance(step, TaskStep_Matching):
                step_dict.update({
                    "zone": step.zone,
                    "image": step.image,
                    "score": step.score,
                    "finded_click": step.finded_click,
                })
            elif step.type == "mousewheel" and isinstance(step, TaskStep_MouseWheel):
                step_dict.update({
                    "amount": step.amount,
                })
            elif step.type == "telegramNoti" and isinstance(step, TaskStep_TeltegramNoti):
                step_dict.update({
                    "dummy": step.dummy,
                })
            
            task_dict["steps"][step_key] = step_dict
        
        # 변환된 딕셔너리 저장
        self.add(key, task_dict, save)
        return True

    def update_task(self, old_key: str, task: Task, new_key: str = None, save: bool = True) -> bool:
        """주어진 키의 Task를 업데이트하는 함수
        
        old_key: 기존 키
        task: 새로운 Task 객체
        new_key: 변경할 새 키 (None이면 키 변경 없음)
        save: 저장 여부
        """
        # 키가 존재하지 않으면 추가
        if old_key not in self.tasks:
            # 키가 존재하지 않으면 new_key 사용 (제공된 경우)
            add_key = new_key if new_key else old_key
            return self.add_task(add_key, task, save)
        
        # print(f"<<<<<<<<<<BEFORE>>>>>>>>>\n{self.tasks.items()}")
        tasklist = {}
        for taskkey, taskvar in self.tasks.items():
            # print(f"{[tsakkey]} {taskvar}")
            if old_key == taskkey:  #덮어쓰기
                keyname = old_key
                if new_key and old_key != new_key:  # new_key가 유효하고 old_key와 다르면
                    keyname = new_key
                    
                task_dict = {
                    "steps": {},
                    "start_key": task.start_key,
                    "comment": task.comment
                }
                
                for stepkey, stepvar in task.steps.items(): #단계 복사
                    step_dict = {
                        "seq": stepvar.seq,
                        "waiting": stepvar.waiting,
                        "type": stepvar.type,
                        "next_step": stepvar.next_step,
                        "fail_step": stepvar.fail_step,
                        "comment": stepvar.comment
                    }
                    
                    # 해당 타입에 따라 추가 필드 저장
                    if stepvar.type == "matching" and isinstance(stepvar, TaskStep_Matching):
                        step_dict.update({
                            "zone": stepvar.zone,
                            "image": stepvar.image,
                            "score": stepvar.score,
                            "finded_click": stepvar.finded_click,
                        })
                    elif stepvar.type == "mousewheel" and isinstance(stepvar, TaskStep_MouseWheel):
                        step_dict.update({
                            "amount": stepvar.amount,
                        })
                    elif stepvar.type == "telegramNoti" and isinstance(stepvar, TaskStep_TeltegramNoti):
                        step_dict.update({
                            "dummy": stepvar.dummy,
                        })
                    
                    task_dict["steps"][stepkey] = step_dict
                
                tasklist[keyname] = task_dict
            else:   # 기존 정보는 그대로
                tasklist[taskkey] = taskvar
        
        self.tasks = tasklist
        # print(f"<<<<<<<<<<AFTER>>>>>>>>>\n{self.tasks.items()}")
        
        if save:
            self.save()
        return True

# 전역 인스턴스 정의 (areas.py 방식)
Tasks = TaskManager("Task 데이터", "task.json")

# 인터페이스 함수 정의
Load_Task = Tasks._load
Add_Task = Tasks.add
Delete_Task = Tasks.delete
_Get_Task = Tasks.get

def _create_step_instance(step_type: str, step_data: dict) -> BaseStep:
    """주어진 타입에 맞는 BaseStep 파생 객체 생성"""
    # 기본 공통 필드
    base_params = {
        "seq": step_data.get("seq", 0),
        "waiting": step_data.get("waiting", 0.0),
        "type": step_type,
        "next_step": step_data.get("next_step", []),
        "fail_step": step_data.get("fail_step", ""),
        "comment": step_data.get("comment", ""),
    }
    
    # 타입별 특화 클래스 선택
    if step_type == "matching":
        return TaskStep_Matching(
            **base_params,
            zone=step_data.get("zone", ""),
            image=step_data.get("image", ""),
            score=step_data.get("score", "<=85.0"),
            finded_click=step_data.get("finded_click", ""),
        )
    elif step_type == "mousewheel":
        return TaskStep_MouseWheel(
            **base_params,
            amount=step_data.get("amount", 0),
        )
    elif step_type == "telegramNoti":
        return TaskStep_TeltegramNoti(
            **base_params,
            dummy=step_data.get("dummy", False),
        )
    else:
        # 알 수 없는 타입은 기본 BaseStep 반환
        return BaseStep(**base_params)

def Get_Task(key, default=None):
    data = Tasks.get(key, default)
    if not data:
        return default

    # step dict를 BaseStep 파생 객체로 변환
    step_dict = {}
    for key, val in data["steps"].items():
        try:
            step_type = val.get("type", "matching")  # 기본값은 matching
            step_dict[key] = _create_step_instance(step_type, val)
        except Exception as e:
            print(f"[Step Load Error] '{key}' 변환 실패: {e}")

    ret = Task(
        steps=step_dict,
        start_key=data["start_key"],
        comment=data.get("comment", "")
    )
    return ret

def GetAll_Tasks() -> dict[str, Task]:
    raw = Tasks.all()
    results: dict[str, Task] = {}

    for key in raw.keys():
        try:
            results[key] = Get_Task(key)
        except Exception as e:
            print(f"[Task Load Error] '{key}' 변환 실패: {e}")
    return results

Save_Tasks = Tasks.save
Add_Task = Tasks.add_task
Update_Task = Tasks.update_task

def Update_Task(old_key: str, task: Task, new_key: str = None, save: bool = True):
    if Tasks.update_task(old_key, task, new_key, save):
        return GetAll_Tasks()
    return None

def Create_Empty_Step(step_type: str, seq: int = 0) -> BaseStep:
    """새로운 빈 단계를 생성하는 함수"""
    # 공통 파라미터
    base_params = {
        "seq": seq,
        "waiting": 0.0,
        "type": step_type,
        "next_step": [],
        "fail_step": "",
        "comment": "",
    }
    
    # 타입별 객체 생성
    if step_type == "matching":
        return TaskStep_Matching(
            **base_params,
            zone="",
            image="",
            score="<=85.0",
            finded_click="",
        )
    elif step_type == "mousewheel":
        return TaskStep_MouseWheel(
            **base_params,
            amount=0,
        )
    elif step_type == "telegramNoti":
        return TaskStep_TeltegramNoti(
            **base_params,
            dummy=False,
        )
    else:
        return BaseStep(**base_params)

class RunningTask:
    key = ""
    def __init__(self, key: str): self.key = key
    def set_key(self, key):
        findTask = Get_Task(key, None)
        if findTask:
            self.key = key
            return True        
        else:
            self.reset_key()
            return False
    def reset_key(self): self.key = ""
    def get(self):
        return (self.key, Get_Task(self.key, None))

_runnging_task = RunningTask("")
SetKey_RunningTask = _runnging_task.set_key
ResetKey_RunningTask = _runnging_task.reset_key
Get_RunningTask = _runnging_task.get

def initialize():
    Tasks.save()

    # Print_Data()
    # Print_Data2()
    # Print_Score()

def Print_Score():
    val = [ 30, 45, 60, 65, 70 ]
    hunting = Get_Task("사냥1")
    step_kesy = [ "잡화상점이동", "몹까지이동", "월드맵아이콘클릭" ]

    for stepkey in step_kesy:
        eval = hunting.Get_Step(stepkey)
        if None != eval:
            print(f"{stepkey}: {eval.score}")
            for v in val:
                result = eval.evaluate_score_condition(v)
                print(f"{v}: {result}")

def Print_Data2():
    hunting = Get_Task("사냥1")
    print(f"{hunting}")
    click_worldmap = hunting.Get_Step("월드맵아이콘클릭")
    print(f"{click_worldmap}")

    err = hunting.Get_Step("err")
    print(f"{err}")

def Print_Data():
    # system.PrintDEV(f"{_GetAll_Tasks()}")
    hunting1 = _Get_Task("사냥1")
    # system.PrintDEV(f"{hunting1}")
    hunting1_steps= hunting1["steps"]
    # system.PrintDEV(f"{hunting1_steps}")
    for key, data in hunting1_steps.items():
        system.PrintDEV(f"[{key}]: {data}")
    # move_zaphwa = hunting1_steps["잡화상점이동"]
    # system.PrintDEV(f"{move_zaphwa}")
    # click_worldmap = hunting1_steps["월드맵아이콘클릭"]
    # system.PrintDEV(f"{click_worldmap}")

    hunting1_startkey= hunting1["start_key"]
    hunting1_comment= hunting1["comment"]
    system.PrintDEV(f"start_key: {hunting1_startkey}")
    system.PrintDEV(f"comment: {hunting1_comment}")