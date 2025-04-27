import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import operator
import re

from grinder_utils import finder, system

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


# 전역 인스턴스 정의 (areas.py 방식)
Tasks = TaskManager("Task 데이터", "task.json")

@dataclass
class TaskStep:
    seq: int
    waiting: float
    type: str
    zone: str
    image: str
    score: str
    finded_click: str
    next_step: list[str]
    fail_step: str
    comment: str

    def parse_score(self) -> tuple:
        """score 문자열을 (숫자, 연산자, 설명) 형태의 튜플로 반환"""
        match = re.match(r"(<=|>=|<|>|==|!=)?\s*(\d+(?:\.\d+)?)", self.score.strip())
        if not match:
            return (0, "==", "일치")

        op_str, value = match.groups()
        
        # 연산자가 없을 경우 기본값 설정
        if not op_str:
            op_str = "=="
            
        return (float(value), op_str, self.operator_to_desc(op_str))
    
    @staticmethod
    def operator_to_desc(op_str: str) -> str:
        """연산자 문자열을 설명 문자열로 변환"""
        op_map = {
            "<=": "이상",
            ">=": "이하",
            "<": "초과",
            ">": "미만",
            "==": "일치",
            "!=": "다른"
        }
        return op_map.get(op_str, "일치")
    
    @staticmethod
    def desc_to_operator(desc: str) -> str:
        """설명 문자열을 연산자 문자열로 변환"""
        desc_map = {
            "이상": "<=",
            "이하": ">",
            "초과": "<",
            "미만": ">",
            "일치": "==",
            "다른": "!="
        }
        return desc_map.get(desc, "==")
    
    @staticmethod
    def make_score_string(value: float, desc: str) -> str:
        """숫자와 설명을 받아 score 문자열 생성"""
        op_str = TaskStep.desc_to_operator(desc)
        return f"{op_str}{value}"

    def evaluate_score_condition(self, actual: float) -> bool:
        """점수 조건 평가: '<=65'는 '실제 점수가 65 이상이면 참'으로 해석"""
        value, op_str, _ = self.parse_score()
        
        # 점수 조건 해석 (매칭 방향과 반대로 해석)
        if op_str == "<=":
            return actual >= value
        elif op_str == ">=":
            return actual <= value
        elif op_str == ">":
            return actual < value
        elif op_str == "<":
            return actual > value
        elif op_str == "==":
            return actual == value
        elif op_str == "!=":
            return actual != value
        else:
            return actual == value
        
    def Print_Score(self) -> str:
        """점수 조건을 한글로 설명하는 함수"""
        value, _, desc = self.parse_score()
        return f"{value}% {desc}"
    
@dataclass
class Task:
    steps: dict[str, TaskStep]
    start_key: str
    comment: str

    def Get_Step(self, key, default=None):
        return self.steps.get(key, default)

# 인터페이스 함수 정의
Add_Task = Tasks.add
Delete_Task = Tasks.delete
_Get_Task = Tasks.get
def Get_Task(key, default=None):
    data = Tasks.get(key, default)
    # print("seq 1")
    if not data:
        return default

    # print("seq 2")
    # # step dict를 TaskStep 객체로 변환
    # print(data["steps"].items())
    step_dict = {}
    for key, val in data["steps"].items():
        try:
            # print(f"[{key}] {val}")
            step_dict[key] = TaskStep(**val)
        except Exception as e:
            print(f"[Step Load Error] '{key}' 변환 실패: {e}")
    # print(f"{step_dict}")
    # print("seq 3")

    ret = Task(
        steps=step_dict,
        # tasks = {},

        start_key=data["start_key"],
        comment=data.get("comment", "")
    )
    return ret
_GetAll_Tasks = Tasks.all
def GetAll_Tasks() -> dict[str, Task]:
    raw = Tasks.all()
    results: dict[str, Task] = {}

    # for key, data in raw.items():
    for key in raw.keys():
        try:
            results[key] = Get_Task(key)
        except Exception as e:
            print(f"[Task Load Error] '{key}' 변환 실패: {e}")
    return results
Save_Tasks = Tasks.save

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