RELEASE_APP = True
# 개발용 앱 구분

# 앱 기본 설정
APP_VERSION="0.2.635"

# APP_TITLE = "쌀먹 - [게임]" # 연결하려는 앱의 타이틀이 포함되면 안됨
APP_TITLE = f"쌀먹툴 - RF온라인넥스트" # 연결하려는 앱의 타이틀이 포함되면 안됨

def AppTitle_nVer(): return f"{APP_TITLE} (ver. {APP_VERSION})"

DEFAULT_APP_NAME = "RF 온라인 넥스트"  # 기본 검색할 앱 이름
DEFAULT_PID = ""    # 기본 PID (비워두기)

# APP_THEME_TkInter = 'classic'
# # clam: 단순 깔끔 / alt: 대체 스타일 / default: 기본 / classic: 클래식(기본 tk 스타일과 유사)
# # vista: Windows Vista/7 / winnative: 원래의 Windows 네이티브 / xpnative: Windows XP 네이티브
# # aqua: macOS의 기본
APP_THEME = 'Macintosh'
# 배포는 'Macintosh' / 개발은 "Windows (Dark Theme)"
# "Fusion", "Windows", "WindowsVista", "Macintosh", "macos"
# 스타일 설정 (PySide6에서는 QApplication 스타일 시트 또는 Fusion 스타일 사용)

def Is_DarkTheme(): return APP_THEME == 'Windows'