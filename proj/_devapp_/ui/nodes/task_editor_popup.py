from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QListWidget, QTabWidget, QWidget, QTextEdit,
                             QGroupBox, QFrame, QCheckBox, QScrollArea,
                             QGridLayout, QApplication, QMessageBox,
                             QDoubleSpinBox, QSizePolicy, QInputDialog,
                             QSpinBox, QStackedWidget)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, Signal, QEvent
import sys
import copy
import datetime

import os
# import tempfile
# import webbrowser

from ui.component.searchable_comboBox import SearchableComboBox
from ui.component.draggable_label import DraggableLabel

from stores.task_base_step import BaseStep, TaskStep_Matching, TaskStep_MouseWheel, TaskStep_TeltegramNoti
import stores.task_manager as TaskMan
import stores.areas as Areas
from grinder_types.selected_task import SelectedTask
import ui.css as CSS
from grinder_utils.pysider import ChangeText_ListWidget
import zzz.app_config as APP_CONFIG
# import core.config as CONFIG
import grinder_utils.finder as FINDER
import grinder_utils.system as SYS_UTIL

class TaskEditorPopup(QDialog):
    """작업 편집기 팝업 창"""
    
    # 상태 신호 정의
    task_saved_signal = Signal(dict)
    status_signal = Signal(str)  # 상태 메시지 시그널 추가
    
    def __init__(self, parent, tasker):
        super().__init__(parent)
        self.setWindowTitle("자동화 에디터")
        self.resize(720, 1000)

        # tasker 인스턴스 저장
        self.tasker = tasker
        
        self.selectedTask = SelectedTask(
            origin_key="",
            task=None,
            origin_step_key = "",)
        
        # UI 설정
        self._setup_ui()
        self.Connect_ChangedUI()
        
        self.Reload_Tasks()

        self.tabs.currentChanged.connect(self.on_tab_changed)
    
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
        # self.tabs.addTab(self.tab_preview, "프리뷰")
        # self.tab_preview.setEnabled(False)
        
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
        self.cancel_btn.clicked.connect(self.Close_Editor)
        buttons_layout.addWidget(self.cancel_btn)

        # 오른쪽 버튼들을 위한 공간 추가
        buttons_layout.addStretch(1)

        # 다시 불러오기 버튼 추가 (오른쪽 첫 번째)
        self.reload_btn = QPushButton("리셋")
        self.reload_btn.setStyleSheet(CSS.BUTTON_ORANGE)  # 적절한 스타일 적용
        self.reload_btn.clicked.connect(self.OnClick_Reload)  # 다시 불러오기 기능 연결
        buttons_layout.addWidget(self.reload_btn)

        # 저장 버튼 (오른쪽 끝)
        self.save_btn = QPushButton("저장")
        self.save_btn.setStyleSheet(CSS.BUTTON_APPLY_GREEN)
        self.save_btn.clicked.connect(self.save_task)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
        
    def Connect_ChangedUI(self):
        """UI 컨트롤 변경 이벤트 연결"""
        self.automation_name_edit.textChanged.connect(lambda task_name: self.selectedTask.UpdateTask_Name(task_name))
        self.task_description.textChanged.connect(lambda: self.selectedTask.UpdateTask_Comment(self.task_description.toPlainText()))
        self.start_step_checkbox.stateChanged.connect(self.ProcessCheck_StartSetp)
        
        # 스텝 타입 변경 시 해당 컨트롤 패널 표시
        self.main_type_combo.currentTextChanged.connect(self.OnStepTypeChanged)
        
        self.waiting_spin.valueChanged.connect(lambda waiting: self.selectedTask.UpdateStep_Waiting(waiting))
        self.step_name_edit.textChanged.connect(lambda step_name: self.selectedTask.UpdateStep_Name(step_name))
        
        # 매칭 타입 컨트롤 연결
        self.zone_combo.currentTextChanged.connect(lambda zone: self.selectedTask.UpdateStep_Zone(zone))
        self.image_select_combo.currentTextChanged.connect(lambda image: self.selectedTask.UpdateStep_Image(image))
        self.similarity_spin.valueChanged.connect(lambda similarity: self.selectedTask.UpdateStep_ScoreVal(similarity))
        self.comparison_combo.currentTextChanged.connect(lambda comparison: self.selectedTask.UpdateStep_ScoreDesc(comparison))
        self.click_type_combo.currentTextChanged.connect(lambda click: self.selectedTask.UpdateStep_ClickType(click))
        
        # 마우스휠 타입 컨트롤 연결
        self.mousewheel_amount_spin.valueChanged.connect(lambda amount: self.selectedTask.UpdateStep_MouseWheel_Amount(amount))
        
        # 텔레그램 알림 타입 컨트롤 연결
        self.telegram_dummy_checkbox.stateChanged.connect(lambda state: self.selectedTask.UpdateStep_TelegramNoti_Dummy(state == Qt.Checked))
        
        # 공통 컨트롤 연결
        self.fail_step_combo.currentTextChanged.connect(lambda step: self.selectedTask.UpdateStep_FailStep(step))

        self.step_description.textChanged.connect(lambda: self.selectedTask.UpdateStep_Comment(self.step_description.toPlainText()))
    
    def OnStepTypeChanged(self, type_str):
        """단계 타입 변경 시 해당하는 위젯 표시"""
        # 타입명을 매핑 (UI 표시용 -> 내부 타입 코드)
        type_mapping = {
            "영역-이미지 매칭": "matching",
            "마우스 휠": "mousewheel",
            "텔레그램 알림": "telegramNoti",
        }
        
        internal_type = type_mapping.get(type_str, "matching")
        
        # 선택된 단계가 있을 때만 타입 변경 처리
        if self.selectedTask.IsSelectStep():
            # 실제 타입 변경
            self.selectedTask.UpdateStep_Type(internal_type)
            
            # 타입에 맞는 패널 표시
            self.ShowTypeSpecificPanel(internal_type)
    
    def ShowTypeSpecificPanel(self, type_str):
        """타입에 맞는 패널 표시"""
        # 스택 위젯의 인덱스 매핑
        panel_index = {
            "matching": 0,
            "mousewheel": 1,
            "telegramNoti": 2,
        }
        
        # 해당 패널 표시
        index = panel_index.get(type_str, 0)
        self.step_type_stacked_widget.setCurrentIndex(index)
    
    def ProcessCheck_StartSetp(self, state):
        startkey, step = self.selectedTask.UpdateTask_StartStepKey(state)
        self.start_step_checkbox.setEnabled(False)
        if "" != startkey: self.start_key_input.setText(step.name)
        
    def Reload_Tasks(self):
        # 작업 데이터 초기화
        self.tasks = TaskMan.GetAll_Tasks()
        
        self.initialize_data()
        
    def initialize_data(self):
        """작업 목록 초기화"""
        self.automation_list.clear() # 기존 항목 모두 제거
        self.step_list.clear()  # 단계 리스트 초기화
        
        # 작업 데이터에서 키 가져와서 추가
        for key, data in self.tasks.items():
            self.automation_list.addItem(data.name)
        
        self.waiting_spin.setValue(0.0)
        self.step_name_edit.setText("")
        self.start_step_checkbox.setChecked(False)
        self.start_step_checkbox.setEnabled(False)
        
        # 영역 콤보박스 초기화
        self.zone_combo.clear()
        self.zone_combo.addItem("")
        for keys in Areas.GetAll_ZoneAreas().keys():
            self.zone_combo.addItem(keys)
        
        # 이미지 콤보박스 초기화
        self.image_select_combo.clear()
        self.image_select_combo.addItem("")
        for keys in Areas.GetAll_ImageAreas().keys():
            self.image_select_combo.addItem(keys)
            
        self.similarity_spin.setValue(80.0)
        self.comparison_combo.setCurrentIndex(0)
        self.click_type_combo.setCurrentIndex(0)
        
        # 마우스휠 컨트롤 초기화
        self.mousewheel_amount_spin.setValue(0)
        
        # 텔레그램 알림 컨트롤 초기화
        self.telegram_dummy_checkbox.setChecked(False)
        
        # 공통 컨트롤 초기화
        self.fail_step_combo.clear()
        self.next_step_combo.clear()
        self.step_description.setText("")
    
    # 이벤트 필터 메서드
    def eventFilter(self, obj, event):
        # automation_list에서 Enter 키를 눌렀을 때의 동작 처리
        if obj == self.automation_list and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Enter 키 이벤트를 소비하고 false 반환하여 기본 동작 막기
                return True
    
        # 기본 이벤트 처리로 돌아가기
        return super().eventFilter(obj, event)
    
    def _setup_basic_tab(self):
        """기본 탭 구성"""
        # 전체 레이아웃은 수직으로 배치
        layout = QVBoxLayout(self.tab_basic)
        
        # 상단 - 자동화 목록 그룹 (가로로 배치)
        self.automation_group = QGroupBox("자동화 목록")
        automation_layout = QHBoxLayout(self.automation_group)
        
        # 왼쪽 영역 - 자동화 목록과 버튼들을 수직으로 배치
        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 자동화 목록 - 비어있는 상태로 초기화
        self.automation_list = QListWidget()
        
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
        
        # 자동화 이름 적용 버튼 핸들러 추가
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
        layout.addWidget(self.automation_group, 1)  # 비율 1
        
        # 하단 - 단계 목록 그룹 (왼쪽 패널의 내용을 기본 탭에 포함)
        self.step_group = QGroupBox("단계 목록")
        step_layout = QVBoxLayout(self.step_group)
        
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

        flowchart_folder_btn = QPushButton("폴더 열기")
        flowchart_folder_btn.clicked.connect(self.open_flowchart_folder)
        buttons_layout.addWidget(flowchart_folder_btn)
        
        flowchart_btn = QPushButton("순서도")
        flowchart_btn.setToolTip("단계를 순서도로 웹브라우저 열기")
        flowchart_btn.setFixedWidth(64)
        # flowchart_btn.setEnabled(False)  # 초기에는 비활성화
        flowchart_btn.clicked.connect(self.update_preview_flowchart)
        buttons_layout.addWidget(flowchart_btn)
        
        step_layout.addLayout(buttons_layout)
        
        # 하단 그룹을 레이아웃에 추가 - 비율 증가
        layout.addWidget(self.step_group, 2)  # 비율 2로 증가

    def _setup_preview_tab(self):
        """프리뷰 탭 구성 - 자동화 목록과 흐름도 버튼"""
        layout = QVBoxLayout(self.tab_preview)
        
        # 자동화 목록 그룹
        automation_group = QGroupBox("자동화 목록")
        automation_layout = QVBoxLayout(automation_group)
        
        # 자동화 목록 위젯
        self.preview_automation_list = QListWidget()
        automation_layout.addWidget(self.preview_automation_list)
        
        # 브라우저에서 보기 버튼
        view_button = QPushButton("브라우저에서 흐름도 보기")
        view_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        view_button.clicked.connect(self.update_preview_flowchart)
        automation_layout.addWidget(view_button)
        
        layout.addWidget(automation_group)
        
        # 간단한 설명 추가
        info_label = QLabel("선택한 태스크의 흐름도를 웹 브라우저에서 확인할 수 있습니다.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin-top: 10px;")
        layout.addWidget(info_label)
        
        # 여백 추가
        layout.addStretch(1)

    def sync_automation_lists(self):
        """기본 탭과 프리뷰 탭의 자동화 목록 동기화"""
        selected_text = None
        if self.automation_list.currentItem():
            selected_text = self.automation_list.currentItem().text()
        
        # 프리뷰 탭의 목록 초기화
        self.preview_automation_list.clear()
        
        # 기본 탭의 항목들을 프리뷰 탭에 복사
        for i in range(self.automation_list.count()):
            item_text = self.automation_list.item(i).text()
            self.preview_automation_list.addItem(item_text)
            
            # 같은 항목이 선택되도록 설정
            if item_text == selected_text:
                self.preview_automation_list.setCurrentRow(i)

    def update_preview_flowchart(self):
        """선택된 태스크의 흐름도를 웹 브라우저에서 열기"""
        # items = self.preview_automation_list.selectedItems()
        items = self.automation_list.selectedItems()
        if not items:
            QMessageBox.information(self, "정보", "왼쪽 목록에서 태스크를 선택하세요.")
            return
        
        task_name = items[0].text()
        task_data = self.tasks.get(task_name)
        
        if not task_data:
            QMessageBox.warning(self, "경고", f"태스크 '{task_name}'를 찾을 수 없습니다.")
            return
        
        try:
            # Mermaid 코드 생성
            from grinder_utils.flowchart_generator import FlowchartGenerator
            mermaid_code = FlowchartGenerator.generate_mermaid_code(task_name, task_data)
            html_content = FlowchartGenerator.get_html_template(mermaid_code, task_name, task_data.comment)
            
            path = FINDER.GetPath_Flowchart()
            os.makedirs(path, exist_ok=True)

            current_time = datetime.datetime.now().strftime("%H%M%S")
            temp_file_name = f"{task_name.replace(' ', '_')}_{current_time}.html"
            temp_file_path = os.path.join(path, temp_file_name)
            
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 기본 웹 브라우저로 파일 열기
            import webbrowser
            webbrowser.open(f'file://{temp_file_path}')
            
            # 상태 메시지 표시
            if hasattr(self, 'status_signal'):
                self.status_signal.emit(f"흐름도를 브라우저에서 열었습니다: {task_name}")
        
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "오류", f"흐름도 생성 중 오류가 발생했습니다:\n{str(e)}\n\n{traceback.format_exc()}")
            
    def open_flowchart_folder(self):
        try:
            path = FINDER.GetPath_Flowchart()
            if not os.path.exists(path):
                os.makedirs(path)
            os.startfile(path)  # Windows 전용
        except Exception as e:
            QMessageBox.critical(self, "폴더 열기 실패", f"폴더를 열 수 없습니다: {str(e)}")
            
    def on_tab_changed(self, index):
        """탭이 변경될 때 호출되는 메서드"""
        if index == 1:  # 프리뷰 탭 인덱스
            self.sync_automation_lists()

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
        type_items = ["영역-이미지 매칭", "마우스 휠",
                    #   "텔레그램 알림",
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
        
        # 타입별 컨트롤을 위한 스택 위젯 추가
        self.step_type_stacked_widget = QStackedWidget()
        
        # --- 1. 매칭 타입 위젯 ---
        matching_widget = QWidget()
        matching_layout = QVBoxLayout(matching_widget)
        
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
        
        matching_layout.addLayout(zone_layout)
        
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
        
        matching_layout.addLayout(image_layout)
        
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

        # 결과 표시용 레이블 생성
        self.result_label = DraggableLabel(parent=self)
        self.result_label.hide()  # 초기에는 숨김 상태
        similarity_layout.addWidget(self.result_label)
        
        # "현재 게임에서" 버튼 추가 (오른쪽 정렬)
        self.current_game_btn = QPushButton("현재 게임에서")
        self.current_game_btn.clicked.connect(self.on_current_game_clicked)
        self.current_game_btn.setMaximumWidth(120)  # 폭 제한
        similarity_layout.addWidget(self.current_game_btn)
        
        matching_layout.addLayout(similarity_layout)
        
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
        
        matching_layout.addLayout(click_layout)
        
        # --- 2. 마우스휠 타입 위젯 ---
        mousewheel_widget = QWidget()
        mousewheel_layout = QVBoxLayout(mousewheel_widget)
        
        # 마우스휠 스크롤 양
        amount_layout = QHBoxLayout()
        amount_label = QLabel("스크롤 양:")
        amount_label.setFixedWidth(min_label_width)
        amount_layout.addWidget(amount_label)
        
        self.mousewheel_amount_spin = QSpinBox()
        self.mousewheel_amount_spin.setRange(-1000, 1000)  # 음수는 위로, 양수는 아래로 스크롤
        self.mousewheel_amount_spin.setSingleStep(120)     # 휠 한 단계 단위로 변경 (일반적인 값)
        self.mousewheel_amount_spin.setValue(120)          # 기본값 (아래로 한 단계)
        amount_layout.addWidget(self.mousewheel_amount_spin)
        
        # 설명 레이블 추가
        help_label = QLabel("(양수: 아래로, 음수: 위로 스크롤)")
        help_label.setStyleSheet("color: gray; font-size: 9pt;")
        amount_layout.addWidget(help_label)
        
        # 오른쪽 여백 추가
        amount_layout.addStretch(1)
        
        mousewheel_layout.addLayout(amount_layout)
        
        # 여백 추가 (나머지 공간 채우기)
        mousewheel_layout.addStretch(1)
        
        # --- 3. 텔레그램 알림 타입 위젯 ---
        telegram_widget = QWidget()
        telegram_layout = QVBoxLayout(telegram_widget)
        
        # 더미 체크박스 (실제로는 다른 옵션이 추가될 수 있음)
        dummy_layout = QHBoxLayout()
        self.telegram_dummy_checkbox = QCheckBox("더미 모드 (실제 전송 안함)")
        dummy_layout.addWidget(self.telegram_dummy_checkbox)
        
        # 오른쪽 여백 추가
        dummy_layout.addStretch(1)
        
        telegram_layout.addLayout(dummy_layout)
        
        # 여백 추가 (나머지 공간 채우기)
        telegram_layout.addStretch(1)
        
        # 스택 위젯에 각 타입별 패널 추가
        self.step_type_stacked_widget.addWidget(matching_widget)       # 인덱스 0: 매칭
        self.step_type_stacked_widget.addWidget(mousewheel_widget)     # 인덱스 1: 마우스휠
        self.step_type_stacked_widget.addWidget(telegram_widget)       # 인덱스 2: 텔레그램
        
        # 스택 위젯을 레이아웃에 추가
        layout.addWidget(self.step_type_stacked_widget)
        
        # 가이드 레이블 추가 (최하단)
        guide_layout = QHBoxLayout()
        self.guide_label_step_normalinfo = QLabel("")
        self.guide_label_step_normalinfo.setStyleSheet("color: gray; font-size: 9pt;")  # 작은 회색 텍스트
        guide_layout.addWidget(self.guide_label_step_normalinfo)
        guide_layout.addStretch(1)  # 오른쪽 여백 추가
        self.Update_GuideLabel_StepNormalInfo()
        
        layout.addLayout(guide_layout)
        
        return group
        
    def _create_right_panel(self):
        """오른쪽 패널 - 단계 추가정보"""
        group = QGroupBox("단계 추가정보")
        layout = QVBoxLayout(group)
        
        # 최소 레이블 너비 계산 (가장 긴 레이블에 맞춤)
        min_label_width = 80  # 기본값 - "실패 후 단계:"에 맞게 조정
        
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
        self.next_steps_list.setStyleSheet("background-color: #c2ffc0; color: #000000;")
        self.next_steps_list.setMinimumHeight(100)  # 최소 높이 설정
        
        # 리스트 항목 선택 시 삭제 버튼 활성화를 위한 연결
        self.next_steps_list.itemSelectionChanged.connect(self.update_next_step_buttons_state)
        
        next_steps_list_layout.addWidget(self.next_steps_list)
        
        layout.addLayout(next_steps_list_layout)

        # 실패 후 단계 - 검색 가능한 콤보박스
        fail_step_layout = QHBoxLayout()
        fail_step_label = QLabel("실패 후 단계:")
        fail_step_label.setFixedWidth(min_label_width)
        fail_step_layout.addWidget(fail_step_label)
        
        # 샘플 항목 생성
        # fail_step_items = [ "" ]
        # fail_step_items += [ f"단계{i}" for i in range(1, 31)]
        self.fail_step_combo = SearchableComboBox(items=[ "" ])
        self.fail_step_combo.setStyleSheet("background-color: #ffc0c0; color: #000000;")
        self.fail_step_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fail_step_layout.addWidget(self.fail_step_combo)
        
        layout.addLayout(fail_step_layout)
        
        # 설명 입력 영역
        layout.addWidget(QLabel("설명:"))
        self.step_description = QTextEdit()
        self.step_description.setMinimumHeight(40)  # 최소 높이 설정
        layout.addWidget(self.step_description)
        
        # 참고 레이블 추가 (최하단)
        guide_layout = QHBoxLayout()
        guide_label = QLabel("※실패 후 단계 / 다음 단계는 검색 가능")
        guide_label.setStyleSheet("color: gray; font-size: 9pt;")  # 작은 회색 텍스트
        guide_layout.addWidget(guide_label)
        guide_layout.addStretch(1)  # 오른쪽 여백 추가
        
        layout.addLayout(guide_layout)
        
        return group
    
    def update_automation_buttons_state(self):
        """자동화 항목 선택 상태에 따라 버튼 활성화 상태 업데이트"""
        DEVDEV = False

        if DEVDEV: print("update_automation step= 1")
        self.save_task()
        
        if DEVDEV: print("update_automation step= 3")
        self.selectedTask.Reset_Task()
        
        self.step_list.clear()
        self.start_key_input.setText("")
        self.task_description.setText("")
        self.start_step_checkbox.setChecked(False)
        self.start_step_checkbox.setEnabled(False)
        self.step_name_edit.setText("")
        
        # 모든 타입별 패널 초기화
        self.zone_combo.setCurrentText("")
        self.image_select_combo.setCurrentText("")
        self.similarity_spin.setValue(70.0)
        self.comparison_combo.setCurrentIndex(0)
        self.click_type_combo.setCurrentIndex(0)
        self.mousewheel_amount_spin.setValue(0)
        self.telegram_dummy_checkbox.setChecked(False)
        
        # 공통 컨트롤 초기화
        self.fail_step_combo.clear()
        self.next_step_combo.clear()
        self.step_description.setText("")
        
        # 여기까지 초기화
        
        items = self.automation_list.selectedItems()
        has_selection = len(items) > 0
        self.remove_automation_btn.setEnabled(has_selection)
        
        # 선택된 항목이 있으면 이름 편집 필드에 표시
        if has_selection:
            if DEVDEV: print("update_automation step= 4")
            selectedItem = items[0]
            self.automation_name_edit.setText(selectedItem.text())
            
            name = selectedItem.text()
            key = ""
            for k, data in self.tasks.items():
                if data.name == name:
                    key = k
            task = self.tasks.get(key)
            
            if not task:
                return
            if DEVDEV: print("update_automation step= 5")
            self.selectedTask.Set_Task(key, task)
            if not APP_CONFIG.RELEASE_APP: self.automation_group.setTitle(f"자동화: {key}")
            
            startstep = self.selectedTask.GetStep_Start()
            if startstep: self.start_key_input.setText(startstep.name) #task.start_key
            self.task_description.setText(task.comment)
            
            # 시작 단계 가져오기
            start_key = task.start_key if hasattr(task, 'start_key') else ""
            
            self.fail_step_combo.addItem("")
            self.next_step_combo.addItem("")
            
            # 단계 목록에 추가 (시작 단계는 특별한 접두사 추가)
            for stepkey, step in task.steps.items():
                display_text = f"{TaskMan.ICON_START_STEP} {step.name}" if stepkey == start_key else step.name
                self.step_list.addItem(display_text)
                # 검색 가능한 콤보박스에는 원래 키를 추가
                self.fail_step_combo.addItem(step.name)
                self.next_step_combo.addItem(step.name)
        else:
            # 선택된 항목이 없으면 이름 편집 필드 비우기
            self.automation_name_edit.clear()

    def update_step_buttons_state(self):
        """단계 선택 상태에 따라 버튼 활성화 상태 업데이트"""
        # 선택된 항목이 있는지 확인
        self.selectedTask.Reset_Step()
        
        # 기본 컨트롤 초기화
        self.start_step_checkbox.setChecked(False)
        self.start_step_checkbox.setEnabled(False)
        self.waiting_spin.setValue(0.00)
        self.step_name_edit.setText("")
        
        # 타입별 컨트롤 초기화
        # 매칭 컨트롤
        self.zone_combo.setCurrentText("")
        self.image_select_combo.setCurrentText("")
        self.similarity_spin.setValue(70.0)
        self.comparison_combo.setCurrentIndex(0)
        self.click_type_combo.setCurrentIndex(0)
        
        # 마우스휠 컨트롤
        self.mousewheel_amount_spin.setValue(0)
        
        # 텔레그램 알림 컨트롤
        self.telegram_dummy_checkbox.setChecked(False)
        
        # 공통 컨트롤
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
        name = selectedItem.text()

        # 아이콘 제거하여 실제 키 가져오기
        if name.startswith(f"{TaskMan.ICON_START_STEP} "):
            name = name.replace(f"{TaskMan.ICON_START_STEP} ", "")
        
        stepkey = self.selectedTask.IsExistStep_byName(name)
        if not stepkey:
            return
        
        step = self.selectedTask.Set_StepKey(stepkey)
        if not APP_CONFIG.RELEASE_APP: self.step_group.setTitle(f"단계: {name}")
        
        # 공통 속성 설정
        isStartStep = (stepkey == self.selectedTask.Get_StartKey())
        self.start_step_checkbox.setChecked(isStartStep)
        self.start_step_checkbox.setEnabled(not isStartStep)
        
        self.waiting_spin.setValue(step.waiting)
        self.step_name_edit.setText(name)
        
        # 타입 설정
        type_ui_mapping = {
            "matching": "영역-이미지 매칭",
            "mousewheel": "마우스 휠",
            "telegramNoti": "텔레그램 알림",
        }
        self.main_type_combo.setCurrentText(type_ui_mapping.get(step.type, "영역-이미지 매칭"))
        
        # 타입에 맞는 패널 표시
        self.ShowTypeSpecificPanel(step.type)
        
        # 타입별 속성 설정
        if step.type == "matching" and hasattr(step, "zone"):
            self.zone_combo.setCurrentText(step.zone)
            self.image_select_combo.setCurrentText(step.image)
            
            num, op, op_text = step.parse_score()
            self.similarity_spin.setValue(float(num))
            self.comparison_combo.setCurrentText(op_text)
            
            click_type = ""
            if "image" == step.finded_click: click_type = "이미지"
            elif "zone" == step.finded_click: click_type = "영역"
            self.click_type_combo.setCurrentText(click_type)
            
        elif step.type == "mousewheel" and hasattr(step, "amount"):
            self.mousewheel_amount_spin.setValue(step.amount)
            
        elif step.type == "telegramNoti" and hasattr(step, "dummy"):
            self.telegram_dummy_checkbox.setChecked(step.dummy)
        
        # 공통 속성 설정 - 실패 단계
        self.fail_step_combo.setCurrentText(step.fail_step)
        
        # 다음 단계 설정
        for nextstep in step.next_step:
            self.next_steps_list.addItem(nextstep)
        self.selectedTask.UpdateStep_NextSteps(self.next_steps_list)
        
        # 설명 설정
        self.step_description.setText(step.comment)

        if not APP_CONFIG.RELEASE_APP: 
            self.Update_GuideLabel_StepNormalInfo()
            
    def Update_GuideLabel_StepNormalInfo(self):
        """단계 정보 가이드 레이블 업데이트"""
        step = self.selectedTask.Get_Step()
        
        if not step:
            text = "※영역 / 이미지는 검색 가능"
            self.guide_label_step_normalinfo.setText(text)
            return
            
        # 기본 텍스트
        text = "※영역 / 이미지는 검색 가능"
        
        # 디버그 모드일 경우 추가 정보 표시
        if not APP_CONFIG.RELEASE_APP:
            text += f" (type: {step.type})"
            
            # 타입별 추가 정보
            if step.type == "matching" and hasattr(step, "zone"):
                text += f", score: {step.score}"
            elif step.type == "mousewheel" and hasattr(step, "amount"):
                text += f", amount: {step.amount}"
        
        self.guide_label_step_normalinfo.setText(text)
        
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
                
    def update_next_step_buttons_state(self):
        """다음 단계 항목 선택 상태에 따라 버튼 활성화 상태 업데이트"""
        # 선택된 항목이 있는지 확인
        has_selection = len(self.next_steps_list.selectedItems()) > 0
        
        # 삭제 버튼 활성화/비활성화
        self.remove_next_step_btn.setEnabled(has_selection)
        
    def save_task(self):
        """작업 저장"""
        isSaved = False
        isChanged = False
        if self.selectedTask.IsSelect():            
            taskkey = self.selectedTask.GetKey_Task()
            isChanged = False
            
            if not isChanged:   # 데이터 변경 체크
                orgintask = self.tasks.get(taskkey)
                if orgintask:
                    deeporgintask = copy.deepcopy(orgintask)
                    isChanged = (deeporgintask != self.selectedTask.task)

            if not isChanged:   # 새로운 아이템인지
                findTask = TaskMan.Get_Task(taskkey, None)
                isChanged = not findTask
                    
            if isChanged:
                # X 버튼은 QMessageBox.No 또는 QMessageBox.Cancel 값과 같은 결과 반환
                reply = QMessageBox.question(self, '데이터 수정됨',
                                             "수정된 데이터를 저장하시겠습니까?\n" +
                                             "('No'는 저장된 상태로 돌아갑니다.)",
                                             QMessageBox.Yes | QMessageBox.No,  # 포함 버튼들
                                             QMessageBox.Yes    # 기본 버튼(Enter 키 누를 때 선택되는 버튼)
                                             )
                if QMessageBox.Yes == reply:
                    newtask = TaskMan.Update_Task(taskkey, self.selectedTask.task)
                    if newtask:
                        self.tasks = newtask
                        # print(f"{newtask}")
                        if (orgintask.name != self.selectedTask.task.name):
                            ChangeText_ListWidget(self.automation_list, orgintask.name, self.selectedTask.task.name)
                        isSaved = True
                # elif QMessageBox.No == reply:
                else:
                    isChanged = False
                    QMessageBox.warning(self, "저장 취소", "저장을 취소하였습니다.")
        
        if isSaved:
            QMessageBox.information(self, "저장 성공", "저장에 성공하였습니다.")
        else:
            if isChanged:
                QMessageBox.information(self, "저장 실패", "저장에 실패하였습니다.")
                
    def Close_Editor(self):
        self.save_task()
        self.close()

    def OnClick_Reload(self):
        self.selectedTask.Reset_Task()
        self.Reload_Tasks()
        
    def add_step(self):
        """새 단계 추가"""
        # 현재 항목 수 확인
        count = self.step_list.count()
        
        # 현재 선택된 타입 가져오기
        type_ui_mapping = {
            "영역-이미지 매칭": "matching",
            "마우스 휠": "mousewheel",
            "텔레그램 알림": "telegramNoti",
        }
        current_type = type_ui_mapping.get(self.main_type_combo.currentText(), "matching")
        
        key = SYS_UTIL.GetKey("step")
        # print(key)
        # return
            
        # 새 항목 추가
        name = f"새 단계 {count + 1}"
        self.step_list.addItem(name)
        
        self.selectedTask.NewStep(key, name, current_type)
        
        # 새 항목 선택
        self.step_list.setCurrentRow(count)

    def remove_step(self):
        """선택한 단계 삭제"""
        # 현재 선택된 행 가져오기
        current_row = self.step_list.currentRow()
        
        if current_row < 0:
            return  # 선택된 항목이 없음
            
        stepname = self.step_list.item(current_row).text()
        
        # 아이콘 제거하여 실제 키 가져오기
        if stepname.startswith(f"{TaskMan.ICON_START_STEP} "):
            stepname = stepname.replace(f"{TaskMan.ICON_START_STEP} ", "")
        
        self.selectedTask.RemoveStep_byName(stepname)
        
        # 항목 삭제
        self.step_list.takeItem(current_row)
        
        # 버튼 상태 업데이트
        self.update_step_buttons_state()
            
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
        
    def add_automation(self):
        """새 자동화 항목 추가"""
        count = self.automation_list.count()
        new_item_name = f"새 자동화 {count+1}"

        # 즉시 편집 모드로 전환
        new_text, ok = QInputDialog.getText(self, "자동화 추가",
                                            "새 이름을 입력하세요:",
                                            QLineEdit.Normal, new_item_name)
        if ok and new_text.strip():
            duplication = self.tasks.get(new_text)
            if duplication:
                QMessageBox.critical(self, "중복 KEY",
                                     "키가 중복됩니다. 다른 이름을 사용하세요.")
                return

            key = SYS_UTIL.GetKey("task")
            # print(key)
            # return
            
            self.tasks[key] = TaskMan.Task(
                name=new_text,
                steps={},
                start_key="",
                comment="",
            )

            # 새 항목 추가
            self.automation_list.addItem(new_text)

            # 새 항목 선택
            self.automation_list.setCurrentRow(count)

    def remove_automation(self):
        """선택한 자동화 항목 삭제"""
        current_row = self.automation_list.currentRow()
        if current_row < 0:
            return  # 선택된 항목이 없음
            
        taskkey = self.automation_list.item(current_row).text()

        # 삭제 전 확인 대화상자
        reply = QMessageBox.question(self, '자동화 삭제', 
                                    f"선택한 자동화({taskkey})를 삭제하시겠습니까?\n" +
                                    "파일에 바로 저장합니다.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.selectedTask.RemoveTask(taskkey)
            
            if TaskMan.Delete_Task(taskkey):
                self.tasks = TaskMan.GetAll_Tasks()

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
    
    def on_current_game_clicked(self):
        """현재 게임 화면에서 선택한 zone에서 image를 찾고 결과를 표시합니다."""
        try:
            # 선택된 단계의 타입 확인
            step = self.selectedTask.Get_Step()
            if not step or step.type != "matching":
                QMessageBox.warning(self, "경고", "영역-이미지 매칭 타입에서만 사용 가능합니다.")
                return
                
            # 선택된 zone과 image 가져오기
            zone_key = self.zone_combo.currentText()
            image_key = self.image_select_combo.currentText()
            
            # 유효성 검사
            if not zone_key or not image_key:
                QMessageBox.warning(self, "경고", "존과 이미지를 모두 선택해주세요.")
                return
                
            # match_image_in_zone 호출
            result = self.tasker.match_image_in_zone(zone_key, image_key)
            
            # 현재 시간 가져오기
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            # 리턴값 확인 및 처리
            if result and 'score_percent' in result:
                # 결과 텍스트 생성
                score_percent = result['score_percent']
                result_text = f"유사도 {score_percent:.2f}% ({current_time})"
                
                # 레이블에 결과 표시
                self.result_label.setText(result_text)
                self.result_label.show()
                
                # 추가 정보 표시 (위치 등이 있다면)
                if 'center_x' in result and 'center_y' in result:
                    center_x = result['center_x']
                    center_y = result['center_y']
                    if hasattr(self, 'status_signal'):
                        self.status_signal.emit(f"중심점: X={center_x}, Y={center_y}")
            else:
                # 매칭 실패
                self.result_label.setText(f"{current_time} 매칭 실패")
                self.result_label.show()
                QMessageBox.information(self, "정보", "해당 영역에서 이미지를 찾을 수 없습니다.")
                if hasattr(self, 'status_signal'):
                    self.status_signal.emit("이미지 매칭 실패")
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"이미지 매칭 중 오류 발생: {str(e)}")
            if hasattr(self, 'status_signal'):
                self.status_signal.emit(f"오류: {str(e)}")