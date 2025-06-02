from PySide6.QtWidgets import QStatusBar
from PySide6.QtCore import Qt, Signal

class StatusBar(QStatusBar):
    """상태바 클래스"""
    
    # 상태 변경 신호 정의
    status_changed = Signal(str)
    
    def __init__(self, main_window):
        """상태바 초기화"""
        super().__init__(main_window)
        
        # 신호 연결
        self.status_changed.connect(self.set_status)
    
    def set_status(self, text):
        """상태 텍스트 설정"""
        self.showMessage(text)  # QStatusBar의 기본 메시지만 사용
    
    def get_status_signal(self):
        """상태 변경 신호 반환"""
        return self.status_changed