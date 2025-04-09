import os
import sys
import json
# from pathlib import Path
from utils import finder
from zzz.config import PATH_Data

class AreaStore:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        
        self.items = {}
        self.store_path = self._resolve_path()
        
        success = self._load()
        if not success:
            print(f"{self.name} 데이터를 로드할 수 없습니다. 새 데이터 저장소를 생성합니다.")

    def _resolve_path(self):
        # base = Path(__file__).parent.parent / "data"
        base = finder.Get_LocalPth() / PATH_Data
        os.makedirs(base, exist_ok=True)
        return base / self.filename

    def _load(self):
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
                    
                if False == getattr(sys, 'frozen', False):  #utils.system.DEVAPP
                    print(f"{self.name}.Load(): {" / ".join(self.items)}")
                    
                return True
            except Exception as e:
                print(f"[{self.name}] 데이터 로드 오류: {e}")
                self.items = {}
                
                return False

    def save(self):
        try:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[{self.name}] 저장 실패: {e}")

    def add(self, key, data, save=True):
        self.items[key] = data
        if save:
            self.save()

    def delete(self, key, save=True):
        if key in self.items:
            del self.items[key]
            
            if save: self.save()
            return True
        return False

    def get(self, key, default=None):
        return self.items.get(key, default)

    def all(self):
        return self.items.copy()
