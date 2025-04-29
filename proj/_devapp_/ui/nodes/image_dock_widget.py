# ImageDockWidget 클래스 (log_dock_widget 참고하여 생성)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea
from PySide6.QtGui import QPixmap, QImage
from PIL import Image, ImageQt
import os

from zzz.config import APP_THEME

class ImageDockWidget(QDockWidget):
    """도킹 가능한 이미지 뷰어 위젯"""
    
    def __init__(self, parent, title="저장된 이미지"):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        
        # 부모 참조 저장
        self.parent_dialog = parent
        
        self.floatingPos = "right"
        # 커스텀 타이틀 바 생성
        self.init_title_bar()
        
        # 내용 위젯 생성
        self.content = QWidget()
        layout = QVBoxLayout(self.content)
        
        # 스크롤 영역 추가
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 이미지 라벨
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("이미지가 없습니다")
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # 파일 경로 표시
        self.path_label = QLabel("파일 경로: ")
        layout.addWidget(self.path_label)
        
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

        title_label = QLabel("저장된 이미지")
        layout.addWidget(title_label)
        layout.addStretch()

      #   self.swap_btn = QPushButton("◀▶")
      #   self.swap_btn.setFixedSize(30, 20)
      #   self.swap_btn.setToolTip("도킹 좌우 위치 전환")
      #   self.swap_btn.clicked.connect(self.toggle_dock_side)
      #   layout.addWidget(self.swap_btn)

        self.setTitleBarWidget(bar)
        
    def toggle_dock_side(self):
        if "right" == self.floatingPos:
            self.floatingPos = "left"
        elif "left" == self.floatingPos:
            self.floatingPos = "right"
            
    def Get_FloatingPos(self): 
        return self.floatingPos
    
    def load_image(self, file_path):
        """이미지 로드 및 표시"""
        if not file_path or not os.path.exists(file_path):
            self.image_label.setText(f"파일을 찾을 수 없음: {file_path}")
            self.path_label.setText(f"파일 경로: {file_path} (없음)")
            return False
            
        try:
            # PIL 이미지 로드
            pil_image = Image.open(file_path)
            
            # QImage로 변환
            q_image = ImageQt.ImageQt(pil_image)
            
            # QPixmap으로 변환
            pixmap = QPixmap.fromImage(q_image)
            
            # 이미지 라벨에 표시
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)
            
            # 파일 경로 표시
            self.path_label.setText(f"파일 경로: {file_path}")
            
            return True
        except Exception as e:
            self.image_label.setText(f"이미지 로드 오류: {str(e)}")
            self.path_label.setText(f"파일 경로: {file_path} (오류)")
            return False