import tkinter as tk
from tkinter import messagebox
import os

from zzz.config import *

class MenuBar:
    def __init__(self, root, settings_manager, ocr_initializer):
        """메뉴바 초기화"""
        self.root = root
        self.settings_manager = settings_manager
        self.ocr_initializer = ocr_initializer
        
        # 메뉴바 생성
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
        
        # 메뉴 추가
        self._create_file_menu()
        self._create_settings_menu()
        self._create_help_menu()
        
        self.update_open_path_menu_state()
    
    def _create_file_menu(self):
        """파일 메뉴 생성"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="종료", command=self.root.quit)
    
    def _create_settings_menu(self):
        """설정 메뉴 생성"""
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="설정", menu=settings_menu)
        
        # OCR 관련 설정 하위 메뉴
        ocr_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="OCR 설정", menu=ocr_menu)
        ocr_menu.add_command(label="Tesseract OCR 경로 설정", command=self.set_tesseract_path)
        ocr_menu.add_command(label="Tesseract OCR 경로 열기", command=self.open_tesseract_folder)
        
        # 응용 프로그램 데이터 폴더 관련 메뉴
        settings_menu.add_separator()
        settings_menu.add_command(label="앱 데이터 경로 열기", command=self.open_appdata_folder)
    
    def _create_help_menu(self):
        """도움말 메뉴 생성"""
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self.show_help)
        help_menu.add_command(label="정보", command=self.show_about)
    
    def set_tesseract_path(self):
        """Tesseract OCR 경로 설정"""
        # 현재 설정값 가져오기
        current_path = self.settings_manager.get('Tesseract', 'Path', DEFAULT_TESSERACT_PATH)
        
        # 사용자에게 경로 선택 요청
        new_path = self.settings_manager.prompt_tesseract_path(self.root)
        
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
                messagebox.showinfo("알림", "Tesseract OCR 경로가 설정되어 있지 않습니다.", parent=self.root)
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 여는 중 오류가 발생했습니다: {str(e)}", parent=self.root)
            
    def update_open_path_menu_state(self):
        """OCR 경로 탐색기로 열기 메뉴 상태 업데이트"""
        # 현재 설정된 Tesseract 경로 가져오기
        tesseract_path = self.settings_manager.get('Tesseract', 'Path', '')
        
        # 메뉴바에서 설정 메뉴 가져오기
        index = self.menubar.index("설정")
        settings_menu = self.menubar.nametowidget(self.menubar.entrycget(index, "menu"))
        
        # OCR 설정 서브메뉴 가져오기
        ocr_menu_index = settings_menu.index("OCR 설정")
        ocr_menu = settings_menu.nametowidget(settings_menu.entrycget(ocr_menu_index, "menu"))
        
        # 메뉴 활성화/비활성화
        if tesseract_path and os.path.exists(tesseract_path):
            ocr_menu.entryconfig("Tesseract OCR 경로 열기", state="normal")
        else:
            ocr_menu.entryconfig("Tesseract OCR 경로 열기", state="disabled")
            
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
                    messagebox.showerror("오류", f"폴더를 생성하는 중 오류가 발생했습니다: {str(e)}", parent=self.root)
        except Exception as e:
            messagebox.showerror("오류", f"앱 데이터 폴더를 여는 중 오류가 발생했습니다: {str(e)}", parent=self.root)
    
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
        
        help_window = tk.Toplevel(self.root)
        help_window.title("사용법")
        help_window.geometry("500x400")
        
        text = tk.Text(help_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)  # 읽기 전용
    
    def show_about(self):
        """정보 표시"""
        about_text = f"""
{APP_TITLE}

버전: 1.0.0

화면 영역을 캡처하여 OCR로 텍스트를 인식하는 도구입니다.

※ OCR 기능을 사용하려면 Tesseract OCR이 필요합니다.
설치: https://github.com/UB-Mannheim/tesseract/wiki
        """
        
        messagebox.showinfo("정보", about_text, parent=self.root)