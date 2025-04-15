from .area_store import AreaStore

Texts = AreaStore("텍스트 영역", "text.json")
Images = AreaStore("이미지 영역", "image.json")
Zones = AreaStore("범위 영역", "zone.json")

# 텍스트 영역 함수 인터페이스
Add_TextArea = Texts.add
Get_TextArea = Texts.get
GetAll_TextArea = Texts.all
Delete_TextArea = Texts.delete
Save_TextArea = Texts.save
Load_TextArea = lambda: True  # 이미 클래스에서 자동 로딩됨

# 이미지 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ImageArea = Images.add
Get_ImageArea = Images.get
GetAll_ImageAreas = Images.all
Delete_ImageArea = Images.delete
Save_ImageAreas = Images.save

# 범위 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ZoneArea = Zones.add
Get_ZoneArea = Zones.get
GetAll_ZoneAreas = Zones.all
Delete_ZoneArea = Zones.delete
Save_ZoneAreas = Zones.save


def initialize():
    Texts.save()
    Images.save()
    Zones.save()
    return True  # 초기화는 생성자에서 이미 처리됨