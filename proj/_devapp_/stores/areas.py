from .area_store import AreaStore
from dataclasses import dataclass, field
from typing import Optional
from stores.base_area_item import BaseAreaItem

Texts = AreaStore("텍스트 영역", "text.json")
Images = AreaStore("이미지 영역", "image.json")
Zones = AreaStore("범위 영역", "zone.json")

@dataclass
class ImageItem(BaseAreaItem):
    # _name: str = field(default="", init=False)
    file: str

    def GetClickPoint_byApp(self, x, y):
        return (x + self.clickx, y + self.clicky)
@dataclass
class ZoneItem(BaseAreaItem):
    # _name: str = field(default="", init=False)
    pass
@dataclass
class TextItem(BaseAreaItem):
    # _name: Optional[str] = None  # 기본값을 설정하면 필수 인자 아님
    pass

# 텍스트 영역 함수 인터페이스
Add_TextArea = Texts.add
def Get_TextArea(key, default=None) -> TextItem | None:
    data = Texts.get(key, default)
    if data:
        return TextItem(**data)
    return default
def Get_TextArea_byName(name, default=None) -> tuple[str, TextItem] | None:
    for key, data in GetAll_TextAreas().items():
        if data.name == name:
            return (key, data)
    return default
def GetAll_TextAreas():
    datalist = {}
    for key, data in Texts.all().items():
        datalist[key] = TextItem(**data)
    return datalist
Delete_TextArea = Texts.delete
def Delete_TextArea_byName(name):
    key, _ = Get_TextArea_byName(name)
    Texts.delete(key)
Save_TextArea = Texts.save
Load_TextArea = lambda: True  # 이미 클래스에서 자동 로딩됨

"""
예시
tlist = GetAll_TextArea()
item1 = tlist["key1"]

textareas = GetAll_TextArea().items()
    for key, item in textareas:
        print(f"[{key}] {item.x}, {item.y} | {item.width} x {item.height}")
hp = GetAll_TextArea()["[스탯]피통"]
print(f"{hp.x}, {hp.y} | {hp.width} x {hp.height}")
"""

# 이미지 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ImageArea = Images.add
def Get_ImageArea(key, default=None) -> ImageItem | None:
    data = Images.get(key, default)
    if data:
        return ImageItem(**data)
    return default
def Get_ImageArea_byName(name, default=None) -> tuple[str, ImageItem] | None:
    for key, data in GetAll_ImageAreas().items():
        if data.name == name:
            return (key, data)
    return default
def GetAll_ImageAreas():
    datalist = {}
    for key, data in Images.all().items():
        datalist[key] = ImageItem(**data)
    return datalist
Delete_ImageArea = Images.delete
def Delete_ImageArea_byName(name):
    key, _ = Get_ImageArea_byName(name)
    Images.delete(key)
Save_ImageAreas = Images.save

# 범위 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ZoneArea = Zones.add
def Get_ZoneArea(key, default=None) -> ZoneItem | None:
    data = Zones.get(key, default)
    if data:
        return ZoneItem(**data)
    return default
def Get_ZoneArea_byName(name, default=None) -> tuple[str, ZoneItem] | None:
    for key, data in GetAll_ZoneAreas().items():
        if data.name == name:
            return (key, data)
    return default
def GetAll_ZoneAreas():
    datalist = {}
    for key, data in Zones.all().items():
        datalist[key] = ZoneItem(**data)
    return datalist
Delete_ZoneArea = Zones.delete
def Delete_ZoneArea_byName(name):
    key, _ = Get_ZoneArea_byName(name)
    Zones.delete(key)
Save_ZoneAreas = Zones.save

def Load_All():
    Zones._load()
    Images._load()
    Texts._load()

def initialize():
    Texts.save()
    Images.save()
    Zones.save()
    return True  # 초기화는 생성자에서 이미 처리됨