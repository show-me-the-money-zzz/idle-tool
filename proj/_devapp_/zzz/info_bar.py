from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt, QTimer

import stores.def_info as Info
import core.sanner as Scanner

class InfoBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 전체 레이아웃 설정
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 2, 5, 2)
        
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
        
        # 타이머로 주기적 업데이트
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(Scanner.Get_LoopInterval_MS())
        
        # 초기 정보 업데이트
        self.update_info()
    
    def update_info(self):
        """정보 업데이트"""
        # print(f"tick~~ ({Scanner.Loop_Interval}): {Scanner.Get_LoopInterval_MS()}")
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
        self.update_timer.setInterval(Scanner.Get_LoopInterval_MS())