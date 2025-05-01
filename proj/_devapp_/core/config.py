"""
프로그램 상수값을 관리하는 설정 모듈
"""

"""
▶■
▶️⏹️🟥
"""

APP_WIDTH = 600
APP_HEIGHT = 1060

# 기본 입력값
DEFAULT_APP_NAME = "RF 온라인 넥스트"  # 기본 검색할 앱 이름
DEFAULT_PID = ""             # 기본 PID (비워두기)
DEFAULT_CAPTURE_X = "0"      # 기본 캡처 X 좌표
DEFAULT_CAPTURE_Y = "0"      # 기본 캡처 Y 좌표
DEFAULT_CAPTURE_WIDTH = "64"  # 기본 캡처 너비
DEFAULT_CAPTURE_HEIGHT = "24" # 기본 캡처 높이
# DEFAULT_CAPTURE_INTERVAL = "1.0" # 기본 캡처 간격(초)
DEFAULT_CLICK_X = "0"        # 기본 클릭 X 좌표
DEFAULT_CLICK_Y = "0"        # 기본 클릭 Y 좌표

DEFAULT_LOOP_INTERVAL = 1.0 # 기본 캡처 간격(초)
LOOP_TEXT_KEYWORD = [
    "[스탯]피통", "[스탯]마나통", "[스탯]물약",
    "[지역]종류", "[지역]이름",
] # stores.def_info 에서 Update_Value 변경해줘야
LOOP_IMAGE_KEYWORD = [
    # "[스탯]물약-엥꼬",
]

DRAG_ZOOM_FACTOR = 4 # 영역 드래그 미리보기 ZOOM 확대 배율

# OCR 설정 - 기본값 (설정 파일이 없을 경우 사용)
DEFAULT_TESSERACT_EXEFILENAME="tesseract.exe"
DEFAULT_TESSERACT_PATH = rf"D:\tool\Tesseract-OCR\{DEFAULT_TESSERACT_EXEFILENAME}"  # Tesseract OCR 기본 경로
OCR_LANGUAGE = "kor+eng"     # OCR 인식 언어

# 드래그 관련 단축키 설정
DRAG_FIXED_WIDTH_KEY = "shift"   # 너비 고정
DRAG_FIXED_HEIGHT_KEY = "ctrl"  # 높이 고정
DRAG_KEEP_SQUARE_KEY = "alt"   # 정사각형 비율 유지
DRAG_ASPECT_RATIO_KEY = "ctrl+alt"  # 특정 비율 유지 (R키)
DRAG_ASPECT_RATIO = 16/9     # 비율 유지 시 가로 대 세로 비율 (16:9)
DRAG_ASPECT_RATIO_TEXT = "16:9" # DRAG_ASPECT_RATIO 출력을 위한 문자열값

# 파일 저장 관련
SAVE_DIRECTORY = "captures"  # 캡처 이미지 저장 기본 폴더
DEFAULT_IMAGE_FORMAT = "png" # 기본 이미지 저장 형식
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S" # 타임스탬프 형식
PATH_Data = "data"

# UI 관련 문자열
STATUS_READY = "준비 완료"
STATUS_CAPTURING = "캡처 중..."
STATUS_STOPPED = "캡처 중지됨"
ERROR_NO_WINDOW = "먼저 창에 연결해주세요."
ERROR_WINDOW_CLOSED = "창이 닫혔습니다."
ERROR_CONNECTION = "연결 중 오류가 발생했습니다"
ERROR_FINDING = "검색 중 오류가 발생했습니다"
ERROR_OCR_CONFIG = "Tesseract OCR 경로 설정이 필요합니다"

COLOR_EXTRACT_MODE_SWAP_KEY = "Z"   # 색상 추출 모드 스왑

# 설정 관련 상수
SETTINGS_FILE = "app_settings.ini"