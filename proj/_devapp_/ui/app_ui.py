from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QDoubleSpinBox, QMessageBox,
                               QSpacerItem, QSizePolicy)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
import time
import os

from core.window_utils import WindowUtil
from core.capture_utils import CaptureManager
from core.tasker import Tasker  # 새로 추가
import stores.task_manager as TaskMan
from core.ocr_engine import setup_tesseract
from core.config import *
from zzz.app_config import *
import zzz.app_config as APP_CONFIG
from ui.nodes.region_selector import RegionSelector
from core.settings_manager import AppSetting

# 각 UI 컴포넌트 import
from zzz.menu_bar import MenuBar
from zzz.status_bar import StatusBar
from zzz.info_bar import InfoBar
from ui.connection_frame import ConnectionFrame
from ui.control_frame import ControlFrame
from ui.noti_frame import NotiFrame
from ui.input_handler_frame import InputHandlerFrame
from ui.log_frame import LogFrame
# from ui.capture_area_frame import CaptureAreaFrame

import stores.sanner as Scanner

class AppUI(QMainWindow):
    status_changed = Signal(str)  # 상태 변경 신호
    
    def __init__(self, settings_manager):
        super().__init__()
        
        # 아이콘 설정
        app_icon = QIcon("zzz/icon.ico")  # 또는 상대 경로
        self.setWindowIcon(app_icon)
    
        # 메인 윈도우 설정
        self.setWindowTitle(APP_CONFIG.AppTitle_nVer())
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
        
        self.tasker = Tasker(self, self.toggle_capture, self.stop_capture, self.capture_manager)
        
        self.region_selector = RegionSelector()
        
        # UI 컴포넌트 생성
        self.setup_ui()
        
        # 시그널 연결
        self.tasker.status_changed.connect(self.status_bar.set_status)
        self.tasker.logframe_addlog.connect(self.log_frame.add_log)
        self.tasker.logframe_addlog_matching.connect(self.log_frame.add_log_matching)
        self.tasker.logframe_addlog_notmatching.connect(self.log_frame.add_log_notmatching)
        self.tasker.logframe_addwarning.connect(self.log_frame.add_warning)
        self.tasker.logframe_adderror.connect(self.log_frame.add_error)
        self.tasker.logframe_addnotice.connect(self.log_frame.add_notice)
        self.tasker.logframe_addchnagetaskstep.connect(self.log_frame.add_chnagetaskstep)
        
        # 마우스 위치 추적을 위한 타이머 설정
        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.track_mouse_position)
        self.mouse_timer.start(100)  # 100ms 간격

    def initialize_ocr(self):
        if not APP_CONFIG.USE_OCR:
            return True
    
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
        self.control_frame = ControlFrame(self,
                                          self.status_changed,
                                          self.toggle_capture,
                                          self.apply_interval,
                                          self.open_capture_area_popup,
                                          self.OpenPopup_TaskEditor
                                          )
        self.main_layout.addWidget(self.control_frame)

        self.noti_frame = NotiFrame(self,
                                    self.Open_NotiEdtor
                                    )
        self.main_layout.addWidget(self.noti_frame)
        
        # if not APP_CONFIG.RELEASE_APP:
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
        # self.info_bar = InfoBar(self)
        self.info_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        if APP_CONFIG.USE_OCR:
            self.main_layout.addWidget(self.info_bar)
        
        # 캡처 설정 저장 변수
        self.capture_settings = None
    
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
                self.control_frame.update_capture_button_text(False)
    
    def open_capture_area_popup(self):
        """캡처 영역 설정 팝업 열기"""
        if not WindowUtil.is_window_valid():
            QMessageBox.critical(self, "오류", "먼저 창에 연결해주세요.")
            return
            
        try:
            # CaptureAreaPopup 인스턴스 생성 (PySide6 버전으로 변환 필요)
            from ui.nodes.capture_area_popup import CaptureAreaPopup
            
            # 현재 설정된 캡처 설정 정보
            # current_settings = self.capture_settings
            
            # 팝업 창 생성
            popup = CaptureAreaPopup(
                self, 
                self.region_selector, 
                self.capture_manager, 
                self.status_changed,  # tkinter의 StringVar 대신 Signal 전달
                self.on_capture_popup_close
            )
            
            # # 현재 설정된 값이 있으면 팝업에 설정
            # if current_settings:
            #     x, y, width, height, interval = current_settings
            #     popup.set_capture_info(x, y, width, height, interval)
                
            # popup.exec()  # 모달 다이얼로그로 표시. 블로킹
            popup.show()    #모달리스
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"캡처 영역 설정 창을 열 수 없습니다: {str(e)}")
            import traceback
            traceback.print_exc()  # 콘솔에 상세 오류 출력
    
    def OpenPopup_TaskEditor(self):
        if not WindowUtil.is_window_valid():
            QMessageBox.critical(self, "오류", "먼저 창에 연결해주세요.")
            return
        
        try:
            from ui.nodes.task_editor_popup import TaskEditorPopup
            # 팝업 창 생성
            popup = TaskEditorPopup(
                self,
                self.tasker,
            )
            
            popup.show()
            # popup.exec()    # 부모 창 제어권 뺏음
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"캡처 영역 설정 창을 열 수 없습니다: {str(e)}")
            import traceback
            traceback.print_exc()  # 콘솔에 상세 오류 출력

    def Open_NotiEdtor(self):
        if not WindowUtil.is_window_valid():
            QMessageBox.critical(self, "오류", "먼저 창에 연결해주세요.")
            return
        
        try:
            from ui.nodes.noti_editor import NotiEditor
            editor = NotiEditor(self)
            editor.show()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"알림 에디터를 열 수 없습니다: {str(e)}")
            import traceback
            traceback.print_exc()  # 콘솔에 상세 오류 출력
            
    def on_capture_popup_close(self, settings):
        """캡처 영역 설정 팝업이 닫힐 때의 콜백"""
        if settings:
            # 캡처 설정 저장
            # self.capture_settings = settings
            
            # 상태바에 설정 정보 표시
            x, y, width, height, clickx, clicky, interval = settings
            status_msg = f"캡처 영역 설정: X={x}, Y={y}, 너비={width}, 클릭x={clickx}, 클릭y={clicky}, 높이={height}, 간격={interval}초"
            self.status_changed.emit(status_msg)
    
    @Slot()
    def toggle_capture(self):
        """캡처 시작/중지 전환"""
        
        # if hasattr(self, '_toggling') and self._toggling:
        #     return
        
        # self._toggling = True
        # QTimer.singleShot(500, lambda: setattr(self, '_toggling', False))
    
        if self.tasker.is_running:
            # 캡처 중지
            self.tasker.stop_tasks()
            self.control_frame.update_capture_button_text(False)
            # 즉시 시작 방지를 위해 버튼 일시적 비활성화
            self.control_frame.capture_btn.setEnabled(False)
            QTimer.singleShot(500, lambda: self.control_frame.capture_btn.setEnabled(True))
        else:
            try:
                # Check if the task was recently stopped (add this flag in Tasker)
                if hasattr(self.tasker, 'recently_stopped') and self.tasker.recently_stopped:
                    # If it was just stopped, don't restart
                    QTimer.singleShot(1000, lambda: setattr(self.tasker, 'recently_stopped', False))
                    return
            
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
                
                # 작업 시작
                self.tasker.start_tasks()
                self.control_frame.update_capture_button_text(True)
                
            except ValueError as e:
                QMessageBox.critical(self, "입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "캡처 오류", f"캡처 시작 중 오류가 발생했습니다: {str(e)}")
                
    def stop_capture(self):
        """Just stop capture without attempting to toggle/restart"""
        if self.tasker.is_running:
            self.tasker.stop_tasks()
            self.control_frame.update_capture_button_text(False)
            # Optional: Disable button temporarily to prevent immediate restart
            self.control_frame.capture_btn.setEnabled(False)
            QTimer.singleShot(200, lambda: self.control_frame.capture_btn.setEnabled(True))
    
    @Slot()
    def apply_interval(self, val):
        try:
            Scanner.Loop_Interval = val
            self.status_changed.emit(f"Loop 간격이 {val:.2f}초로 적용되었습니다.")
        except ValueError:
            QMessageBox.critical(self, "입력 오류", "간격은 숫자 형식으로 입력해주세요.")