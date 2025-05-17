from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QSizePolicy, QScrollArea, QWidget)
from PySide6.QtCore import Qt

import stores.noti_store as NotiStores
import ui.css as CSS

class NotiFrame(QGroupBox):

    def __init__(self, parent, open_edtor_callback):
        super().__init__("메시지 알림", parent)
        self.open_edtor_callback = open_edtor_callback
        
        # 알림 아이템 데이터
        self.noti_items = []
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 단일 행 레이아웃 - 편집 버튼과 스크롤 영역을 같은 행에 배치
        row_layout = QHBoxLayout()
        
        # 편집 버튼
        edit_btn = QPushButton("편집")
        edit_btn.setStyleSheet(CSS.BUTTON_ORANGE)
        edit_btn.clicked.connect(self.open_edtor_callback)
        edit_btn.setFixedWidth(80)  # 버튼 너비 고정
        row_layout.addWidget(edit_btn)
        
        # 간격 추가
        row_layout.addSpacing(10)
        
        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # scroll_area.setMaximumHeight(40)  # 스크롤 영역 높이 제한
        scroll_area.setFixedHeight(54)
        
        # 스크롤 영역에 들어갈 컨테이너 위젯
        scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)  # 아이템 간 간격
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 왼쪽 정렬
        
        # 스크롤 영역에 컨테이너 설정
        scroll_area.setWidget(scroll_content)
        
        # 스크롤 영역을 row_layout에 추가하고 확장되도록 설정
        row_layout.addWidget(scroll_area, 1)  # 1은 stretch factor - 공간을 확장하여 차지
        
        # 메인 레이아웃에 row_layout 추가
        main_layout.addLayout(row_layout)
        
        # 나머지 공간을 채우기 위한 여백 추가
        main_layout.addStretch(1)
        
        # 테스트용 아이템 추가
        # self.add_test_items()
        self.Reload_Items()
        
    def Reload_Items(self):
        items = []
        keys = NotiStores.GetAll_Notis().keys()
        for key in keys:
            item = NotiStores.Get_Noti(key)
            if item and item.enable:
                items.append({ "name": item.name, "type": item.type })
        if 0 < len(items): self.update_noti_items(items)
        
    def add_test_items(self):
        """테스트용 알림 아이템 추가"""
        # 여기에 실제 데이터를 연결하면 됩니다
        test_items = [
            {"name": "서버1 알림", "type": "discord"},
            {"name": "텔레그램 알림", "type": "telegram"},
            {"name": "디스코드 공지", "type": "discord"},
            {"name": "일일 보고서", "type": "telegram"},
            {"name": "에러 알림", "type": "discord"},
            {"name": "장기 모니터링", "type": "telegram"},
            {"name": "추가 알림 1", "type": "discord"},  # 스크롤이 보이도록 더 많은 항목 추가
            {"name": "추가 알림 2", "type": "telegram"},
            {"name": "추가 알림 3", "type": "discord"}
        ]
        
        for item in test_items:
            self.add_noti_item(item["name"], item["type"])
    
    def add_noti_item(self, text, noti_type):
        """알림 아이템을 스크롤 영역에 추가"""
        # 타입에 따른 스타일 결정
        color = "#5865f2" if noti_type == "discord" else "#23a0dd"  # discord 또는 telegram
        
        # 버튼 스타일
        style = f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
        """
        
        # 버튼으로 알림 아이템 표시
        btn = QPushButton(text)
        btn.setStyleSheet(style)
        # btn.setEnabled(False)
        
        # 버튼 크기 정책 설정 (텍스트에 맞춰 너비 조정)
        btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # 스크롤 레이아웃에 추가
        self.scroll_layout.addWidget(btn)
        
        # 아이템 저장
        self.noti_items.append({"widget": btn, "text": text, "type": noti_type})
    
    def _darken_color(self, hex_color):
        """색상을 약간 어둡게 만들기 (호버 효과용)"""
        # 16진수 색상을 RGB로 변환
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # 각 색상 값을 10% 어둡게
        factor = 0.9
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        
        # RGB를 16진수로 변환하여 반환
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def update_noti_items(self, items):
        """알림 아이템 목록 업데이트"""
        # 기존 아이템 모두 제거
        for item in self.noti_items:
            self.scroll_layout.removeWidget(item["widget"])
            item["widget"].deleteLater()
        
        self.noti_items = []
        
        # 새 아이템 추가
        for item in items:
            self.add_noti_item(item["name"], item["type"])