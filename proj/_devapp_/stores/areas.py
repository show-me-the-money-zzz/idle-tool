from .area_store import AreaStore

TextAreaStore = AreaStore("텍스트 영역", "textareas.json")
ImageAreaStore = AreaStore("이미지 영역", "imageareas.json")

# 텍스트 영역 함수 인터페이스
Add_TextArea = TextAreaStore.add
Get_TextArea = TextAreaStore.get
GetAll_TextArea = TextAreaStore.all
Delete_TextArea = TextAreaStore.delete
Save_TextArea = TextAreaStore.save
Load_TextArea = lambda: True  # 이미 클래스에서 자동 로딩됨

# 이미지 영역 함수 인터페이스 (선택적으로 따로 제공 가능)
Add_ImageArea = ImageAreaStore.add
Get_ImageArea = ImageAreaStore.get
GetAll_ImageAreas = ImageAreaStore.all
Delete_ImageArea = ImageAreaStore.delete
Save_ImageAreas = ImageAreaStore.save


def initialize():
    TextAreaStore.save()
    ImageAreaStore.save()
    return True  # 초기화는 생성자에서 이미 처리됨