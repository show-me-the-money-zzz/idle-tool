from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDoubleSpinBox

from core.config import APP_THEME

class LogDockWidget(QDockWidget):
    """도킹 가능한 로그 위젯"""
    
    def __init__(self, parent):
        super().__init__("인식된 텍스트", parent)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        # self.setAllowedAreas(Qt.NoDockWidgetArea)  # 도킹 영역 없음
        # self.setFeatures(QDockWidget.DockWidgetFloatable)  # 이동만 가능하게
        
        # 부모 참조 저장
        self.parent_dialog = parent
        
        self.floatingPos = "left"
        # --- 🔸 커스텀 타이틀 바 생성 ---
        self.init_title_bar()
        
        # 내용 위젯 생성
        self.content = QWidget()
        layout = QVBoxLayout(self.content)
        
        # 컨트롤 영역 레이아웃
        controls_layout = QHBoxLayout()
        
        # 간격 설정
        controls_layout.addWidget(QLabel("간격(초):"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 10.0)
        self.interval_spin.setValue(1.0)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setFixedWidth(60)
        controls_layout.addWidget(self.interval_spin)
        
        # 텍스트 읽기 버튼
        self.read_text_btn = QPushButton(parent.READTEXT_BUTTON_START_TEXT)
        self.read_text_btn.setFixedWidth(28)
        controls_layout.addWidget(self.read_text_btn)
        
        # 중간 여백
        controls_layout.addStretch(1)
        
        # 로그 초기화 버튼
        self.clear_log_btn = QPushButton("지우기")
        controls_layout.addWidget(self.clear_log_btn)
        
        layout.addLayout(controls_layout)
        
        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        self.setWidget(self.content)
        
    def init_title_bar(self):
        """스왑 버튼이 포함된 타이틀 바 위젯 생성"""
        bar = QWidget()
        
        BG_COLOR = "#ffffff"
        TEXT_COLOR = "#000000"
        if False == ("mac" in APP_THEME.lower()):
            BG_COLOR = "#2b2b2b"
            TEXT_COLOR = "#7f7f7f"
        bar.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR};")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(5, 2, 5, 2)

        title_label = QLabel("OCR - 텍스트 읽기")
        layout.addWidget(title_label)
        layout.addStretch()

        # self.swap_btn = QPushButton("◀▶")
        # self.swap_btn.setFixedSize(30, 20)
        # self.swap_btn.setToolTip("도킹 좌우 위치 전환")
        # self.swap_btn.clicked.connect(self.toggle_dock_side)
        # layout.addWidget(self.swap_btn)

        self.setTitleBarWidget(bar)
        
    def toggle_dock_side(self):
        if "right" == self.floatingPos:
            self.floatingPos = "left"
        elif "left" == self.floatingPos:
            self.floatingPos = "right"
    def Get_FloatingPos(self): return self.floatingPos
    
    def clear_log(self):
        """로그 내용 초기화"""
        self.log_text.clear()
    
    def append_log(self, text):
        """로그에 텍스트 추가"""
        self.log_text.append(text)
        # 스크롤 맨 아래로 이동
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())