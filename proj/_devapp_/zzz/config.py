"""
프로그램 상수값을 관리하는 설정 모듈
"""

# 앱 기본 설정
APP_TITLE = "돈! 도온~~~" # 연결하려는 앱의 타이틀이 포함되면 안됨
# APP_TITLE = "쌀먹 - [게임]" # 연결하려는 앱의 타이틀이 포함되면 안됨
APP_WIDTH = 600
APP_HEIGHT = 1060
APP_THEME = 'vista'
# clam: 단순 깔끔 / alt: 대체 스타일 / default: 기본 / classic: 클래식(기본 tk 스타일과 유사)
# vista: Windows Vista/7 / winnative: 원래의 Windows 네이티브 / xpnative: Windows XP 네이티브
# aqua: macOS의 기본

# 기본 입력값
DEFAULT_APP_NAME = "LORDNINE"  # 기본 검색할 앱 이름
DEFAULT_PID = ""             # 기본 PID (비워두기)
DEFAULT_CAPTURE_X = "0"      # 기본 캡처 X 좌표
DEFAULT_CAPTURE_Y = "0"      # 기본 캡처 Y 좌표
DEFAULT_CAPTURE_WIDTH = "300"  # 기본 캡처 너비
DEFAULT_CAPTURE_HEIGHT = "100" # 기본 캡처 높이
DEFAULT_CAPTURE_INTERVAL = "1.0" # 기본 캡처 간격(초)
DEFAULT_CLICK_X = "0"        # 기본 클릭 X 좌표
DEFAULT_CLICK_Y = "0"        # 기본 클릭 Y 좌표

DRAG_ZOOM_FACTOR = 4 # 영역 드래그 미리보기 ZOOM 확대 배율

# OCR 설정 - 기본값 (설정 파일이 없을 경우 사용)
DEFAULT_TESSERACT_PATH = r"D:\tool\Tesseract-OCR\tesseract.exe"  # Tesseract OCR 기본 경로
OCR_LANGUAGE = "kor+eng"     # OCR 인식 언어

# 드래그 관련 단축키 설정
DRAG_FIXED_WIDTH_KEY = "F"   # 너비 고정 (W키)
DRAG_FIXED_HEIGHT_KEY = "G"  # 높이 고정 (H키)
DRAG_KEEP_SQUARE_KEY = "E"   # 정사각형 비율 유지 (S키)
DRAG_ASPECT_RATIO_KEY = "R"  # 특정 비율 유지 (R키)
DRAG_ASPECT_RATIO = 16/9     # 비율 유지 시 가로 대 세로 비율 (16:9)
DRAG_ASPECT_RATIO_TEXT = "16:9" # DRAG_ASPECT_RATIO 출력을 위한 문자열값

# 파일 저장 관련
SAVE_DIRECTORY = "captures"  # 캡처 이미지 저장 기본 폴더
DEFAULT_IMAGE_FORMAT = "png" # 기본 이미지 저장 형식
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S" # 타임스탬프 형식

# UI 관련 문자열
STATUS_READY = "준비 완료"
STATUS_CAPTURING = "캡처 중..."
STATUS_STOPPED = "캡처 중지됨"
ERROR_NO_WINDOW = "먼저 창에 연결해주세요."
ERROR_WINDOW_CLOSED = "창이 닫혔습니다."
ERROR_CONNECTION = "연결 중 오류가 발생했습니다"
ERROR_FINDING = "검색 중 오류가 발생했습니다"
ERROR_OCR_CONFIG = "Tesseract OCR 경로 설정이 필요합니다"

# 설정 관련 상수
SETTINGS_FILE = "lordnine_settings.ini"