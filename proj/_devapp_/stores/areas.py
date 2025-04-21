from .area_store import AreaStore
from dataclasses import dataclass

Texts = AreaStore("텍스트 영역", "text.json")
Images = AreaStore("이미지 영역", "image.json")
Zones = AreaStore("범위 영역", "zone.json")

@dataclass
class ImageItem:
    x: int
    y: int
    width: int
    height: int
    file: str
    
    @property
    def CenterX(self): return self.x + self.width // 2
    @property
    def CneterY(self): return self.y + self.height // 2
    
    @property
    def ClickX(self): return int(self.CenterX)
    
    @property
    def ClickY(self): return int(self.CneterY)
@dataclass
class ZoneItem:
    x: int
    y: int
    width: int
    height: int
@dataclass
class TextItem:
    x: int
    y: int
    width: int
    height: int

# 텍스트 영역 함수 인터페이스
Add_TextArea = Texts.add
Get_TextArea = Texts.get
# def Get_TextArea(key, default=None) -> TextItem | None:
#     data = Texts.get(key, default)
#     if data:
#         return TextItem(**data)
#     return default
GetAll_TextArea = Texts.all
Delete_TextArea = Texts.delete
Save_TextArea = Texts.save
Load_TextArea = lambda: True  # 이미 클래스에서 자동 로딩됨

# 이미지 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ImageArea = Images.add
def Get_ImageArea(key, default=None) -> ImageItem | None:
    data = Images.get(key, default)
    if data:
        return ImageItem(**data)
    return default
GetAll_ImageAreas = Images.all
Delete_ImageArea = Images.delete
Save_ImageAreas = Images.save

# 범위 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ZoneArea = Zones.add
def Get_ZoneArea(key, default=None) -> ZoneItem | None:
    data = Zones.get(key, default)
    if data:
        return ZoneItem(**data)
    return default
GetAll_ZoneAreas = Zones.all
Delete_ZoneArea = Zones.delete
Save_ZoneAreas = Zones.save

def initialize():
    Texts.save()
    Images.save()
    Zones.save()
    return True  # 초기화는 생성자에서 이미 처리됨