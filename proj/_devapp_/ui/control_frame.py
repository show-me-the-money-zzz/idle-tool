from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QDoubleSpinBox, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Slot

import stores.sanner as Scanner
import ui.css as CSS

class ControlFrame(QFrame):
    """캡처 제어 프레임"""
    
    RUNNER_BUTTON_START_TEXT = "스캔 ▶️" 
    RUNNER_BUTTON_STOP_TEXT = "스캔 🟥"
    
    def __init__(self, parent, status_signal, toggle_capture_callback, 
                 apply_interval_callback, open_popup_callback):
        super().__init__(parent)
        self.parent = parent
        self.status_signal = status_signal
        self.toggle_capture_callback = toggle_capture_callback
        self.apply_interval_callback = apply_interval_callback
        self.open_popup_callback = open_popup_callback
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 설정"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # 캡처 시작/중지 버튼
        self.capture_btn = QPushButton(self.RUNNER_BUTTON_START_TEXT)
        self.capture_btn.clicked.connect(self.toggle_capture_callback)
        layout.addWidget(self.capture_btn)
        
        # 간격 프레임
        interval_frame = self.create_interval_frame()
        layout.addWidget(interval_frame)
        
        # 여백 추가
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        # 아이템 생성 버튼
        self.create_item_btn = QPushButton("아이템 생성")
        self.create_item_btn.setStyleSheet(CSS.BUTTON_APPLY)
        self.create_item_btn.clicked.connect(self.open_popup_callback)
        layout.addWidget(self.create_item_btn)
        
        # 크기 정책 설정
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def create_interval_frame(self):
        """간격 설정 프레임 생성"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 0, 10, 0)
        
        interval_label = QLabel("간격(초)")
        layout.addWidget(interval_label)
        
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.00, 3.00)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setValue(Scanner.Loop_Interval)
        self.interval_spin.setDecimals(2)   # 소수점 N자리 허용
        self.interval_spin.setFixedWidth(60)
        layout.addWidget(self.interval_spin)
        
        apply_btn = QPushButton("적용")
        apply_btn.clicked.connect(self.on_apply_interval)
        layout.addWidget(apply_btn)
        
        return frame
    
    def on_apply_interval(self):
        """간격 적용 버튼 클릭 처리"""
        value = self.interval_spin.value()
        self.apply_interval_callback(value)
    
    def update_capture_button_text(self, is_capturing):
        """캡처 버튼 텍스트 업데이트"""
        text = self.RUNNER_BUTTON_STOP_TEXT if is_capturing else self.RUNNER_BUTTON_START_TEXT
        self.capture_btn.setText(text)