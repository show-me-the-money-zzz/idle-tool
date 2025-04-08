import os
import json
from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).parent.parent  # 프로젝트 루트 디렉토리
STORE_DIR = BASE_DIR / "data"  # 데이터 저장 디렉토리
STORE_FILE = STORE_DIR / "textareas.json"

# 데이터 저장소
TextAreas = {}

def AddItem_TextArea(key, data):
    """텍스트 영역 항목 추가/업데이트"""
    TextAreas[key] = data
    print(f"store.AddItem_TextArea({key}, {data})")

def GetItem_TextArea(key, default=None):
    """텍스트 영역 항목 조회"""
    return TextAreas.get(key, default)

def GetAllItems_TextArea():
    """모든 텍스트 영역 항목 조회"""
    return TextAreas.copy()

def DeleteItem_TextArea(key):
    """텍스트 영역 항목 삭제"""
    if key in TextAreas:
        del TextAreas[key]
        return True
    return False

def Save_TextAreas():
    """텍스트 영역 데이터 저장"""
    # 디렉토리가 없으면 생성
    os.makedirs(STORE_DIR, exist_ok=True)
    
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(TextAreas, f, indent=2, ensure_ascii=False)
    return True

def Load_TextAreas():
    """텍스트 영역 데이터 로드"""
    global TextAreas
    
    # 파일이 존재하면 로드
    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                TextAreas = json.load(f)
            return True
        except Exception as e:
            print(f"텍스트 영역 데이터 로드 오류: {e}")
            TextAreas = {}
    return False

# 초기화 시 자동 로드
def initialize():
    """모듈 초기화 (앱 시작 시 호출)"""
    # 데이터 디렉토리 확인 및 생성
    os.makedirs(STORE_DIR, exist_ok=True)
    
    # 데이터 로드
    success = Load_TextAreas()
    if not success:
        print("텍스트 영역 데이터를 로드할 수 없습니다. 새 데이터 저장소를 생성합니다.")
    
    return success