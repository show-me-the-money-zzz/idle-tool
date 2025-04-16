from PySide6.QtWidgets import QMenu, QMessageBox, QDialog, QVBoxLayout, QTextEdit
from PySide6.QtGui import QAction
import os

from zzz.config import *

class MenuBar:
    def __init__(self, main_window, settings_manager, ocr_initializer):
        """메뉴바 초기화"""
        self.main_window = main_window
        self.settings_manager = settings_manager
        self.ocr_initializer = ocr_initializer
        
        # 메뉴바 생성 (QMainWindow에서 제공하는 메뉴바 사용)
        self.menubar = main_window.menuBar()
        
        # 메뉴 추가
        self._create_file_menu()
        self._create_settings_menu()
        self._create_help_menu()
        
        self.update_open_path_menu_state()
    
    def _create_file_menu(self):
        """파일 메뉴 생성"""
        file_menu = self.menubar.addMenu("파일(&F)")
        exit_action = QAction("종료(&Q)", self.main_window)
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)
    
    def _create_settings_menu(self):
        """설정 메뉴 생성"""
        self.settings_menu = self.menubar.addMenu("설정(&S)")
        
        # OCR 관련 설정 하위 메뉴
        self.ocr_menu = QMenu("OCR 설정", self.main_window)
        self.settings_menu.addMenu(self.ocr_menu)
        
        set_path_action = QAction("Tesseract OCR 경로 설정", self.main_window)
        set_path_action.triggered.connect(self.set_tesseract_path)
        self.ocr_menu.addAction(set_path_action)
        
        self.open_path_action = QAction("Tesseract OCR 경로 열기", self.main_window)
        self.open_path_action.triggered.connect(self.open_tesseract_folder)
        self.ocr_menu.addAction(self.open_path_action)
        
        # 응용 프로그램 데이터 폴더 관련 메뉴
        self.settings_menu.addSeparator()
        
        open_appdata_action = QAction("앱 데이터 경로 열기", self.main_window)
        open_appdata_action.triggered.connect(self.open_appdata_folder)
        self.settings_menu.addAction(open_appdata_action)
    
    def _create_help_menu(self):
        """도움말 메뉴 생성"""
        help_menu = self.menubar.addMenu("도움말(&H)")
        
        help_action = QAction("사용법", self.main_window)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("정보", self.main_window)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def set_tesseract_path(self):
        """Tesseract OCR 경로 설정"""
        # 현재 설정값 가져오기
        current_path = self.settings_manager.get('Tesseract', 'Path', DEFAULT_TESSERACT_PATH)
        
        # 사용자에게 경로 선택 요청
        new_path = self.settings_manager.prompt_tesseract_path(self.main_window)
        
        if new_path:
            # OCR 재초기화 함수 호출 (메시지 표시 옵션을 True로 설정)
            self.ocr_initializer(new_path, True)
            self.update_open_path_menu_state()
            
    def open_tesseract_folder(self):
        """Tesseract OCR 폴더를 탐색기로 열기"""
        try:
            # 현재 설정된 Tesseract 경로 가져오기
            tesseract_path = self.settings_manager.get('Tesseract', 'Path', '')
            
            if tesseract_path and os.path.exists(tesseract_path):
                # 파일 경로에서 디렉토리 경로 추출
                folder_path = os.path.dirname(tesseract_path)
                
                # 해당 폴더 탐색기로 열기
                os.startfile(folder_path)
            else:
                QMessageBox.information(
                    self.main_window,
                    "알림",
                    "Tesseract OCR 경로가 설정되어 있지 않습니다."
                )
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "오류",
                f"폴더를 여는 중 오류가 발생했습니다: {str(e)}"
            )
            
    def update_open_path_menu_state(self):
        """OCR 경로 탐색기로 열기 메뉴 상태 업데이트"""
        # 현재 설정된 Tesseract 경로 가져오기
        tesseract_path = self.settings_manager.get('Tesseract', 'Path', '')
        
        # 메뉴 활성화/비활성화
        if tesseract_path and os.path.exists(tesseract_path):
            self.open_path_action.setEnabled(True)
        else:
            self.open_path_action.setEnabled(False)
            
    def open_appdata_folder(self):
        """앱 데이터 폴더 열기"""
        try:
            # Settings Manager에서 사용하는 AppData 경로 가져오기
            # 경로는 설정 파일의 디렉토리 경로를 사용
            appdata_path = os.path.dirname(self.settings_manager.settings_path)
            
            if os.path.exists(appdata_path):
                # 해당 폴더 탐색기로 열기
                os.startfile(appdata_path)
            else:
                # 폴더가 없으면 생성 후 열기
                try:
                    os.makedirs(appdata_path)
                    os.startfile(appdata_path)
                except Exception as e:
                    QMessageBox.critical(
                        self.main_window,
                        "오류",
                        f"폴더를 생성하는 중 오류가 발생했습니다: {str(e)}"
                    )
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "오류",
                f"앱 데이터 폴더를 여는 중 오류가 발생했습니다: {str(e)}"
            )
    
    def show_help(self):
        """사용법 표시"""
        help_text = """
사용법:

1. 프로그램 연결:
   - '앱 이름으로 연결' 탭에서 앱 이름 입력 후 검색
   - 목록에서 원하는 앱 선택 후 '선택 연결' 클릭

2. 캡처 영역 설정:
   - '드래그로 영역 선택' 버튼 클릭 후 화면에서 영역 드래그
   - 또는 직접 좌표와 크기 입력

3. 캡처 시작/중지:
   - '캡처 시작' 버튼 클릭하여 OCR 인식 시작
   - 다시 클릭하여 중지

4. 입력 처리:
   - 키보드 입력: 원하는 키를 입력 필드에 입력 후 실행
   - 마우스 클릭: 설정된 좌표에 클릭 전송

5. OCR 설정:
   - '설정' 메뉴에서 Tesseract OCR 경로 설정
        """
        
        # 도움말 대화상자 생성
        help_dialog = QDialog(self.main_window)
        help_dialog.setWindowTitle("사용법")
        help_dialog.resize(500, 400)
        
        layout = QVBoxLayout(help_dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(help_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        help_dialog.exec()
    
    def show_about(self):
        """정보 표시"""
        about_text = f"""
{APP_TITLE}

버전: 1.0.0

화면 영역을 캡처하여 OCR로 텍스트를 인식하는 도구입니다.

※ OCR 기능을 사용하려면 Tesseract OCR이 필요합니다.
설치: https://github.com/UB-Mannheim/tesseract/wiki
        """
        
        QMessageBox.information(
            self.main_window,
            "정보",
            about_text
        )