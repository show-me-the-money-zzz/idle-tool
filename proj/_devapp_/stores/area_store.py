import os
import sys
import json
# from pathlib import Path
from grinder_utils import finder, system
from stores.data_setting import DataSetting
from core.window_utils import WindowUtil

class AreaStore:
    _issetup_resolution = False
    
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        
        self.items = {}
        self.store_path = self._resolve_path()
        
        success = self._load()
        if not success:
            system.PrintDEV(f"{self.name} 데이터를 로드할 수 없습니다. 새 데이터 저장소를 생성합니다.")

    def _resolve_path(self):
        # base = Path(__file__).parent.parent / "data"
        base = finder.Get_DataPath()
        os.makedirs(base, exist_ok=True)
        return base / self.filename
    
    def NewKey(self):
        if "범위 영역" == self.name:
            newlist = {}
            for k, v in self.items.items():
                # print(f"[{k}] {v}")
                if k == v["name"]:
                    newkey = system.GetKey("zone")
                    newlist[newkey] = v
                    
                    import time
                    time.sleep(1)
                else:
                    newlist[k] = v
                
            # print(f"{newlist}")
            # self.items = newlist
            self.items = {}
            for k, v in newlist.items():
                # print(f"[{k}] {v}")
                self.add(k, v, False)
            # print(f"{self.items}")
            self.save()

    def _load(self):
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
                    
                if False == getattr(sys, 'frozen', False):  #utils.system.DEVAPP
                    # system.PrintDEV(f"{self.name}.Load(): {' / '.join(self.items)}")
                    system.PrintDEV(f"{self.name}.Load(): {len(self.items)}")
                    
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
            if not AreaStore._issetup_resolution:
                AreaStore.Setup_Resolution()
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
    
    @staticmethod
    def Setup_Resolution():
        # 1회성 처리
        # tesseract_path = AppSetting.get('Tesseract', 'path');
        gene_resolution = DataSetting.Get_Resolution()
        system.PrintDEV(f"AreaStore.Setup_Resolution(): {gene_resolution}")
        if None == gene_resolution:
            left, top, right, bottom = WindowUtil.get_window_rect()
            width = right - left
            height = bottom - top
            # print(f"AreaStore.Setup_Resolution(): window resolution= {width} x {height}")
            update_setting = DataSetting.Set_Resolution(width, height)
            system.PrintDEV(f"AreaStore.Setup_Resolution(): update setting= {update_setting}")
        AreaStore._issetup_resolution = True