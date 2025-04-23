import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from grinder_utils import finder, system

class TaskManager:
    def __init__(self, name: str, filename: str):
        self.name = name
        self.filename = filename
        self.tasks = {}
        self.store_path = self._resolve_path()

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
Tasks = TaskManager("Task 데이터", "tasks.json")

# 인터페이스 함수 정의
Add_Task = Tasks.add
Delete_Task = Tasks.delete
Get_Task = Tasks.get
GetAll_Tasks = Tasks.all
Save_Tasks = Tasks.save

def initialize():
    Tasks.save()

    Print_Data()

def Print_Data():
    # system.PrintDEV(f"{_GetAll_Tasks()}")
    hunting1 = Get_Task("사냥1")
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