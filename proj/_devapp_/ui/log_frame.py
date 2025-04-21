from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QScrollBar, QWidget, QFrame)
from PySide6.QtCore import Qt, Signal, Slot

class LogFrame(QGroupBox):
    """로그 프레임 (이전의 인식된 텍스트 영역)"""
    
    def __init__(self, parent, status_signal):
        super().__init__("로그", parent)
        
        self.status_signal = status_signal
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 버튼 프레임 (상단)
        button_frame = QWidget(self)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(button_frame)
        
        # 버튼 레이아웃에 빈 공간 추가 (왼쪽)
        button_layout.addStretch(1)
        
        # 로그 초기화 버튼
        self.clear_log_btn = QPushButton("로그 초기화")
        self.clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_log_btn)
        
        # 텍스트 영역
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)  # 읽기 전용 설정
        main_layout.addWidget(self.log_text)
        
        # PySide6에서는 QTextEdit이 이미 스크롤바를 내장하고 있음
    
    @Slot()
    def clear_log(self):
        """로그 텍스트 초기화"""
        self.log_text.clear()
        self.status_signal.emit("로그가 초기화되었습니다.")
    
    def add_log(self, text):
        """로그에 텍스트 추가"""
        self.log_text.append(text)
        
        # 스크롤을 최신으로 이동
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())