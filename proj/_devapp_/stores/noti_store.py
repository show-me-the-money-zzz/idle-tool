import os
import sys
import json
# from pathlib import Path
from grinder_utils import finder, system
from grinder_types.noti_item import BaseNotiItem, DiscordNoti, TelegramNoti

class NotiStore:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        
        self.items = {}
        self.store_path = self._resolve_path()
        
        success = self._load()
        if not success:
            system.PrintDEV(f"[{self.name}] 데이터를 로드할 수 없습니다. 새 데이터 저장소를 생성합니다.")

    def _resolve_path(self):
        # base = Path(__file__).parent.parent / "data"
        base = finder.Get_DataPath()
        os.makedirs(base, exist_ok=True)
        return base / self.filename
    
    def _load(self):
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
                    
                if False == getattr(sys, 'frozen', False):  #utils.system.DEVAPP
                    # system.PrintDEV(f"{self.name}.Load(): {' / '.join(self.items)}")
                    system.PrintDEV(f"[{self.name}].Load(): {len(self.items)}")
                    
                return True
            except Exception as e:
                system.PrintDEV(f"[{self.name}] 데이터 로드 오류: {e}")
                self.items = {}
                
                return False

    def save(self):
        try:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            system.PrintDEV(f"[{self.name}] 저장 실패: {e}")

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
    
NOTIs = NotiStore("알림 데이터", "noti.json")
Add_Noti = NOTIs.add
Save_Notis = NOTIs.save
GetAll_Notis = NOTIs.all
def Get_Noti(key, default=None):
   data = NOTIs.get(key, default)
   if not data: return default

   if "type" in data:
      if "discord" == data["type"]:
         return DiscordNoti(**data)
      elif "telegram" == data["type"]:
         return TelegramNoti(**data)
   
   return default

def initialize():
    NOTIs.save()