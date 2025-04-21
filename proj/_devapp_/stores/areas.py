from .area_store import AreaStore
from dataclasses import dataclass, field
from typing import Optional
from stores.base_area_item import BaseAreaItem

Texts = AreaStore("텍스트 영역", "text.json")
Images = AreaStore("이미지 영역", "image.json")
Zones = AreaStore("범위 영역", "zone.json")

@dataclass
class ImageItem(BaseAreaItem):
    _name: str = field(default="", init=False)
    file: str
@dataclass
class ZoneItem(BaseAreaItem):
    _name: str = field(default="", init=False)
@dataclass
class TextItem(BaseAreaItem):
    _name: Optional[str] = None  # 기본값을 설정하면 필수 인자 아님

# 텍스트 영역 함수 인터페이스
Add_TextArea = Texts.add
def Get_TextArea(key, default=None) -> TextItem | None:
    data = Texts.get(key, default)
    if data:
        return TextItem(**data)
    return default
def GetAll_TextArea():
    datalist = {}
    for key, data in Texts.all().items():
        datalist[key] = TextItem(**data)
    return datalist
Delete_TextArea = Texts.delete
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
def GetAll_ImageAreas():
    datalist = {}
    for key, data in Images.all().items():
        datalist[key] = ImageItem(**data)
    return datalist
Delete_ImageArea = Images.delete
Save_ImageAreas = Images.save

# 범위 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ZoneArea = Zones.add
def Get_ZoneArea(key, default=None) -> ZoneItem | None:
    data = Zones.get(key, default)
    if data:
        return ZoneItem(**data)
    return default
def GetAll_ZoneAreas():
    datalist = {}
    for key, data in Zones.all().items():
        datalist[key] = ZoneItem(**data)
    return datalist
Delete_ZoneArea = Zones.delete
Save_ZoneAreas = Zones.save

def initialize():
    Texts.save()
    Images.save()
    Zones.save()
    return True  # 초기화는 생성자에서 이미 처리됨