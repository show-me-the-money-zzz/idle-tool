from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QDoubleSpinBox, QMessageBox,
                               QSpacerItem, QSizePolicy)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
import time
import os

from core.window_utils import WindowUtil
from core.capture_utils import CaptureManager
from core.ocr_engine import setup_tesseract
from zzz.config import *
from ui.nodes.region_selector import RegionSelector
from core.settings_manager import AppSetting

# 각 UI 컴포넌트 import
from zzz.menu_bar import MenuBar
from zzz.status_bar import StatusBar
from zzz.info_bar import InfoBar
from ui.connection_frame import ConnectionFrame
from ui.input_handler_frame import InputHandlerFrame
from ui.log_frame import LogFrame

# from ui.capture_area_frame import CaptureAreaFrame

import core.sanner as Scanner

class AppUI(QMainWindow):
    RUNNER_BUTTON_START_TEXT = "스캔 ▶️" 
    RUNNER_BUTTON_STOP_TEXT = "스캔 🟥"
    
    status_changed = Signal(str)  # 상태 변경 신호
    
    def __init__(self, settings_manager):
        super().__init__()
        
        # 아이콘 설정
        app_icon = QIcon("zzz/icon.ico")  # 또는 상대 경로
        self.setWindowIcon(app_icon)
    
        # 메인 윈도우 설정
        self.setWindowTitle(APP_TITLE)
        self.resize(APP_WIDTH, APP_HEIGHT)
        
        # 상태 메시지 변수
        self.status_message = STATUS_READY
        
        # 중앙 위젯 및 레이아웃 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 상태바 생성
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
        
        # 정보바 생성 (별도로 생성)
        self.info_bar = InfoBar(self)
        
        # 상태바 signal-slot 연결
        self.status_changed.connect(self.status_bar.set_status)
        
        # OCR 엔진 초기화
        self.initialize_ocr()
        
        # 메뉴바 생성
        self.menu_bar = MenuBar(
            self, 
            self.initialize_ocr_with_path
        )
        
        # 기본 매니저 객체 생성
        winman = WindowUtil  # 초기화를 위한
        self.capture_manager = CaptureManager(self.handle_capture_callback)
        self.region_selector = RegionSelector()
        
        # UI 컴포넌트 생성
        self.setup_ui()
        
        # 마우스 위치 추적을 위한 타이머 설정
        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.track_mouse_position)
        self.mouse_timer.start(100)  # 100ms 간격

    def initialize_ocr(self):
        """OCR 엔진 초기화"""
        # Tesseract 경로 확인 및 설정
        tesseract_path = AppSetting.check_tesseract_path(self)
        
        if tesseract_path and os.path.exists(tesseract_path):
            # OCR 엔진 초기화 (기존 설정은 메시지 표시하지 않음)
            return self.initialize_ocr_with_path(tesseract_path, show_message=False)
        else:
            # 사용자에게 경고 메시지 표시
            QMessageBox.warning(
                self,
                "OCR 초기화 실패",
                "Tesseract OCR 경로 설정이 필요합니다.\n"
                "설정 메뉴에서 경로를 설정해주세요."
            )
            return False
    
    def initialize_ocr_with_path(self, tesseract_path, show_message=True):
        """지정된 경로로 OCR 엔진 초기화"""
        try:
            # tesseract_path가 None이면 사용자에게 물어봐야 합니다
            if tesseract_path is None:
                # 이 부분은 AppSetting 구현한 방식에 따라 달라질 수 있습니다
                tesseract_path = AppSetting.ask_tesseract_path(self)
                if not tesseract_path:
                    return False
            
            setup_tesseract(tesseract_path)
            
            # show_message 매개변수가 True일 때만 메시지 박스 표시
            if show_message:
                QMessageBox.information(
                    self,
                    "설정 완료",
                    f"Tesseract OCR 경로가 설정되었습니다.\n{tesseract_path}"
                )
            
            self.status_changed.emit("Tesseract OCR 경로가 업데이트되었습니다.")
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "OCR 초기화 오류",
                f"Tesseract OCR 초기화 중 오류가 발생했습니다.\n{str(e)}"
            )
            return False
    
    def setup_ui(self):
        """UI 구성요소 초기화"""
        # 1. 프로그램 연결 프레임 (변환된 ConnectionFrame 사용)
        self.connection_frame = ConnectionFrame(self, self.status_changed)
        # ConnectionFrame의 크기 정책 설정 - 높이 최소화
        self.connection_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # 필요한 최소 높이만 사용하도록 설정
        self.connection_frame.setMaximumHeight(self.connection_frame.minimumSizeHint().height())
        self.main_layout.addWidget(self.connection_frame)
        
        # 2. 캡처 영역 및 버튼 프레임
        control_frame = self.create_control_frame()
        # 컨트롤 프레임도 필요한 최소 높이만 사용
        control_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.main_layout.addWidget(control_frame)
        
        # 3. 입력 처리 프레임
        self.input_handler_frame = InputHandlerFrame(self, self.status_changed)
        # 입력 처리 프레임도 필요한 최소 높이만 사용
        self.input_handler_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.main_layout.addWidget(self.input_handler_frame)
        
        # 4. 로그 프레임 - 확장 가능하도록 설정
        self.log_frame = LogFrame(self, self.status_changed)
        # 로그 프레임이 수직으로 최대한 확장되도록 설정
        self.log_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 로그 프레임에 stretch factor 추가
        self.main_layout.addWidget(self.log_frame, 1)  # stretch factor 1 추가

        # 5. 정보바를 하단에 추가 (상태바 위쪽)
        self.info_bar = InfoBar(self)
        self.info_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.main_layout.addWidget(self.info_bar)
        
        # 캡처 설정 저장 변수
        self.capture_settings = None
    
    def create_control_frame(self):
        """캡처 제어 프레임 생성"""
        frame = QFrame()
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(0, 5, 0, 5)
        
        # 캡처 시작/중지 버튼
        self.capture_btn = QPushButton(AppUI.RUNNER_BUTTON_START_TEXT)
        self.capture_btn.clicked.connect(self.toggle_capture)
        frame_layout.addWidget(self.capture_btn)
        
        # 간격 프레임
        interval_frame = QFrame()
        interval_layout = QHBoxLayout(interval_frame)
        interval_layout.setContentsMargins(10, 0, 10, 0)
        
        interval_label = QLabel("간격(초)")
        interval_layout.addWidget(interval_label)
        
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.0, 3.0)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setValue(Scanner.Loop_Interval)
        self.interval_spin.setDecimals(1)
        self.interval_spin.setFixedWidth(60)
        interval_layout.addWidget(self.interval_spin)
        
        apply_btn = QPushButton("적용")
        apply_btn.clicked.connect(self.apply_interval)
        interval_layout.addWidget(apply_btn)
        
        frame_layout.addWidget(interval_frame)
        
        # 여백 추가
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        frame_layout.addItem(spacer)
        
        # 아이템 생성 버튼
        self.create_item_btn = QPushButton("아이템 생성")
        self.create_item_btn.clicked.connect(self.open_capture_area_popup)
        frame_layout.addWidget(self.create_item_btn)
        
        return frame
    
    @Slot()
    def track_mouse_position(self):
        """마우스 위치 추적"""
        # InputHandlerFrame의 마우스 위치 업데이트 메서드 호출
        if hasattr(self, 'input_handler_frame'):
            self.input_handler_frame.update_mouse_position()
        
    def handle_capture_callback(self, type_str, message):
        """캡처 콜백 처리"""
        if type_str == "result":
            # 로그 프레임에 추가
            self.log_frame.add_log(message)
        elif type_str == "error":
            # 에러 메시지 표시
            self.status_changed.emit(message)
            # 심각한 오류면 UI 업데이트
            if ERROR_WINDOW_CLOSED in message:
                self.capture_btn.setText(AppUI.RUNNER_BUTTON_START_TEXT)
    
    def open_capture_area_popup(self):
        """캡처 영역 설정 팝업 열기"""
        if not WindowUtil.is_window_valid():
            QMessageBox.critical(self, "오류", "먼저 창에 연결해주세요.")
            return
            
        try:
            # CaptureAreaPopup 인스턴스 생성 (PySide6 버전으로 변환 필요)
            from ui.nodes.capture_area_popup import CaptureAreaPopup
            
            # 현재 설정된 캡처 설정 정보
            current_settings = self.capture_settings
            
            # 팝업 창 생성
            popup = CaptureAreaPopup(
                self, 
                self.region_selector, 
                self.capture_manager, 
                self.status_changed,  # tkinter의 StringVar 대신 Signal 전달
                self.on_capture_popup_close
            )
            
            # 현재 설정된 값이 있으면 팝업에 설정
            if current_settings:
                x, y, width, height, interval = current_settings
                popup.set_capture_info(x, y, width, height, interval)
                
            # 모달 다이얼로그로 표시 (exec() 사용)
            popup.exec()  # show() 대신 exec() 사용
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"캡처 영역 설정 창을 열 수 없습니다: {str(e)}")
            import traceback
            traceback.print_exc()  # 콘솔에 상세 오류 출력
            
    def on_capture_popup_close(self, settings):
        """캡처 영역 설정 팝업이 닫힐 때의 콜백"""
        if settings:
            # 캡처 설정 저장
            self.capture_settings = settings
            
            # 상태바에 설정 정보 표시
            x, y, width, height, interval = settings
            status_msg = f"캡처 영역 설정: X={x}, Y={y}, 너비={width}, 높이={height}, 간격={interval}초"
            self.status_changed.emit(status_msg)
    
    @Slot()
    def toggle_capture(self):
        """캡처 시작/중지 전환"""
        if self.capture_manager.is_capturing:
            # 캡처 중지
            self.capture_manager.stop_capture()
            self.capture_btn.setText(AppUI.RUNNER_BUTTON_START_TEXT)
            self.status_changed.emit(STATUS_STOPPED)
        else:
            try:
                # Tesseract OCR이 설정되어 있는지 확인
                tesseract_path = AppSetting.get('Tesseract', 'Path', '')
                if not tesseract_path or not os.path.exists(tesseract_path):
                    # OCR 설정 요청
                    if not self.initialize_ocr():
                        self.status_changed.emit(ERROR_OCR_CONFIG)
                        return
                
                # 타겟 윈도우 확인
                if not WindowUtil.is_window_valid():
                    QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                    return
                
                # 캡처 시작
                self.capture_manager.start_capture()
                self.capture_btn.setText(AppUI.RUNNER_BUTTON_STOP_TEXT)
                self.status_changed.emit(STATUS_CAPTURING)
                
            except ValueError as e:
                QMessageBox.critical(self, "입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "캡처 오류", f"캡처 시작 중 오류가 발생했습니다: {str(e)}")
    
    @Slot()
    def apply_interval(self):
        try:
            new_value = self.interval_spin.value()
            Scanner.Loop_Interval = new_value
            self.status_changed.emit(f"Loop 간격이 {new_value:.2f}초로 적용되었습니다.")
        except ValueError:
            QMessageBox.critical(self, "입력 오류", "간격은 숫자 형식으로 입력해주세요.")