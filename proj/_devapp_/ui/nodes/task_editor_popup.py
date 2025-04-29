from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QListWidget, QTabWidget, QWidget, QTextEdit,
                             QGroupBox, QFrame, QCheckBox, QScrollArea,
                             QGridLayout, QApplication, QMessageBox,
                             QDoubleSpinBox, QSizePolicy, QInputDialog)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, Signal, QEvent
import sys
import copy

from ui.component.searchable_comboBox import SearchableComboBox

import stores.task_manager as TaskMan
import stores.areas as Areas
from grinder_types.selected_task  import SelectedTask
import ui.css as CSS
from grinder_utils.pysider import ChangeText_ListWidget

class TaskEditorPopup(QDialog):
    """작업 편집기 팝업 창"""
    
    # 상태 신호 정의
    task_saved_signal = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("작업 편집기")
        self.resize(720, 1000)
        
        self.selectedTask = SelectedTask(
            origin_key="",
            current_key="",
            task=None,
            origin_step_key = "",
            current_step_key="")
        
        # UI 설정
        self._setup_ui()
        self.Connect_ChangedUI()
        
        self.Reload_Tasks()
    
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
        
        # 왼쪽에 취소 버튼 배치
        self.cancel_btn = QPushButton("닫기")
        self.cancel_btn.setStyleSheet(CSS.BUTTON_CANCEL)
        self.cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_btn)

        # 오른쪽 버튼들을 위한 공간 추가
        buttons_layout.addStretch(1)

        # 다시 불러오기 버튼 추가 (오른쪽 첫 번째)
        self.reload_btn = QPushButton("리셋")
        self.reload_btn.setStyleSheet(CSS.BUTTON_APPLY2)  # 적절한 스타일 적용
        self.reload_btn.clicked.connect(self.OnClick_Reload)  # 다시 불러오기 기능 연결
        buttons_layout.addWidget(self.reload_btn)

        # 저장 버튼 (오른쪽 끝)
        self.save_btn = QPushButton("저장")
        self.save_btn.setStyleSheet(CSS.BUTTON_APPLY)
        self.save_btn.clicked.connect(self.save_task)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
        
    def Connect_ChangedUI(self):
        self.automation_name_edit.textChanged.connect(lambda task_name: self.selectedTask.UpdateTask_Key(task_name))
        self.task_description.textChanged.connect(lambda: self.selectedTask.UpdateTask_Comment(self.task_description.toPlainText()))
        self.start_step_checkbox.stateChanged.connect(self.ProcessCheck_StartSetp)
        
        # self.main_type_combo.currentTextChanged.connect(lambda type: print(f"type= {type}"))
        self.waiting_spin.valueChanged.connect(lambda waiting: self.selectedTask.UpdateStep_Waiting(waiting))
        self.step_name_edit.textChanged.connect(lambda step_name: self.selectedTask.UpdateStep_Key(step_name))
        self.zone_combo.currentTextChanged.connect(lambda zone: self.selectedTask.UpdateStep_Zone(zone))
        self.image_select_combo.currentTextChanged.connect(lambda image: self.selectedTask.UpdateStep_Image(image))
        self.similarity_spin.valueChanged.connect(lambda similarity: self.selectedTask.UpdateStep_ScoreVal(similarity))
        self.comparison_combo.currentTextChanged.connect(lambda comparison: self.selectedTask.UpdateStep_ScoreDesc(comparison))
        self.click_type_combo.currentTextChanged.connect(lambda click: self.selectedTask.UpdateStep_ClickType(click))
        
        self.fail_step_combo.currentTextChanged.connect(lambda step: self.selectedTask.UpdateStep_FailStep(step))

        # # self.next_steps_list.itemChanged.connect(lambda next_steps: print(f"fail_step= {next_steps}"))
        ## self.selectedTask.UpdateStep_NextSteps에서 처리

        self.step_description.textChanged.connect(lambda: self.selectedTask.UpdateStep_Comment(self.step_description.toPlainText()))
        # print("Connect_ChangedUI")
    def ProcessCheck_StartSetp(self, state):
        startkey = self.selectedTask.UpdateTask_StartStepKey(state)
        self.start_step_checkbox.setEnabled(False)
        if "" != startkey: self.start_key_input.setText(startkey)
        
    def Reload_Tasks(self):
        # 작업 데이터 초기화
        self.tasks = TaskMan.GetAll_Tasks()
        def DevTest_Tasks():
            # for key, task in self.tasks.items():
            #     print(f"[{key}] {task}")
            task_keyz = self.tasks.keys()
            # print(f"{task_keyz}")
            사냥1 = self.tasks.get('사냥1')
            # print(f"{사냥1}")
            # 사냥1_keyz = 사냥1.steps.keys()
            # print(f"{사냥1_keyz}")
            사냥1_표준치료제찾기 = 사냥1.steps.get("표준치료제찾기")
            print(f"{사냥1_표준치료제찾기}")
        # DevTest_Tasks()
        def DevTest_Selected():
            selectedTask = SelectedTask(
                origin_key="aa",
                current_key="",
                task=None,
                origin_step_key = "",
                current_step_key="")
            print(f"{selectedTask.origin_key}, {selectedTask.task}")
            
            taskkey = "사냥1"
            selectedTask.Set_Task(taskkey, self.tasks.get(taskkey))
            # selectedTask.origin_key = "사냥1"
            # selectedTask.task = self.tasks.get(selectedTask.origin_key)
            # print(f"{selectedTask.task}")
            # selectedTask.current_key = "사냥-손창욱"    # selectedTask.task가 변경될 때 원본 데이터 대체
            selectedTask.ChangeKey_CurrentTask("사냥-손창욱")   # selectedTask.task가 변경될 때 원본 데이터 대체
            
            # selectedTask.origin_step_key = "잡화상점이동"
            selectedTask.Set_StepKey("잡화상점 확인")
            step = selectedTask.Get_Step()
            print(f"{step}")
            # selectedTask.current_step_key = "잡화상점이동해야지"    # origin_step_key 데이터를 복사해서 current_step_key 키로 저장
            selectedTask.ChangeKey_CurrentStep("잡화상점이동해야지")    # origin_step_key 데이터를 복사해서 current_step_key 키로 저장
        # DevTest_Selected()
        
        self.initialize_data()
        
    def initialize_data(self):
        """작업 목록 초기화"""
        self.automation_list.clear() # 기존 항목 모두 제거
        self.step_list.clear()  # 단계 리스트 초기화
        
        # 작업 데이터에서 키 가져와서 추가
        for key in self.tasks.keys():
        # for taskkey, steps in self.tasks.items():
            # addItem 사용 - 문자열 그대로 추가
            self.automation_list.addItem(key)
        # self.automation_list.addItem("하하호호")  # DEV TEST
        # self.automation_list.addItem("즐겁다")  # DEV TEST
        
        self.waiting_spin.setValue(0.0)
        self.step_name_edit.setText("")
        self.start_step_checkbox.setChecked(False)
        self.start_step_checkbox.setEnabled(False)
        
        self.zone_combo.clear()
        self.zone_combo.addItem("")
        for keys in Areas.GetAll_ZoneAreas().keys():
            self.zone_combo.addItem(keys)
        
        self.image_select_combo.clear()
        self.image_select_combo.addItem("")
        for keys in Areas.GetAll_ImageAreas().keys():
            self.image_select_combo.addItem(keys)
        self.similarity_spin.setValue(80.0)
        self.comparison_combo.setCurrentIndex(0)
        self.click_type_combo.setCurrentIndex(0)
        
        self.fail_step_combo.clear()
        self.next_step_combo.clear()
        self.step_description.setText("")
        
    def _setup_basic_tab(self):
        """기본 탭 구성"""
        # 전체 레이아웃은 수직으로 배치
        layout = QVBoxLayout(self.tab_basic)
        
        # 상단 - 자동화 목록 그룹 (가로로 배치)
        automation_group = QGroupBox("자동화 목록")
        automation_layout = QHBoxLayout(automation_group)
        
        # 왼쪽 영역 - 자동화 목록과 버튼들을 수직으로 배치
        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 자동화 목록 - 비어있는 상태로 초기화
        self.automation_list = QListWidget()
        # self.automation_list.addItems([f"자동화 항목 {i+1}" for i in range(10)])
        # # 임시 테스트용 항목 (실제로는 initialize_automation_list()에서 초기화)
        # # 올바른 방법 1: addItem 사용
        # self.automation_list.addItem("사냥1")  # 하나의 항목으로 추가
        
        # # 올바른 방법 2: 리스트로 전달
        # # self.automation_list.addItems(["사냥1"])  # 리스트 형태로 전달
        
        # 항목을 더블 클릭하면 수정 가능하도록 설정
        # self.automation_list.itemDoubleClicked.connect(lambda: self.edit_automation_item(self.automation_list.currentItem(), False))
        
        # 선택 변경 시 삭제 버튼 활성화
        self.automation_list.itemSelectionChanged.connect(self.update_automation_buttons_state)
        # Enter 키 이벤트 처리를 위한 이벤트 필터 설치
        self.automation_list.installEventFilter(self)
        
        left_layout.addWidget(self.automation_list)
        
        # 버튼 그룹 - 자동화 목록 하단
        automation_buttons_layout = QHBoxLayout()
        
        # 자동화 이름 편집 필드 추가
        self.automation_name_edit = QLineEdit()
        self.automation_name_edit.setPlaceholderText("자동화 이름 입력...")
        automation_buttons_layout.addWidget(self.automation_name_edit, 1)  # 가중치 1로 설정하여 확장되게 함
        
        # 버튼 컨테이너 (우측 정렬을 위한)
        button_container = QHBoxLayout()
        button_container.setContentsMargins(0, 0, 0, 0)
        button_container.setSpacing(2)  # 버튼 간 간격 축소
        
        # + 버튼 (크기 축소)
        self.add_automation_btn = QPushButton("✚")
        self.add_automation_btn.setToolTip("자동화 추가")
        self.add_automation_btn.setFixedWidth(24)  # 크기 축소
        self.add_automation_btn.setFixedHeight(24) # 크기 축소
        self.add_automation_btn.clicked.connect(self.add_automation)
        button_container.addWidget(self.add_automation_btn)
        
        # - 버튼 (크기 축소, 초기에는 비활성화)
        self.remove_automation_btn = QPushButton("━")
        self.remove_automation_btn.setToolTip("선택한 자동화 삭제")
        self.remove_automation_btn.setFixedWidth(24)  # 크기 축소
        self.remove_automation_btn.setFixedHeight(24) # 크기 축소
        self.remove_automation_btn.setEnabled(False)  # 초기에는 비활성화
        self.remove_automation_btn.clicked.connect(self.remove_automation)
        button_container.addWidget(self.remove_automation_btn)
        
        # 버튼 컨테이너를 메인 레이아웃에 추가
        automation_buttons_layout.addLayout(button_container)
        
        left_layout.addLayout(automation_buttons_layout)
        
        automation_layout.addWidget(left_content)
        
        # # 자동화 이름 적용 버튼 핸들러 추가
        # self.automation_name_edit.returnPressed.connect(self.apply_automation_name)
        self.automation_name_edit.returnPressed.connect(lambda: None)
        
        # 오른쪽 내용을 담을 위젯
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        
        # 검색창 추가 (시작 단계 키 위에 배치)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("검색:"))
        self.automation_search = QLineEdit()
        self.automation_search.setPlaceholderText("검색어 입력...")
        self.automation_search.textChanged.connect(self.filter_automation_list)
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
        layout.addWidget(automation_group, 1)  # 비율 1
        
        # 하단 그룹은 변경 없이 유지...
        # (이하 코드는 동일)
        
        # 하단 - 단계 목록 그룹 (왼쪽 패널의 내용을 기본 탭에 포함)
        step_group = QGroupBox("단계 목록")
        step_layout = QVBoxLayout(step_group)
        
        # 검색 영역 (레이블과 입력 필드를 수평으로 배치)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("검색"))
        
        # 검색 입력 필드 추가
        self.taskstep_search = QLineEdit()
        self.taskstep_search.setPlaceholderText("단계 검색...")
        self.taskstep_search.textChanged.connect(self.filter_step_list)
        search_layout.addWidget(self.taskstep_search)
        
        step_layout.addLayout(search_layout)
        
        # 단계 리스트 - 높이 증가
        self.step_list = QListWidget()
        self.step_list.setMinimumHeight(160)  # 최소 높이 설정 추가
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
        
        # 하단 그룹을 레이아웃에 추가 - 비율 증가
        layout.addWidget(step_group, 2)  # 비율 2로 증가
        
    # 클래스 내에 이벤트 필터 메서드 추가
    def eventFilter(self, obj, event):
        # automation_list에서 Enter 키를 눌렀을 때의 동작 처리
        if obj == self.automation_list and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Enter 키 이벤트를 소비하고 false 반환하여 기본 동작 막기
                return True
    
        # 기본 이벤트 처리로 돌아가기
        return super().eventFilter(obj, event)
    
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
        type_items = ["영역-이미지 매칭",
                    #   "기다리기", "클릭",
                    ]
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
        
        # "잠깐만~" 입력 필드 추가 (타입과 이름 사이에 추가)
        waiting_layout = QHBoxLayout()
        waiting_label = QLabel("잠깐만~")
        waiting_label.setFixedWidth(min_label_width)
        waiting_layout.addWidget(waiting_label)
        
        # SpinBox 설정 (100.00 ~ 0.00, 1.0씩 변경)
        self.waiting_spin = QDoubleSpinBox()
        self.waiting_spin.setRange(0.00, 100.00)  # 0.00 ~ 100.00 사이
        self.waiting_spin.setSingleStep(1.0)      # 1.0 단위로 변경
        self.waiting_spin.setDecimals(2)          # 소수점 2자리까지 표시
        self.waiting_spin.setValue(1.00)          # 기본값 설정
        waiting_layout.addWidget(self.waiting_spin)
        
        # 오른쪽 여백 추가
        waiting_layout.addStretch(1)
        
        layout.addLayout(waiting_layout)
        
        # 이름 입력 필드 (잠깐만~과 영역 사이에 배치)
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
        # fail_step_items = [ "" ]
        # fail_step_items += [ f"단계{i}" for i in range(1, 31)]
        self.fail_step_combo = SearchableComboBox(items=[ "" ])
        self.fail_step_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fail_step_layout.addWidget(self.fail_step_combo)
        
        layout.addLayout(fail_step_layout)
        
        # 다음 단계 - 검색 가능한 콤보박스
        next_step_layout = QHBoxLayout()
        next_step_label = QLabel("다음 단계:")
        next_step_label.setFixedWidth(min_label_width)
        next_step_layout.addWidget(next_step_label)
        
        # 샘플 항목 생성
        # next_step_items = [f"단계{i}" for i in range(1, 31)]
        self.next_step_combo = SearchableComboBox(items=[ "" ])
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
        
        # 설명 입력 영역
        layout.addWidget(QLabel("설명:"))
        self.step_description = QTextEdit()
        self.step_description.setMinimumHeight(40)  # 최소 높이 설정
        layout.addWidget(self.step_description)
        
        # 여백 추가 (설명 컨트롤 추가로 여백 제거)
        # layout.addStretch(1)
        
        # 참고 레이블 추가 (최하단)
        guide_layout = QHBoxLayout()
        guide_label = QLabel("※실패 후 단계 / 다음 단계는 검색 가능")
        guide_label.setStyleSheet("color: gray; font-size: 9pt;")  # 작은 회색 텍스트
        guide_layout.addWidget(guide_label)
        guide_layout.addStretch(1)  # 오른쪽 여백 추가
        
        layout.addLayout(guide_layout)
        
        return group
        
    def apply_automation_name(self):
        """자동화 이름을 현재 선택된 항목에 적용"""
        current_item = self.automation_list.currentItem()
        if current_item:
            new_name = self.automation_name_edit.text().strip()
            if new_name:
                current_item.setText(new_name)
            
    # 자동화 목록 관련 메서드 추가
    def update_automation_buttons_state(self):
        """자동화 항목 선택 상태에 따라 버튼 활성화 상태 업데이트"""

        if self.selectedTask.IsSelect():
            originkey, currentkey = self.selectedTask.Get_Keys()
            isChanged = (originkey != currentkey)
            # print(f"key 변경= {isChanged}")
        
            if not isChanged:
                orgintask = self.tasks.get(originkey)
                if orgintask:
                    deeporgintask = copy.deepcopy(orgintask)
                    isChanged = (deeporgintask != self.selectedTask.task)
                    
            if isChanged:
                # X 버튼은 QMessageBox.No 또는 QMessageBox.Cancel 값과 같은 결과 반환
                reply = QMessageBox.question(self, '데이트 수정됨',
                                             "수정된 데이터를 저장하시겠습니까?\n" +
                                             "('No'는 저장된 상태로 돌아갑니다.)",
                                             QMessageBox.Yes | QMessageBox.No,  # 포함 버튼들
                                             QMessageBox.Yes    # 기본 버튼(Enter 키 누를 때 선택되는 버튼)
                                             )
                if QMessageBox.Yes == reply:
                    print("update_automation_buttons_state(): 파일 저장")
                    newtask = TaskMan.Update_Task(originkey, self.selectedTask.task, currentkey)
                    if newtask:
                        self.tasks = newtask

                        if (originkey != currentkey):
                            ChangeText_ListWidget(self.automation_list, originkey, currentkey)
                    # print(self.tasks.items())
                # elif QMessageBox.No == reply:
                else:
                    print("파일 저장 취소 (리로드)")
                    # self.Reload_Tasks()   # 테스트 하기
        
        self.selectedTask.Reset_Task()
        
        self.step_list.clear()
        self.start_key_input.setText("")
        self.task_description.setText("")
        self.start_step_checkbox.setChecked(False)
        self.start_step_checkbox.setEnabled(False)
        self.step_name_edit.setText("")
        
        self.zone_combo.setCurrentText("")
        self.image_select_combo.setCurrentText("")
        
        self.fail_step_combo.clear()
        self.next_step_combo.clear()
        self.step_description.setText("")
        
        # 여기까지 초기화
        
        items = self.automation_list.selectedItems()
        has_selection = len(items) > 0
        self.remove_automation_btn.setEnabled(has_selection)
        
        # 선택된 항목이 있으면 이름 편집 필드에 표시
        if has_selection:
            selectedItem = items[0]
            self.automation_name_edit.setText(selectedItem.text())
            
            key = selectedItem.text()
            task = self.tasks.get(key)
            
            if not task:
                return
            
            self.selectedTask.Set_Task(key, task)
            
            self.start_key_input.setText(task.start_key)
            self.task_description.setText(task.comment)
            
            self.fail_step_combo.addItem("")
            self.next_step_combo.addItem("")
            for key in task.steps.keys():
                self.step_list.addItem(key)
                self.fail_step_combo.addItem(key)
                self.next_step_combo.addItem(key)
        else:
            # 선택된 항목이 없으면 이름 편집 필드 비우기
            self.automation_name_edit.clear()

    def update_step_buttons_state(self):
        """단계 선택 상태에 따라 버튼 활성화 상태 업데이트"""
        if self.selectedTask.IsSelectStep() and not self.selectedTask.IsSame_StepKey():
            # 키가 변경되었으면
            newsteps = self.selectedTask.Swap_StepKey()
            if newsteps:
                # print(f"{newsteps}")
                originkey, currentkey = self.selectedTask.Get_StepKeys()
                if originkey == self.start_key_input.text():    # 시작 키 input 변경
                    self.start_key_input.setText(currentkey)

                # 키 리스트 사용하는 combobox 업데이트
                self.step_list.clear()
                self.fail_step_combo.clear()
                self.next_step_combo.clear()

                self.fail_step_combo.addItem("")
                self.next_step_combo.addItem("")
                for key in newsteps.keys():
                    self.step_list.addItem(key)
                    self.fail_step_combo.addItem(key)
                    self.next_step_combo.addItem(key)
        # 선택된 항목이 있는지 확인
        self.selectedTask.Reset_Step()
        
        # self.main_type_combo
        self.start_step_checkbox.setChecked(False)
        self.start_step_checkbox.setEnabled(False)
        self.waiting_spin.setValue(0.00)
        self.step_name_edit.setText("")
        
        self.zone_combo.setCurrentText("")
        self.image_select_combo.setCurrentText("")
        
        self.similarity_spin.setValue(70.0)
        self.comparison_combo.setCurrentIndex(0)
        
        self.click_type_combo.setCurrentIndex(0)
        
        self.next_steps_list.clear()
        
        self.step_description.setText("")
        
        # 여기까지 초기화
        
        items = self.step_list.selectedItems()
        has_selection = len(items) > 0
        
        # 삭제 버튼 활성화/비활성화
        self.remove_step_btn.setEnabled(has_selection)
        
        if not has_selection:
            return
        
        selectedItem = items[0]
        key = selectedItem.text()
        
        if not self.selectedTask.IsExistStep(key):
            return
        
        step = self.selectedTask.Set_StepKey(key)
        # step = self.selectedTask.Get_Step()
        
        isStartStep = (key == self.selectedTask.Get_StartKey())
        self.start_step_checkbox.setChecked(isStartStep)
        self.start_step_checkbox.setEnabled(not isStartStep)
        
        self.waiting_spin.setValue(step.waiting)
        self.step_name_edit.setText(key)
        
        self.zone_combo.setCurrentText(step.zone)
        self.image_select_combo.setCurrentText(step.image)
        
        num, op, op_text = step.parse_score()
        # print(f"({num}, {op}, {op_text}): {TaskMan.TaskStep.operator_to_desc(op)}")
        self.similarity_spin.setValue(float(num))
        self.comparison_combo.setCurrentText(op_text)
        
        # click_items = ["", "이미지", "영역"]
        click_type = ""
        if "image" == step.finded_click: click_type = "이미지"
        elif "zone" == step.finded_click: click_type = "영역"
        self.click_type_combo.setCurrentText(click_type)
        
        self.fail_step_combo.setCurrentText(step.fail_step)
        for nextstep in step.next_step:
            self.next_steps_list.addItem(nextstep)
        self.selectedTask.UpdateStep_NextSteps(self.next_steps_list)
        self.step_description.setText(step.comment)
        
    def add_automation(self):
        """새 자동화 항목 추가"""
        count = self.automation_list.count()
        new_item_name = f"새 자동화 {count+1}"
        
        # 새 항목 추가
        self.automation_list.addItem(new_item_name)
        
        # 새 항목 선택
        self.automation_list.setCurrentRow(count)
        
        # 즉시 편집 모드로 전환
        self.edit_automation_item(self.automation_list.currentItem(), True)

    def remove_automation(self):
        """선택한 자동화 항목 삭제"""
        current_row = self.automation_list.currentRow()
        if current_row >= 0:
            # 삭제 전 확인 대화상자
            reply = QMessageBox.question(self, '자동화 삭제', 
                                        "선택한 자동화를 삭제하시겠습니까?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.automation_list.takeItem(current_row)
                self.update_automation_buttons_state()

    def edit_automation_item(self, item, isNew):
        """자동화 항목 편집"""
        if item:
            current_text = item.text()
            
            text_title = "자동화 추가" if isNew else "자동화 이름 편집"
            text_conts = "새 이름을 입력하세요:" if isNew else "변경할 이름을 입력하세요"
            
            # 인라인 편집을 위해 텍스트 입력 대화상자 표시
            new_text, ok = QInputDialog.getText(self, text_title,
                                                text_conts, 
                                                QLineEdit.Normal, current_text)
            
            # 사용자가 확인을 누르고 텍스트가 비어있지 않으면 항목 업데이트
            if ok and new_text.strip():
                item.setText(new_text)

    def filter_automation_list(self, text):
        """자동화 목록 필터링"""
        text = text.lower()
        for i in range(self.automation_list.count()):
            item = self.automation_list.item(i)
            if text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def filter_step_list(self, text):
        """단계 목록 필터링"""
        text = text.lower()
        for i in range(self.step_list.count()):
            item = self.step_list.item(i)
            if text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

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
        self.selectedTask.UpdateStep_NextSteps(self.next_steps_list)

    def remove_next_step(self):
        """선택한 다음 단계 삭제"""
        selected_items = self.next_steps_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.next_steps_list.row(item)
                self.next_steps_list.takeItem(row)
            
            # 버튼 상태 업데이트
            self.update_next_step_buttons_state()
        self.selectedTask.UpdateStep_NextSteps(self.next_steps_list)

    def update_next_step_buttons_state(self):
        """다음 단계 항목 선택 상태에 따라 버튼 활성화 상태 업데이트"""
        # 선택된 항목이 있는지 확인
        has_selection = len(self.next_steps_list.selectedItems()) > 0
        
        # 삭제 버튼 활성화/비활성화
        self.remove_next_step_btn.setEnabled(has_selection)

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
            
    # # dataclass는 내부적으로 __eq__()를 제공하므로 객체 비교가 가능
    # def is_task_modified(self): return self.selectedTask != self.originalTask
    # def is_step_modified(self): return self.selectedTaskStep != self.originalTaskStep

    # def OpenPopup_WarningSave(self):
    #     reply = QMessageBox.question(
    #         self,
    #         "변경 내용 확인",
    #         "변경된 내용이 있습니다. 저장하시겠습니까?",
    #         QMessageBox.Yes | QMessageBox.No,
    #         QMessageBox.No
    #     )
    #     # print(reply)
    #     return (True if QMessageBox.Yes == reply else False)
    #     # if reply == QMessageBox.No:
    #         # return
    #     # self.reject()
    
    def save_task(self):
        """작업 저장"""
        # self.accept()
        # self.close()
        
        print("저장하기")
        
    def OnClick_Reload(self):
        # print("리로드")

        self.selectedTask.Reset_Task()
        # print(f"{self.selectedTask.IsSelect()}")
        # # self.selectedTask.Reset_Step()

        self.Reload_Tasks()