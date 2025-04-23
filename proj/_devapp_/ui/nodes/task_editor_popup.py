from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QListWidget, QTabWidget, QWidget, QTextEdit,
                             QGroupBox, QFrame, QCheckBox, QScrollArea,
                             QGridLayout, QApplication, QMessageBox)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, Signal
import sys

class TaskEditorPopup(QDialog):
    """작업 편집기 팝업 창"""
    
    # 상태 신호 정의
    task_saved_signal = Signal(dict)
    
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("작업 편집기")
        self.resize(800, 600)
        
        # 작업 데이터 초기화
        self.task_data = task_data or {}
        
        # UI 설정
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성 설정"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        
        # 상단 영역 - 탭 위젯
        self.tabs = QTabWidget()
        
        # 첫 번째 탭 - 기본
        self.tab_basic = QWidget()
        self._setup_basic_tab()
        self.tabs.addTab(self.tab_basic, "기본")
        
        # 두 번째 탭 - 프리뷰
        self.tab_preview = QWidget()
        self._setup_preview_tab()
        self.tabs.addTab(self.tab_preview, "프리뷰")
        
        # 메인 레이아웃에 탭 추가
        main_layout.addWidget(self.tabs)
        
        # 중앙 영역 - 메인 컨텐츠 (3개의 영역으로 분할)
        center_layout = QHBoxLayout()
        
        # 왼쪽 영역 - 단계 목록
        self.left_panel = self._create_left_panel()
        center_layout.addWidget(self.left_panel)
        
        # 중앙 영역 - 메인 설정 패널 (녹색 테두리)
        self.center_panel = self._create_center_panel()
        center_layout.addWidget(self.center_panel, 2)  # 비율 2
        
        # 오른쪽 영역 - 상세 설정
        self.right_panel = self._create_right_panel()
        center_layout.addWidget(self.right_panel)
        
        main_layout.addLayout(center_layout, 4)  # 비율 4
        
        # 하단 영역 - 미리보기
        preview_group = QGroupBox("미리보기")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("미리보기 내용이 여기에 표시됩니다.")
        preview_layout.addWidget(self.preview_text)
        
        main_layout.addWidget(preview_group)
        
        # 최하단 - 버튼 영역
        buttons_layout = QHBoxLayout()
        
        # 이미지 타입 선택
        image_selection_layout = QHBoxLayout()
        image_selection_layout.addWidget(QLabel("이미지:"))
        self.image_combo = QComboBox()
        self.image_combo.addItems(["이미지 없음", "이미지1", "이미지2", "이미지3"])
        image_selection_layout.addWidget(self.image_combo)
        buttons_layout.addLayout(image_selection_layout)
        
        # 오른쪽에 공간 추가
        buttons_layout.addStretch(1)
        
        # 저장/취소 버튼
        self.save_btn = QPushButton("저장")
        self.save_btn.clicked.connect(self.save_task)
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _setup_basic_tab(self):
        """기본 탭 구성"""
        layout = QHBoxLayout(self.tab_basic)
        
        # 자동화 목록 그룹
        automation_group = QGroupBox("자동화 목록")
        automation_layout = QHBoxLayout(automation_group)
        
        # 왼쪽 - 자동화 목록
        self.automation_list = QListWidget()
        self.automation_list.addItems([f"자동화 항목 {i+1}" for i in range(10)])
        automation_layout.addWidget(self.automation_list)
        
        # 오른쪽 내용을 담을 위젯
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        
        # 검색창 추가 (시작 단계 키 위에 배치)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("검색:"))
        self.automation_search = QLineEdit()
        self.automation_search.setPlaceholderText("검색어 입력...")
        search_layout.addWidget(self.automation_search)
        right_layout.addLayout(search_layout)
        
        # 시작 단계 키 (QLineEdit)
        start_key_layout = QHBoxLayout()
        start_key_layout.addWidget(QLabel("시작 단계 키:"))
        self.start_key_input = QLineEdit("기본 키")
        self.start_key_input.setEnabled(False)
        start_key_layout.addWidget(self.start_key_input)
        right_layout.addLayout(start_key_layout)
        
        # 설명 입력
        right_layout.addWidget(QLabel("설명:"))
        self.task_description = QTextEdit()
        right_layout.addWidget(self.task_description)
        
        automation_layout.addWidget(right_content)
        
        # 전체 레이아웃에 추가
        layout.addWidget(automation_group)
    
    def _setup_preview_tab(self):
        """프리뷰 탭 구성"""
        layout = QVBoxLayout(self.tab_preview)
        
        # 프리뷰 설정 그룹
        preview_settings_group = QGroupBox("프리뷰 설정")
        preview_settings_layout = QGridLayout(preview_settings_group)
        
        # 프리뷰 옵션들
        preview_settings_layout.addWidget(QLabel("표시 옵션:"), 0, 0)
        self.preview_option_combo = QComboBox()
        self.preview_option_combo.addItems(["옵션1", "옵션2", "옵션3"])
        preview_settings_layout.addWidget(self.preview_option_combo, 0, 1)
        
        preview_settings_layout.addWidget(QLabel("갱신 주기:"), 1, 0)
        self.refresh_rate_combo = QComboBox()
        self.refresh_rate_combo.addItems(["빠름", "보통", "느림"])
        preview_settings_layout.addWidget(self.refresh_rate_combo, 1, 1)
        
        layout.addWidget(preview_settings_group)
        
        # 프리뷰 화면
        preview_display_group = QGroupBox("프리뷰 화면")
        preview_display_layout = QVBoxLayout(preview_display_group)
        self.preview_display = QTextEdit()
        self.preview_display.setReadOnly(True)
        self.preview_display.setPlaceholderText("여기에 프리뷰가 표시됩니다.")
        preview_display_layout.addWidget(self.preview_display)
        
        layout.addWidget(preview_display_group, 1)  # 비율 1로 늘어남
    
    def _create_left_panel(self):
        """왼쪽 패널 - 단계 목록 생성"""
        group = QGroupBox("조회/설정 도구")
        layout = QVBoxLayout(group)
        
        # 아이콘 버튼들
        icons_frame = QFrame()
        icons_layout = QVBoxLayout(icons_frame)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_buttons = []
        for icon_name in ["도구1", "도구2", "도구3"]:
            btn = QPushButton(icon_name)
            self.icon_buttons.append(btn)
            icons_layout.addWidget(btn)
        
        layout.addWidget(icons_frame)
        
        # 검색창
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어를 입력하세요")
        layout.addWidget(self.search_input)
        
        # 메인 리스트
        self.task_list = QListWidget()
        self.task_list.addItems([f"작업{i+1}" for i in range(10)])
        layout.addWidget(self.task_list)
        
        # 하단 드롭다운
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["필터1", "필터2", "필터3"])
        layout.addWidget(self.filter_combo)
        
        return group
    
    def _create_center_panel(self):
        """중앙 패널 - 메인 설정 영역"""
        # 프레임으로 구현하여 테두리 설정
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("border: 1px solid green;")
        layout = QVBoxLayout(frame)
        
        # 타입 선택
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("타입:"))
        self.main_type_combo = QComboBox()
        self.main_type_combo.addItems(["이미지", "zone", "텍스트"])
        type_layout.addWidget(self.main_type_combo)
        layout.addLayout(type_layout)
        
        # 영역 선택
        zone_layout = QHBoxLayout()
        zone_layout.addWidget(QLabel("영역:"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItems(["영역1", "영역2", "영역3"])
        zone_layout.addWidget(self.zone_combo)
        layout.addLayout(zone_layout)
        
        # 이미지 선택
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("이미지:"))
        self.image_select_combo = QComboBox()
        self.image_select_combo.addItems(["이미지1", "이미지2", "이미지3"])
        image_layout.addWidget(self.image_select_combo)
        layout.addLayout(image_layout)
        
        # 테스트 영역
        test_layout = QHBoxLayout()
        test_layout.addWidget(QLabel("유닛 테스트:"))
        self.test_input = QLineEdit("30")
        test_layout.addWidget(self.test_input)
        self.test_check = QCheckBox("체크")
        test_layout.addWidget(self.test_check)
        layout.addLayout(test_layout)
        
        # 하단 버튼들
        buttons_layout = QHBoxLayout()
        self.find_btn = QPushButton("찾아보기")
        buttons_layout.addWidget(self.find_btn)
        self.image_btn = QPushButton("이미지")
        buttons_layout.addWidget(self.image_btn)
        layout.addLayout(buttons_layout)
        
        return frame
    
    def _create_right_panel(self):
        """오른쪽 패널 - 상세 설정"""
        group = QGroupBox("상세 설정")
        layout = QVBoxLayout(group)
        
        # 설정 옵션
        layout.addWidget(QLabel("설정 옵션:"))
        self.settings_combo = QComboBox()
        self.settings_combo.addItems(["옵션1", "옵션2", "옵션3"])
        layout.addWidget(self.settings_combo)
        
        # 설정값
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("설정값:"))
        self.setting_value = QLineEdit()
        value_layout.addWidget(self.setting_value)
        layout.addLayout(value_layout)
        
        # 설명 영역
        layout.addWidget(QLabel("설명:"))
        self.settings_desc = QTextEdit()
        self.settings_desc.setPlaceholderText("설정에 대한 설명")
        layout.addWidget(self.settings_desc)
        
        # 적용 버튼
        self.apply_btn = QPushButton("적용")
        layout.addWidget(self.apply_btn)
        
        return group
    
    def save_task(self):
        """작업 저장"""
        self.accept()