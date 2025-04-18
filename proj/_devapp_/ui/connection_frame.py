from PySide6.QtWidgets import (QWidget, QTabWidget, QLabel, QLineEdit, QPushButton, 
                           QComboBox, QGridLayout, QHBoxLayout, QVBoxLayout, 
                           QMessageBox, QFileDialog, QFrame, QGroupBox)
from PySide6.QtCore import Qt, Signal, Slot
import win32gui
from datetime import datetime
import os
import asyncio

from zzz.config import *
import ui.css as CSS
from core.window_utils import WindowUtil

class ConnectionFrame(QGroupBox):
    """프로그램 연결 프레임"""

    def __init__(self, parent, status_signal):
        super().__init__("프로그램 연결", parent)
        
        self.status_signal = status_signal
        
        self._setup_ui()
        
        asyncio.run(self.AutoConnect())
            
    async def AutoConnect(self):
        if RELEASE_APP:
            self.connect_to_app_name()
            await asyncio.sleep(0.5)
            
            self.connect_to_selected_app()
            await asyncio.sleep(0.35)
            
            self.activateWindow()
            self.raise_()
        await asyncio.sleep(0)

    def _setup_ui(self):
        """UI 구성요소 초기화"""
        main_layout = QVBoxLayout(self)
        
        # 탭 위젯 생성
        tab_control = QTabWidget(self)
        main_layout.addWidget(tab_control)
        
        # 탭 페이지 생성
        name_tab = QWidget()
        tab_control.addTab(name_tab, "앱 이름으로 연결")
        
        # 앱 이름 탭 설정
        name_layout = QGridLayout(name_tab)
        
        name_layout.addWidget(QLabel("앱 이름 (부분 일치):"), 0, 0, Qt.AlignLeft)
        self.app_name_entry = QLineEdit(DEFAULT_APP_NAME)
        self.app_name_entry.setMinimumWidth(200)
        if RELEASE_APP: self.app_name_entry.setEnabled(False)
        name_layout.addWidget(self.app_name_entry, 0, 1, Qt.AlignLeft)
        
        search_btn = QPushButton("검색")
        search_btn.clicked.connect(self.connect_to_app_name)
        if RELEASE_APP: search_btn.setEnabled(False)
        name_layout.addWidget(search_btn, 0, 2)
        
        name_layout.addWidget(QLabel("검색 결과:"), 1, 0, Qt.AlignLeft)
        self.app_list = QComboBox()
        self.app_list.setMinimumWidth(400)
        if RELEASE_APP: self.app_list.setEnabled(False)
        name_layout.addWidget(self.app_list, 1, 1, 1, 2)
        
        # 상단 버튼 그룹 (좌측과 우측 나누기)
        top_action_frame = QWidget()
        top_action_layout = QHBoxLayout(top_action_frame)
        top_action_layout.setContentsMargins(0, 0, 0, 0)
        
        # 좌측 영역 - 게임 맨위로 버튼
        self.activate_window_btn = QPushButton("게임 맨위로")
        self.activate_window_btn.clicked.connect(self.activate_connected_window)
        self.activate_window_btn.setEnabled(False)
        top_action_layout.addWidget(self.activate_window_btn, 0, Qt.AlignLeft)
        
        # 여백 추가
        top_action_layout.addStretch(1)
        
        # 우측 영역 - 게임 연결 버튼
        connect_app_btn = QPushButton("게임 연결")
        connect_app_btn.setStyleSheet(CSS.BUTTON_APPLY)
        connect_app_btn.clicked.connect(self.connect_to_selected_app)
        top_action_layout.addWidget(connect_app_btn, 0, Qt.AlignRight)
        
        name_layout.addWidget(top_action_frame, 2, 0, 1, 3)
        
        # 하단 버튼 그룹 (캡처 버튼들)
        bottom_action_frame = QWidget()
        bottom_action_layout = QHBoxLayout(bottom_action_frame)
        bottom_action_layout.setContentsMargins(0, 0, 0, 0)

        # 왼쪽에 배치할 버튼들
        left_buttons_widget = QWidget()
        left_buttons_layout = QHBoxLayout(left_buttons_widget)
        left_buttons_layout.setContentsMargins(0, 0, 0, 0)

        # 캡처 버튼
        self.capture_window_btn = QPushButton("캡처")
        self.capture_window_btn.clicked.connect(self.capture_full_window)
        self.capture_window_btn.setEnabled(False)
        left_buttons_layout.addWidget(self.capture_window_btn)

        # 자동 캡처 버튼
        self.auto_capture_btn = QPushButton("캡처 (자동 저장)")
        self.auto_capture_btn.clicked.connect(self.auto_capture_full_window)
        self.auto_capture_btn.setEnabled(False)
        left_buttons_layout.addWidget(self.auto_capture_btn)

        # 폴더 열기 버튼 추가
        open_folder_btn = QPushButton("캡처 폴더 열기")
        open_folder_btn.clicked.connect(self.open_capture_folder)
        left_buttons_layout.addWidget(open_folder_btn)

        # 왼쪽 버튼 그룹 추가
        bottom_action_layout.addWidget(left_buttons_widget, 0, Qt.AlignLeft)

        # 여백을 추가하여 오른쪽 버튼들과 분리
        bottom_action_layout.addStretch(1)

        # 해상도 버튼 그룹
        hd_button_widget = QWidget()
        hd_button_layout = QHBoxLayout(hd_button_widget)
        hd_button_layout.setContentsMargins(0, 0, 0, 0)
        hd_button_layout.setSpacing(0)  # 버튼 간 간격 줄이기

        for label in ["nHD", "HD+", "FHD"]:
            btn = QPushButton(label)
            btn.setFixedWidth(48)
            btn.clicked.connect(lambda _, res=label: WindowUtil.Resize_HD(res))
            hd_button_layout.addWidget(btn)

        # 해상도 버튼 그룹을 오른쪽에 추가
        bottom_action_layout.addWidget(hd_button_widget, 0, Qt.AlignRight)

        name_layout.addWidget(bottom_action_frame, 3, 0, 1, 3)
        
        if not RELEASE_APP:
            pid_tab = QWidget()
            tab_control.addTab(pid_tab, "PID로 연결")
            
            # PID 탭 설정
            pid_layout = QGridLayout(pid_tab)
            
            pid_layout.addWidget(QLabel("프로세스 ID (PID):"), 0, 0, Qt.AlignLeft)
            self.pid_entry = QLineEdit(DEFAULT_PID)
            self.pid_entry.setMaximumWidth(100)
            pid_layout.addWidget(self.pid_entry, 0, 1, Qt.AlignLeft)
            
            connect_pid_btn = QPushButton("연결")
            connect_pid_btn.clicked.connect(self.connect_to_pid)
            pid_layout.addWidget(connect_pid_btn, 0, 2)
        
        # 창 정보 표시 레이블
        self.window_info_edit = QLineEdit("연결된 창 없음")
        self.window_info_edit.setReadOnly(True)  # 읽기 전용으로 설정
        self.window_info_edit.setCursor(Qt.IBeamCursor)  # 텍스트 선택 커서로 변경
        self.window_info_edit.setStyleSheet("background-color: #5d5d5d; color:#ffffff")  # 비활성화 느낌의 배경색
        main_layout.addWidget(self.window_info_edit)
        
        # 여백 조정
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

    @Slot()
    def connect_to_pid(self):
        try:
            pid = int(self.pid_entry.text())
            if not pid:
                raise ValueError("PID가 입력되지 않았습니다.")

            window_info = WindowUtil.find_window_by_pid(pid)
            if not window_info:
                QMessageBox.critical(self, "오류", f"PID {pid}에 해당하는 창을 찾을 수 없습니다.")
                return

            hwnd, title = window_info
            WindowUtil.set_target_window(hwnd)
            WindowUtil.activate_window()

            # self.window_info_label.setText(f"연결됨: '{title}' (HWND: {hwnd})")  # 기존 코드
            self.window_info_edit.setText(f"연결됨: '{title}' (HWND: {hwnd})")
            self.status_signal.emit(f"PID {pid}에 연결되었습니다. 창이 활성화되었습니다.")

            self.capture_window_btn.setEnabled(True)
            self.auto_capture_btn.setEnabled(True)
            self.activate_window_btn.setEnabled(True)

        except ValueError as e:
            QMessageBox.critical(self, "입력 오류", f"올바른 PID를 입력해주세요: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"{ERROR_CONNECTION}: {str(e)}")

    @Slot()
    def connect_to_app_name(self):
        try:
            app_name = self.app_name_entry.text().strip()
            if not app_name:
                raise ValueError("앱 이름이 입력되지 않았습니다.")

            windows = WindowUtil.find_windows_by_name(app_name)

            if not windows:
                QMessageBox.information(self, "검색 결과", "일치하는 창을 찾을 수 없습니다.")
                return

            self.app_list.clear()
            for hwnd, title, pid, proc_name in windows:
                self.app_list.addItem(f"{title} (PID: {pid}, {proc_name})")
                
            self.found_windows = windows
            self.status_signal.emit(f"{len(windows)}개 창을 찾았습니다. 연결할 창을 선택하세요.")

        except ValueError as e:
            QMessageBox.critical(self, "입력 오류", f"올바른 앱 이름을 입력해주세요: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"{ERROR_FINDING}: {str(e)}")

    @Slot()
    def connect_to_selected_app(self):
        try:
            if not hasattr(self, 'found_windows') or not self.found_windows:
                QMessageBox.critical(self, "오류", "먼저 앱을 검색해주세요.")
                return

            selected_index = self.app_list.currentIndex()
            if selected_index < 0:
                QMessageBox.critical(self, "오류", "연결할 창을 선택해주세요.")
                return

            hwnd, title, pid, proc_name = self.found_windows[selected_index]

            if not win32gui.IsWindow(hwnd):
                QMessageBox.critical(self, "오류", "선택한 창이 존재하지 않습니다.")
                return

            WindowUtil.set_target_window(hwnd)
            WindowUtil.activate_window()

            # self.window_info_label.setText(f"연결됨: '{title}' (PID: {pid}, {proc_name})")
            self.window_info_edit.setText(f"연결됨: '{title}' (PID: {pid}, {proc_name})")
            self.status_signal.emit(f"창 '{title}'에 연결되었습니다. 창이 활성화되었습니다.")

            self.capture_window_btn.setEnabled(True)
            self.auto_capture_btn.setEnabled(True)
            self.activate_window_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "오류", f"{ERROR_CONNECTION}: {str(e)}")

    @Slot()
    def capture_full_window(self):
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return

            from core.capture_utils import CaptureManager
            capture_manager = CaptureManager(None)
            screenshot = capture_manager.capture_full_window()

            if not screenshot:
                QMessageBox.critical(self, "오류", "캡처에 실패했습니다.")
                return

            # selected_index = self.app_list.currentIndex()
            # _, title, _, _ = self.found_windows[selected_index]
            # filetitle = title.lower().replace(" ", "-")
            # timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            # initial_file = f"{filetitle}_{timestamp}.{DEFAULT_IMAGE_FORMAT}"
            initial_file = self.Get_Capture_Filename()

            if not os.path.exists(SAVE_DIRECTORY):
                os.makedirs(SAVE_DIRECTORY)

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "캡처 저장",
                os.path.join(SAVE_DIRECTORY, initial_file),
                f"이미지 파일 (*.{DEFAULT_IMAGE_FORMAT});;모든 파일 (*.*)"
            )

            if file_path:
                screenshot.save(file_path)
                self.status_signal.emit(f"창 캡처가 저장되었습니다: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "캡처 오류", f"창 캡처 중 오류가 발생했습니다: {str(e)}")
            
    @Slot()
    def auto_capture_full_window(self):
        """다이얼로그 없이 자동으로 창 캡처하고 저장"""
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return

            from core.capture_utils import CaptureManager
            capture_manager = CaptureManager(None)
            screenshot = capture_manager.capture_full_window()

            if not screenshot:
                QMessageBox.critical(self, "오류", "캡처에 실패했습니다.")
                return
                
            # timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            # filename = f"{filetitle}_{timestamp}.{DEFAULT_IMAGE_FORMAT}"
            filename = self.Get_Capture_Filename()

            # 저장 디렉토리 확인
            if not os.path.exists(SAVE_DIRECTORY):
                os.makedirs(SAVE_DIRECTORY)

            # 파일 저장 (자동)
            file_path = os.path.join(SAVE_DIRECTORY, filename)
            screenshot.save(file_path)
            self.status_signal.emit(f"창 캡처가 자동 저장되었습니다: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "캡처 오류", f"창 캡처 중 오류가 발생했습니다: {str(e)}")
            
    @Slot()
    def open_capture_folder(self):
        try:
            if not os.path.exists(SAVE_DIRECTORY):
                os.makedirs(SAVE_DIRECTORY)
            os.startfile(SAVE_DIRECTORY)  # Windows 전용
        except Exception as e:
            QMessageBox.critical(self, "폴더 열기 실패", f"폴더를 열 수 없습니다: {str(e)}")
            
    def Get_Capture_Filename(self):
        # 자동 파일명 생성
        gametitle = ""
        try:
            selected_index = self.app_list.currentIndex()
            _, title, _, _ = self.found_windows[selected_index]
            gametitle = title.lower().replace(" ", "-")
        except:
            gametitle = "screenshot"
            
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        return f"{gametitle}_{timestamp}.{DEFAULT_IMAGE_FORMAT}"

    @Slot()
    def activate_connected_window(self):
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return

            if WindowUtil.activate_window():
                self.status_signal.emit("연결된 창이 활성화되었습니다.")
            else:
                QMessageBox.critical(self, "오류", "창 활성화에 실패했습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"창 활성화 중 오류가 발생했습니다: {str(e)}")