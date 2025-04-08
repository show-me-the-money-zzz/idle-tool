import os
import json
from utils import finder
from zzz.config import PATH_Data

# 기본 경로 설정
# BASE_DIR = Path(__file__).parent.parent  # 프로젝트 루트 디렉토리
BASE_DIR = finder.Get_LocalPth()
STORE_DIR = BASE_DIR / PATH_Data  # 데이터 저장 디렉토리
STORE_FILE = STORE_DIR / "textareas.json"

# 데이터 저장소
TextAreas = {}

def AddItem(key, data, issave: True):
    """텍스트 영역 항목 추가/업데이트"""
    TextAreas[key] = data
    
    if issave: Save()
    
    print(f"store.AddItem_TextArea({key}, {data})")

def GetItem(key, default=None):
    """텍스트 영역 항목 조회"""
    return TextAreas.get(key, default)

def GetAllItems():
    """모든 텍스트 영역 항목 조회"""
    return TextAreas.copy()

def DeleteItem(key):
    """텍스트 영역 항목 삭제"""
    if key in TextAreas:
        del TextAreas[key]
        return True
    return False

def Save():
    """텍스트 영역 데이터 저장"""
    # 디렉토리가 없으면 생성
    os.makedirs(STORE_DIR, exist_ok=True)
    
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(TextAreas, f, indent=2, ensure_ascii=False)
    return True

def Load():
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
    
    # print(f"저장 경로: {STORE_DIR}")
    # print(f"파일 경로: {STORE_FILE}")
    
    # 데이터 디렉토리 확인 및 생성
    os.makedirs(STORE_DIR, exist_ok=True)
    
    # 데이터 로드
    success = Load()
    if not success:
        print("텍스트 영역 데이터를 로드할 수 없습니다. 새 데이터 저장소를 생성합니다.")
    
    return success