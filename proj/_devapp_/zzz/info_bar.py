from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt
import threading
import mss
import time
import numpy as np

import stores.def_info as Info
from stores.areas import *
import core.ocr_engine as OcrEngine
from core.config import LOOP_TEXT_KEYWORD
from core.window_utils import WindowUtil

class InfoBar(QFrame):
    # 스캔 상태 변경 시그널 추가
    # scan_status_changed = Signal(bool)
    # click_requested = Signal(float, float)  # 클릭 요청 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.parent = parent
        
        # 스캔 상태 변수
        self.is_scanning = False
        self.scan_thread = None
        
        # 전체 레이아웃 설정
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 2, 5, 2)
        
        # 스캔 버튼 추가
        self.scan_button = QPushButton("▶️")
        self.scan_button.setFixedWidth(28)
        self.scan_button.clicked.connect(self.toggle_scan)
        main_layout.addWidget(self.scan_button)
        
        # 왼쪽 여백 추가
        main_layout.addSpacing(5)
        
        # 좌측/우측 프레임 생성
        left_frame = QFrame(self)
        left_layout = QHBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        right_frame = QFrame(self)
        right_layout = QHBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 메인 레이아웃에 좌/우 프레임 추가
        main_layout.addWidget(left_frame, 1)  # 좌측 프레임이 공간을 확장
        main_layout.addWidget(right_frame, 0)  # 우측 프레임은 필요한 크기만큼만 차지
        
        # 값 표시용 입력창들 생성
        # HP 정보
        left_layout.addWidget(QLabel("HP"))
        self.hp_entry = QLineEdit()
        self.hp_entry.setReadOnly(True)
        self.hp_entry.setFixedWidth(60)
        self.hp_entry.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.hp_entry)
        left_layout.addSpacing(10)
        
        # MP 정보
        left_layout.addWidget(QLabel("MP"))
        self.mp_entry = QLineEdit()
        self.mp_entry.setReadOnly(True)
        self.mp_entry.setFixedWidth(60)
        self.mp_entry.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.mp_entry)
        left_layout.addSpacing(10)
        
        # 물약 정보
        left_layout.addWidget(QLabel("물약"))
        self.potion_entry = QLineEdit()
        self.potion_entry.setReadOnly(True)
        self.potion_entry.setFixedWidth(60)
        self.potion_entry.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.potion_entry)
        
        self.is_potion0_entry = QLineEdit()
        self.is_potion0_entry.setReadOnly(True)
        self.is_potion0_entry.setFixedWidth(30)
        self.is_potion0_entry.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.is_potion0_entry)
        left_layout.addSpacing(10)
        
        # 우측에 위치 정보 표시
        self.loc_kind_entry = QLineEdit()
        self.loc_kind_entry.setReadOnly(True)
        self.loc_kind_entry.setFixedWidth(70)
        self.loc_kind_entry.setAlignment(Qt.AlignRight)
        right_layout.addWidget(self.loc_kind_entry)
        
        right_layout.addWidget(QLabel(" / "))
        
        self.loc_name_entry = QLineEdit()
        self.loc_name_entry.setReadOnly(True)
        self.loc_name_entry.setMinimumWidth(120)
        self.loc_name_entry.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(self.loc_name_entry)
        right_layout.addSpacing(15)
        
        # 스타일 설정
        self.setFrameShape(QFrame.StyledPanel)
        
        # # 타이머로 주기적 업데이트
        # self.update_timer = QTimer(self)
        # self.update_timer.timeout.connect(self.update_info)
        
        # 초기 정보 업데이트
        self.update_info()
    
    def toggle_scan(self):
        """스캔 시작/정지 토글"""
        if self.is_scanning:
            self.stop_scan()
        else:
            self.start_scan()
    
    def start_scan(self):
        """스캔 시작"""
        # 이미 스캔 중이거나 스레드가 살아 있다면 중복 실행 방지
        if self.is_scanning or (self.scan_thread and self.scan_thread.is_alive()):
            return

        self.is_scanning = True
        self.scan_button.setText("🟥")
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()
        
        # # 상태 변경 시그널 발생
        # self.scan_status_changed.emit(True)
    
    def stop_scan(self):
        """스캔 중지"""
        if not self.is_scanning:
            return

        self.is_scanning = False
        self.scan_button.setText("▶️")

        # 스레드 종료 대기 및 정리
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=0.5)  # 대기.. 기다리는 시기
        self.scan_thread = None # 참조 제거 → GC 대상
        # 스레드는 scan_loop()가 False == self.is_scanning 로 종료
        
        # 상태 변경 시그널 발생
        # self.scan_status_changed.emit(False)
    
    def scan_loop(self):
        """스캔 루프 - 별도의 스레드에서 실행"""
        # 스레드 내부에서 필요한 객체 생성 - 스레드 안전성 확보
        
        from core.capture_utils import CaptureManager  # 🔁 루프 내부에서 안전하게 import
        captureman = CaptureManager()  # ✅ 스레드 안에서 생성
        
        while self.is_scanning:
            with mss.mss() as sct:
                # 창이 여전히 존재하는지 확인
                if not WindowUtil.update_window_info():
                    # 창이 닫혔으면 스캔 중지
                    self.is_scanning = False
                    # UI 업데이트는 메인 스레드에서 해야 함
                    self.scan_button.setText("▶️")
                    break
                
                # OCR 처리 수행
                # self.process_ocr(captureman, sct)
                if False == self.process_ocr_1Capture(captureman, sct):
                    break
                
                # 지정된 간격만큼 대기
                self.update_info()
                
                # print("scan_loop")
                time.sleep(0.5)
    
    def process_ocr(self, captureman, sct):
        """OCR 처리"""
        for KEY in LOOP_TEXT_KEYWORD:
            try:
                areaitem = Get_TextArea(KEY)
                if areaitem is None:
                    continue
                
                # print(KEY)
                img = captureman._capture_crop(sct, areaitem.x, areaitem.y, areaitem.width, areaitem.height)
                
                if img is None:
                    raise ValueError("캡처된 이미지가 None입니다.")
                    
                text = OcrEngine.image_to_text(img)
                
                # 메모리 관리
                del img
                import gc; gc.collect()
                
                # 값 업데이트
                Info.Update_Value(KEY, text)
                
            except Exception as e:
                Info.Update_Value(KEY, "")
                
    def process_ocr_1Capture(self, captureman, sct):
        images = captureman._capture_crop_AllTextArea(sct)
        if not images:
            return False
        
        for key, image in images.items():
            try:
                # print(f"[{key}] {image}")
                
                text = OcrEngine.image_to_text(image)
                # print(f"[{key}] → {text.strip()}")

                # 값 업데이트
                Info.Update_Value(key, text)
            except Exception as e:
                # print(f"[OCR 에러:{key}] {e}")
                Info.Update_Value(key, "")
                return False
        
        images.clear()
        del images
        return True
    
    def update_info(self):
        """정보 업데이트"""
        def Check_Vital(vital):
            return "Χ" if -1 == vital else str(vital)
        
        self.hp_entry.setText(Check_Vital(Info.HP))
        self.mp_entry.setText(Check_Vital(Info.MP))
        self.potion_entry.setText(Check_Vital(Info.POTION))
        
        # 물약 상태 아이콘 설정
        if 1 == Info.Is_Potion0:
            self.is_potion0_entry.setText("★")
        elif 0 == Info.Is_Potion0:
            self.is_potion0_entry.setText("○")
        elif -1 == Info.Is_Potion0:
            self.is_potion0_entry.setText("Χ")
        
        self.loc_kind_entry.setText(Info.Locate_Kind)
        self.loc_name_entry.setText(Info.Locate_Name)
        
        # 타이머 간격 업데이트
        # self.update_timer.setInterval(Scanner.Get_LoopInterval_MS())
    
    def closeEvent(self, event):
        """창 닫힘 이벤트 - 스레드 정리"""
        # 스캔 중지
        self.stop_scan()
        
        # 부모 창 닫힘 이벤트 처리
        super().closeEvent(event)