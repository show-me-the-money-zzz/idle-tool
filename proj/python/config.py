"""
프로그램 상수값을 관리하는 설정 모듈
"""

# 앱 기본 설정
APP_TITLE = "쇼 미더 머니 - 로드나인" # 연결하려는 앱의 타이틀이 포함되면 안됨
APP_WIDTH = 600
APP_HEIGHT = 650

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

# OCR 설정
TESSERACT_PATH = r"..\..\Tesseract-OCR\tesseract.exe"  # Tesseract OCR 경로
OCR_LANGUAGE = "kor+eng"     # OCR 인식 언어

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