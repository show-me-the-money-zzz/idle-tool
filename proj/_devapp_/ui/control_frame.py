from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                              QDoubleSpinBox, QSpacerItem, QSizePolicy, QComboBox)
from PySide6.QtCore import Signal, Slot

try:
    from ui.component.searchable_comboBox import SearchableComboBox
except ImportError:
    SearchableComboBox = QComboBox

import stores.sanner as Scanner
import ui.css as CSS
import zzz.app_config as APP_CONFIG
import stores.task_manager as TaskMan
import stores.areas as Areas
import stores.noti_store as NotiStores

class ControlFrame(QFrame):
    """캡처 제어 프레임"""
    
    RUNNER_BUTTON_START_TEXT = "일해 ▶️" 
    RUNNER_BUTTON_STOP_TEXT = "정지 🟥"
    
    def __init__(self, parent, status_signal, toggle_capture_callback, 
                 apply_interval_callback,
                 open_popup_callback, openpopup_taskeditor
                 ):
        super().__init__(parent)
        self.parent = parent
        self.status_signal = status_signal
        self.toggle_capture_callback = toggle_capture_callback
        self.apply_interval_callback = apply_interval_callback
        self.open_popup_callback = open_popup_callback
        self.openpopup_taskeditor = openpopup_taskeditor
        
        self.setup_ui()
        self.reload_tasks()
    
    def setup_ui(self):
        """UI 설정"""
        # 메인 레이아웃을 수직으로 변경
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 5)
        main_layout.setSpacing(5)  # 적절한 간격 설정
        
        # 첫 번째 행 - 좌: 자동화/아이템 생성 버튼, 우: 간격 프레임과 캡처 버튼
        top_row = QHBoxLayout()
        
        # 자동화 생성 버튼 (왼쪽)
        self.create_task_btn = QPushButton("자동화")
        self.create_task_btn.setStyleSheet(CSS.BUTTON_APPLY_GREEN)
        self.create_task_btn.clicked.connect(self.openpopup_taskeditor)
        top_row.addWidget(self.create_task_btn)
        
        # 아이템 생성 버튼 (왼쪽 두번째)
        self.create_item_btn = QPushButton("아이템")
        self.create_item_btn.setStyleSheet(CSS.BUTTON_ORANGE)
        self.create_item_btn.clicked.connect(self.open_popup_callback)
        top_row.addWidget(self.create_item_btn)
        
        # 리로드 버튼 추가 (아이템 버튼 우측으로 이동)
        try:
            self.reload_btn = QPushButton("🔄 파일 다시 읽기", self)
            self.reload_btn.setToolTip("작업 목록 새로고침")
            self.reload_btn.setFixedWidth(110)
            self.reload_btn.clicked.connect(self.reload_tasks)
            top_row.addWidget(self.reload_btn)
        except Exception as e:
            print(f"리로드 버튼 생성 오류: {e}")
        
        # 여백 추가 (가운데)
        top_row.addStretch(1)
        
        if not APP_CONFIG.RELEASE_APP:
            # 간격 프레임 (오른쪽)
            interval_frame = self.create_interval_frame()
            top_row.addWidget(interval_frame)
        
        # 캡처 시작/중지 버튼 (오른쪽 끝)
        self.capture_btn = QPushButton(self.RUNNER_BUTTON_START_TEXT)
        self.capture_btn.setStyleSheet(CSS.BUTTON_APPLY_BLUESKY)
        self.capture_btn.setFixedWidth(60)
        self.capture_btn.clicked.connect(self.toggle_capture_callback)
        top_row.addWidget(self.capture_btn)
        
        # 첫 번째 행을 메인 레이아웃에 추가
        main_layout.addLayout(top_row)
        
        # 두 번째 행 - "자동화" 레이블과 작업 콤보박스
        task_row = QHBoxLayout()
        
        # "자동화" 레이블 추가 (고정 너비로 설정)
        task_label = QLabel("자동화:")
        task_label.setFixedWidth(60)  # 레이블 너비 고정
        task_row.addWidget(task_label)
        
        # 작업 콤보박스 추가
        try:
            task_items = [
                "한국노총, 민주당 이재명 대선후보 지지…공동선대위 구성 추진(종합)",
                "각종 유세 지원하고 선거운동원 파견…5월 1일 이 후보와 정책협약",
                "한국노총은 민주당이 이번 대선 지지 정당으로 결정됨에 따라 민주당",
                "이 후보는 정책 협약 체결에 이어 한국노총 노동절 대회에 참석할 예정이다",
            ]
            self.task_combo = SearchableComboBox(items=task_items)
        except Exception as e:
            print(f"SearchableComboBox 생성 오류: {e}")
            self.task_combo = QComboBox(self)
            self.task_combo.addItem("작업 선택...")
        
        # 콤보박스 설정 - 확장하도록 설정
        try:
            # 확장 정책 설정 - 수평으로는 확장, 수직으로는 고정
            self.task_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.task_combo.currentTextChanged.connect(lambda task: self.Change_Task(task))
        except Exception as e:
            print(f"콤보박스 크기 설정 오류: {e}")
        
        task_row.addWidget(self.task_combo)
        
        # 두 번째 행을 메인 레이아웃에 추가
        main_layout.addLayout(task_row)
        
        # 세 번째 행 - "단계" 레이블과 단계 콤보박스
        step_row = QHBoxLayout()
        
        # "단계" 레이블 추가 (고정 너비로 설정 - 자동화 레이블과 동일하게)
        step_label = QLabel("단계:")
        step_label.setFixedWidth(60)  # 레이블 너비 고정
        step_row.addWidget(step_label)
        
        # 단계 콤보박스 추가
        self.step_combo = SearchableComboBox()
        # 확장 정책 설정 - 수평으로는 확장, 수직으로는 고정
        self.step_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.step_combo.currentTextChanged.connect(lambda step: self.Change_Step(step))
        step_row.addWidget(self.step_combo)
        
        # 세 번째 행을 메인 레이아웃에 추가
        main_layout.addLayout(step_row)
        
        # 크기 정책 설정
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def create_interval_frame(self):
        """간격 설정 프레임 생성"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 0, 10, 0)
        
        interval_label = QLabel("간격(초)")
        layout.addWidget(interval_label)
        
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.00, 3.00)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setValue(Scanner.Loop_Interval)
        self.interval_spin.setDecimals(2)   # 소수점 N자리 허용
        self.interval_spin.setFixedWidth(60)
        layout.addWidget(self.interval_spin)
        
        apply_btn = QPushButton("적용")
        apply_btn.clicked.connect(self.on_apply_interval)
        layout.addWidget(apply_btn)
        
        return frame
    
    def Change_Task(self, tasktext):
        # TaskMan.SetKey_RunningTask 호출
        # taskkey = self.task_combo.currentData()
        # print(f"Change_Task({tasktext}): {taskkey}")
        key, _ = TaskMan.Get_Task_byName(tasktext)
        Scanner.SetKey_RunningTask(key)
        
        # 단계 콤보박스 업데이트
        self.update_step_combo(key)

    def update_step_combo(self, task_key):
        """작업에 따라 단계 콤보박스 업데이트하고 시작 단계 구분해서 표시"""
        self.step_combo.clear()
        
        if not task_key:
            return
                
        # 작업에서 단계 가져오기
        task = TaskMan.Get_Task(task_key)
        if not task or not hasattr(task, 'steps'):
            return
        
        # 시작 단계 가져오기
        start_key = task.start_key if hasattr(task, 'start_key') else ""
                
        # 단계 키를 콤보박스에 추가 (시작 단계는 특별한 접두사 추가)
        for key, step in task.steps.items():
            display_text = f"{TaskMan.ICON_START_STEP} {step.name}" if key == start_key else step.name
            self.step_combo.addItem(display_text, key)  # 실제 키를 userData로 저장
        
        # 시작 단계가 설정되어 있으면 해당 단계 선택
        if start_key and start_key in task.steps:
            display_text = f"{TaskMan.ICON_START_STEP} {task.steps.get(start_key).name}"
            index = self.step_combo.findText(display_text)
            if index >= 0:
                self.step_combo.setCurrentIndex(index)
                # 상태 표시 업데이트 (옵션)
                self.status_signal.emit(f"시작 단계: {start_key}")
        elif self.step_combo.count() > 0:
            # 시작 단계가 없거나 유효하지 않으면 첫 번째 단계 선택
            self.step_combo.setCurrentIndex(0)
        # print(f"{self.step_combo.currentData()}")

    def Change_Step(self, display_text):
        # 표시 텍스트에서 실제 키 추출 (⭐ 제거)    #TaskMan.ICON_START_STEP
        step_name = display_text.replace(f"{TaskMan.ICON_START_STEP} ", "") if display_text.startswith(f"{TaskMan.ICON_START_STEP} ") else display_text
        step_key = self.step_combo.currentData()
        # print(f"Change_Step({step_name}, {step_key})")
        Scanner.SetKey_StartStep(step_key)

    def reload_tasks(self):
        """작업 목록 새로고침"""
        Areas.Load_All()

        # 콤보박스 내용 업데이트 코드
        TaskMan.Load_Task()
        self.task_combo.clear()

        tasks = TaskMan.GetAll_Tasks()
        for key, task in tasks.items():
            self.task_combo.addItem(task.name, key)
            
        # 첫 번째 작업 선택 및 단계 업데이트
        if tasks:
            first_key = next(iter(tasks))
            first_task = tasks.get(first_key)
            # print(f"[{first_key}] {first_task}")
            self.task_combo.setCurrentText(first_task.name)
            self.update_step_combo(first_key)
        else:
            self.step_combo.clear()
            
        NotiStores.Load_Notis()
    
    def update_capture_button_text(self, is_capturing):
        """캡처 버튼 텍스트 업데이트"""
        text = self.RUNNER_BUTTON_STOP_TEXT if is_capturing else self.RUNNER_BUTTON_START_TEXT
        self.capture_btn.setText(text)

    def on_apply_interval(self):
        """간격 적용 버튼 클릭 처리"""
        value = self.interval_spin.value()
        self.apply_interval_callback(value)