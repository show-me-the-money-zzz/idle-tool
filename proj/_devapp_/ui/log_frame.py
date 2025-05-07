from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QScrollBar, QWidget, QFrame)
from PySide6.QtCore import Qt, Signal, Slot

from datetime import datetime

from stores.task_base_step import TaskStep_Matching

class LogFrame(QGroupBox):
    """로그 프레임 (이전의 인식된 텍스트 영역)"""
    
    def __init__(self, parent, status_signal):
        super().__init__("로그", parent)
        
        self.status_signal = status_signal
        
        self._color_toggle = False

        self.before_step_matching = None
        
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
        self.log_text.setStyleSheet("background-color: #4a4a4a; color: white;")
        self.log_text.setFontPointSize(11)
        main_layout.addWidget(self.log_text)
        
        # PySide6에서는 QTextEdit이 이미 스크롤바를 내장하고 있음
    
    @Slot()
    def clear_log(self):
        """로그 텍스트 초기화"""
        self.log_text.clear()
        self.status_signal.emit("로그가 초기화되었습니다.")
    
    def add_log(self, text):
        color = "#b5b5b5" if self._color_toggle else "#ffffff"
        self.print_log(color, text)
        
        self._color_toggle = not self._color_toggle

    def add_log_matching(self, step: TaskStep_Matching, matched_score: float, issuccess: bool):
        succsstext = "성공" if issuccess else "실패"
        resulttext = f"{matched_score:.1f}%({succsstext})"

        if self.before_step_matching: pass
        else:
            # self.before_step_matching = {
            #     "step": step,
            # }

            logtext = "[[[매칭]]] "
            if 0 < step.waiting:
                logtext += f"(잠깐만 {step.waiting} 초) "
            logtext += f"[영역: {step.zone}]의 [이미지: {step.image}]의 [유사도] {step.Print_Score()}에서: "
            self.add_log(logtext + resulttext)
        
    def add_log_notmatching(self, text):
        # print(f"add_log_notmatching({text})")
        self.before_step_matching = None
        self.add_log(text)
    
    def add_warning(self, text): self.print_log("#ffe88c", text)    
    def add_error(self, text): self.print_log("#ff8c8c", text)
    def add_notice(self, text): self.print_log("#00ff00", text)
        
    def print_log(self, color, text):
        timestamp = datetime.now().strftime("%m/%d %H:%M:%S")
        
        html = f'<span style="color:{color}">[{timestamp}] {text}</span>'
        self.log_text.append(html)
        
        # 스크롤을 최신으로 이동
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())