from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QComboBox, QLabel, QSizePolicy)
from PySide6.QtCore import Qt

import ui.css as CSS

class NotiFrame(QGroupBox):

    def __init__(self, parent,
                 open_edtor_callback
                 ):
        super().__init__("메시지 알림", parent)
        self.open_edtor_callback = open_edtor_callback
        
        # 토글 상태 변수
        self.notification_enabled = True
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 수평 레이아웃으로 변경하여 버튼, 콤보박스, 토글 버튼을 가로로 배치
        controls_layout = QHBoxLayout()
        
        # 편집 버튼
        edit_btn = QPushButton("편집")
        edit_btn.setStyleSheet(CSS.BUTTON_APPLY_BLUESKY)
        edit_btn.clicked.connect(self.open_edtor_callback)
        edit_btn.setFixedWidth(80)  # 버튼 너비 고정
        controls_layout.addWidget(edit_btn)
        
        # 약간의 공간 추가
        controls_layout.addSpacing(10)
        
        # 콤보박스 추가
        self.notification_combo = QComboBox()
        self.notification_combo.addItems(["텔레그램", "슬랙", "이메일", "카카오톡"])
        self.notification_combo.setFixedWidth(120)  # 콤보박스 너비 고정
        controls_layout.addWidget(self.notification_combo)
        
        # 약간의 공간 추가
        controls_layout.addSpacing(10)
        
        # 토글 버튼 추가
        self.toggle_btn = QPushButton("ON")
        self.toggle_btn.setFixedWidth(60)  # 토글 버튼 너비 고정
        self.toggle_btn.setStyleSheet(self._get_toggle_style(True))  # 초기 스타일 설정
        self.toggle_btn.clicked.connect(self.toggle_notification)
        controls_layout.addWidget(self.toggle_btn)
        
        # 오른쪽에 여백 추가
        controls_layout.addStretch(1)
        
        main_layout.addLayout(controls_layout)
        
        # 나머지 공간을 채우기 위한 여백 추가
        main_layout.addStretch(1)
    
    def toggle_notification(self):
        """알림 활성화/비활성화 토글"""
        self.notification_enabled = not self.notification_enabled
        
        # 버튼 텍스트와 스타일 업데이트
        self.toggle_btn.setText("ON" if self.notification_enabled else "OFF")
        self.toggle_btn.setStyleSheet(self._get_toggle_style(self.notification_enabled))
    
    def _get_toggle_style(self, is_on):
        """토글 버튼의 스타일을 반환"""
        if is_on:
            # ON 상태 스타일 (녹색)
            return """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """
        else:
            # OFF 상태 스타일 (회색)
            return """
                QPushButton {
                    background-color: #aaaaaa;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #999999;
                }
            """