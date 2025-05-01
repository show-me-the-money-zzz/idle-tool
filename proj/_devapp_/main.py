from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir, Qt
import sys
import os

# 모듈 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from zzz.app_ui import AppUI
from core.settings_manager import AppSetting
from core.config import *

def main():
    """메인 함수"""
    
    # import grinder_utils.system as SystemUtil
    # SystemUtil.Print_LibPath()
    
    Load_Stores()
    
    # DPI 스케일링 활성화 (이 부분 추가)
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Qt 6에서는 아래와 같이 사용 (필요한 경우)
    from PySide6.QtGui import QGuiApplication
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # # 설정 관리자 생성
    # settings_manager = SettingsManager()
    ## 모듈에서 직접 생성. 공용 사용 위함
    
    # QApplication 생성
    app = QApplication(sys.argv)
    
    app.setStyle(APP_THEME)
    
    # 메인 애플리케이션 UI 생성
    main_window = AppUI(AppSetting)
    main_window.show()
    
    # 메인 이벤트 루프 실행
    sys.exit(app.exec())
    
def Load_Stores():
    from stores import areas
    areas.initialize()

    from stores import task_manager
    task_manager.initialize()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        dummy = 0
        
        # print(f"[예외 발생] {e}")
        # import traceback
        # traceback.print_exc()
        # input("\n[ENTER] 키를 누르면 종료합니다.")