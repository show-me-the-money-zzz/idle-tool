from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QListWidget, QTabWidget, QWidget, QTextEdit,
                             QGroupBox, QFrame, QCheckBox, QScrollArea,
                             QGridLayout, QApplication, QMessageBox,
                             QDoubleSpinBox, QSizePolicy)  # QDoubleSpinBox와 QSizePolicy 추가
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, Signal
import sys

from ui.component.searchable_comboBox import SearchableComboBox

class TaskEditorPopup(QDialog):
    """작업 편집기 팝업 창"""
    
    # 상태 신호 정의
    task_saved_signal = Signal(dict)
    
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("작업 편집기")
        self.resize(800, 1000)
        
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
        
        # 중앙 영역 - 단계 정보 부분
        center_layout = QVBoxLayout()  # 수직 레이아웃으로 변경
        
        # 단계 기본정보 패널
        self.center_panel = self._create_center_panel()
        center_layout.addWidget(self.center_panel)
        
        # 단계 추가정보 패널 (기본정보 아래에 배치)
        self.right_panel = self._create_right_panel()
        center_layout.addWidget(self.right_panel)
        
        main_layout.addLayout(center_layout, 4)  # 비율 4
        
        # 최하단 - 버튼 영역
        buttons_layout = QHBoxLayout()
        
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
        # 전체 레이아웃은 수직으로 배치
        layout = QVBoxLayout(self.tab_basic)
        
        # 상단 - 자동화 목록 그룹 (가로로 배치)
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
        start_key_layout.addWidget(QLabel("시작 단계:"))
        self.start_key_input = QLineEdit("")
        self.start_key_input.setEnabled(False)
        start_key_layout.addWidget(self.start_key_input)
        right_layout.addLayout(start_key_layout)
        
        # 설명 입력
        right_layout.addWidget(QLabel("설명:"))
        self.task_description = QTextEdit()
        right_layout.addWidget(self.task_description)
        
        automation_layout.addWidget(right_content)
        
        # 상단 그룹을 레이아웃에 추가
        layout.addWidget(automation_group)
        
        # 하단 - 단계 목록 그룹 (왼쪽 패널의 내용을 기본 탭에 포함)
        step_group = QGroupBox("단계 목록")
        step_layout = QVBoxLayout(step_group)
        
        # 검색 영역 (레이블과 입력 필드를 수평으로 배치)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("검색"))
        
        # 검색 입력 필드 추가
        self.taskstep_search = QLineEdit()
        self.taskstep_search.setPlaceholderText("단계 검색...")
        search_layout.addWidget(self.taskstep_search)
        
        step_layout.addLayout(search_layout)
        
        # 단계 리스트
        self.step_list = QListWidget()
        self.step_list.addItems([f"단계{i+1}" for i in range(10)])
        # 선택 변경 시 버튼 상태 업데이트를 위한 이벤트 연결
        self.step_list.itemSelectionChanged.connect(self.update_step_buttons_state)
        step_layout.addWidget(self.step_list)
        
        # 버튼 그룹군
        buttons_layout = QHBoxLayout()
        
        # + 버튼
        self.add_step_btn = QPushButton("✚")
        self.add_step_btn.setToolTip("단계 추가")
        self.add_step_btn.setFixedWidth(32)
        self.add_step_btn.clicked.connect(self.add_step)
        buttons_layout.addWidget(self.add_step_btn)
        
        # - 버튼 (초기에는 비활성화)
        self.remove_step_btn = QPushButton("━")
        self.remove_step_btn.setToolTip("선택한 단계 삭제")
        self.remove_step_btn.setFixedWidth(32)
        self.remove_step_btn.setEnabled(False)  # 초기에는 비활성화
        self.remove_step_btn.clicked.connect(self.remove_step)
        buttons_layout.addWidget(self.remove_step_btn)
        
        # 여백 추가
        buttons_layout.addStretch(1)
        
        step_layout.addLayout(buttons_layout)
        
        # 하단 그룹을 레이아웃에 추가
        layout.addWidget(step_group)
    
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
    
    def _create_center_panel(self):
        """중앙 패널 - 단계 기본정보 영역"""
        # GroupBox로 변경
        group = QGroupBox("단계 기본정보")
        layout = QVBoxLayout(group)
        
        # 최소 레이블 너비 계산 (가장 긴 레이블에 맞춤)
        min_label_width = 60  # 기본값
        
        # 타입 선택 - 레이블 폭 조절 및 콤보박스 항목 길이에 맞춤
        type_layout = QHBoxLayout()
        type_label = QLabel("타입:")
        type_label.setFixedWidth(min_label_width)
        type_layout.addWidget(type_label)
        
        self.main_type_combo = QComboBox()
        type_items = ["이미지", "zone", "텍스트"]
        self.main_type_combo.addItems(type_items)
        
        # 항목 최대 길이에 맞게 너비 계산
        fm = self.main_type_combo.fontMetrics()
        max_width = 0
        for item in type_items:
            width = fm.horizontalAdvance(item) + 30  # 약간의 여백 추가
            if width > max_width:
                max_width = width
        self.main_type_combo.setMinimumWidth(max_width)
        
        # SizePolicy 설정 - 최소 너비 유지, 확장 안함
        self.main_type_combo.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        type_layout.addWidget(self.main_type_combo)
        
        # 오른쪽 여백 추가
        type_layout.addStretch(1)
        
        # "시작 단계로 설정" 체크박스를 타입 행의 오른쪽 끝으로 이동
        self.start_step_checkbox = QCheckBox("시작 단계로 설정")
        type_layout.addWidget(self.start_step_checkbox)
        
        layout.addLayout(type_layout)
        
        # 이름 입력 필드 (타입과 영역 사이에 추가)
        name_layout = QHBoxLayout()
        name_label = QLabel("이름:")
        name_label.setFixedWidth(min_label_width)
        name_layout.addWidget(name_label)
        
        self.step_name_edit = QLineEdit()
        self.step_name_edit.setPlaceholderText("단계 이름을 입력하세요")
        name_layout.addWidget(self.step_name_edit)
        
        layout.addLayout(name_layout)
        
        # 영역 선택 - 검색 가능한 콤보박스로 변경
        zone_layout = QHBoxLayout()
        zone_label = QLabel("영역:")
        zone_label.setFixedWidth(min_label_width)
        zone_layout.addWidget(zone_label)
        
        # 많은 샘플 항목 생성
        zone_items = [f"영역{i}" for i in range(1, 31)]
        self.zone_combo = SearchableComboBox(items=zone_items)
        self.zone_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        zone_layout.addWidget(self.zone_combo)
        
        layout.addLayout(zone_layout)
        
        # 이미지 선택 - 검색 가능한 콤보박스로 변경
        image_layout = QHBoxLayout()
        image_label = QLabel("이미지:")
        image_label.setFixedWidth(min_label_width)
        image_layout.addWidget(image_label)
        
        # 많은 샘플 항목 생성
        image_items = [f"이미지{i}" for i in range(1, 31)]
        self.image_select_combo = SearchableComboBox(items=image_items)
        self.image_select_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        image_layout.addWidget(self.image_select_combo)
        
        layout.addLayout(image_layout)
        
        # 유사도 영역 - SpinBox와 콤보박스 크기 조정
        similarity_layout = QHBoxLayout()
        similarity_label = QLabel("유사도:")
        similarity_label.setFixedWidth(min_label_width)
        similarity_layout.addWidget(similarity_label)
        
        # SpinBox 폭 절반으로 조정
        self.similarity_spin = QDoubleSpinBox()
        self.similarity_spin.setRange(0, 100.00)
        self.similarity_spin.setSingleStep(1.0)
        self.similarity_spin.setDecimals(2)
        self.similarity_spin.setValue(80.00)
        self.similarity_spin.setMaximumWidth(100)  # 폭 제한
        similarity_layout.addWidget(self.similarity_spin)
        
        # 비교 연산자 콤보박스 폭 조정
        self.comparison_combo = QComboBox()
        self.comparison_combo.addItems(["이상", "초과", "이하", "미만", "일치", "다른"])
        self.comparison_combo.setMaximumWidth(100)  # 폭 제한
        similarity_layout.addWidget(self.comparison_combo)
        
        # 오른쪽 여백 추가
        similarity_layout.addStretch(1)
        
        # "현재 게임에서" 버튼 추가 (오른쪽 정렬)
        self.current_game_btn = QPushButton("현재 게임에서")
        self.current_game_btn.setMaximumWidth(120)  # 폭 제한
        similarity_layout.addWidget(self.current_game_btn)
        
        layout.addLayout(similarity_layout)
        
        # 클릭 선택 영역 (빈 값 허용)
        click_layout = QHBoxLayout()
        click_label = QLabel("클릭:")
        click_label.setFixedWidth(min_label_width)
        click_layout.addWidget(click_label)
        
        # 클릭 콤보박스 항목 길이에 맞춤
        click_items = ["", "이미지", "영역"]
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(click_items)
        
        # 항목 최대 길이에 맞게 너비 계산
        fm = self.click_type_combo.fontMetrics()
        max_width = 0
        for item in click_items:
            width = fm.horizontalAdvance(item) + 30  # 약간의 여백 추가
            if width > max_width:
                max_width = width
        self.click_type_combo.setMinimumWidth(max_width)
        
        # SizePolicy 설정 - 최소 너비 유지, 확장 안함
        self.click_type_combo.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        click_layout.addWidget(self.click_type_combo)
        
        # 오른쪽 여백 추가
        click_layout.addStretch(1)
        
        layout.addLayout(click_layout)
        
        # 가이드 레이블 추가 (최하단)
        guide_layout = QHBoxLayout()
        guide_label = QLabel("※영역 / 이미지는 검색 가능")
        guide_label.setStyleSheet("color: gray; font-size: 9pt;")  # 작은 회색 텍스트
        guide_layout.addWidget(guide_label)
        guide_layout.addStretch(1)  # 오른쪽 여백 추가
        
        layout.addLayout(guide_layout)
        
        return group
    
    def _create_right_panel(self):
        """오른쪽 패널 - 단계 추가정보"""
        group = QGroupBox("단계 추가정보")
        layout = QVBoxLayout(group)
        
        # 최소 레이블 너비 계산 (가장 긴 레이블에 맞춤)
        min_label_width = 80  # 기본값 - "실패 후 단계:"에 맞게 조정
        
        # 실패 후 단계 - 검색 가능한 콤보박스
        fail_step_layout = QHBoxLayout()
        fail_step_label = QLabel("실패 후 단계:")
        fail_step_label.setFixedWidth(min_label_width)
        fail_step_layout.addWidget(fail_step_label)
        
        # 샘플 항목 생성
        fail_step_items = [ "" ]
        fail_step_items += [ f"단계{i}" for i in range(1, 31)]
        self.fail_step_combo = SearchableComboBox(items=fail_step_items)
        self.fail_step_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fail_step_layout.addWidget(self.fail_step_combo)
        
        layout.addLayout(fail_step_layout)
        
        # 다음 단계 - 검색 가능한 콤보박스
        next_step_layout = QHBoxLayout()
        next_step_label = QLabel("다음 단계:")
        next_step_label.setFixedWidth(min_label_width)
        next_step_layout.addWidget(next_step_label)
        
        # 샘플 항목 생성
        next_step_items = [f"단계{i}" for i in range(1, 31)]
        self.next_step_combo = SearchableComboBox(items=next_step_items)
        self.next_step_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        next_step_layout.addWidget(self.next_step_combo)
        
        # 추가 버튼
        self.add_next_step_btn = QPushButton("✚")
        self.add_next_step_btn.setFixedWidth(30)
        self.add_next_step_btn.setToolTip("다음 단계 추가")
        self.add_next_step_btn.clicked.connect(self.add_next_step)
        next_step_layout.addWidget(self.add_next_step_btn)
        
        self.remove_next_step_btn = QPushButton("━")
        self.remove_next_step_btn.setFixedWidth(30)
        self.remove_next_step_btn.setToolTip("선택한 다음 단계 삭제")
        self.remove_next_step_btn.setEnabled(False)  # 초기에는 비활성화
        self.remove_next_step_btn.clicked.connect(self.remove_next_step)
        next_step_layout.addWidget(self.remove_next_step_btn)
        
        layout.addLayout(next_step_layout)
        
        # 다음 단계 목록 - QListWidget
        next_steps_list_layout = QVBoxLayout()
        self.next_steps_list = QListWidget()
        self.next_steps_list.setMinimumHeight(100)  # 최소 높이 설정
        
        # 리스트 항목 선택 시 삭제 버튼 활성화를 위한 연결
        self.next_steps_list.itemSelectionChanged.connect(self.update_next_step_buttons_state)
        
        next_steps_list_layout.addWidget(self.next_steps_list)
        
        layout.addLayout(next_steps_list_layout)
        
        # 여백 추가
        layout.addStretch(1)
        
        # 참고 레이블 추가 (최하단)
        guide_layout = QHBoxLayout()
        guide_label = QLabel("※검색 가능")
        guide_label.setStyleSheet("color: gray; font-size: 9pt;")  # 작은 회색 텍스트
        guide_layout.addWidget(guide_label)
        guide_layout.addStretch(1)  # 오른쪽 여백 추가
        
        layout.addLayout(guide_layout)
        
        return group

    # 다음단계 관련 메서드 추가
    def add_next_step(self):
        """다음 단계 추가"""
        current_text = self.next_step_combo.currentText()
        if current_text:
            # 중복 확인
            for i in range(self.next_steps_list.count()):
                if self.next_steps_list.item(i).text() == current_text:
                    return  # 이미 있는 항목이면 추가하지 않음
            
            # 새 항목 추가
            self.next_steps_list.addItem(current_text)

    def remove_next_step(self):
        """선택한 다음 단계 삭제"""
        selected_items = self.next_steps_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.next_steps_list.row(item)
                self.next_steps_list.takeItem(row)
            
            # 버튼 상태 업데이트
            self.update_next_step_buttons_state()

    def update_next_step_buttons_state(self):
        """다음 단계 항목 선택 상태에 따라 버튼 활성화 상태 업데이트"""
        # 선택된 항목이 있는지 확인
        has_selection = len(self.next_steps_list.selectedItems()) > 0
        
        # 삭제 버튼 활성화/비활성화
        self.remove_next_step_btn.setEnabled(has_selection)

    def update_step_buttons_state(self):
        """단계 선택 상태에 따라 버튼 활성화 상태 업데이트"""
        # 선택된 항목이 있는지 확인
        has_selection = len(self.step_list.selectedItems()) > 0
        
        # 삭제 버튼 활성화/비활성화
        self.remove_step_btn.setEnabled(has_selection)

    def add_step(self):
        """새 단계 추가"""
        # 현재 항목 수 확인
        count = self.step_list.count()
        
        # 새 항목 추가
        self.step_list.addItem(f"새 단계 {count+1}")
        
        # 새 항목 선택
        self.step_list.setCurrentRow(count)

    def remove_step(self):
        """선택한 단계 삭제"""
        # 현재 선택된 행 가져오기
        current_row = self.step_list.currentRow()
        
        # 유효한 행이 선택되었는지 확인
        if current_row >= 0:
            # 항목 삭제
            self.step_list.takeItem(current_row)
            
            # 버튼 상태 업데이트
            self.update_step_buttons_state()
    
    def save_task(self):
        """작업 저장"""
        self.accept()