from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                              QDoubleSpinBox, QSpacerItem, QSizePolicy, QComboBox)
from PySide6.QtCore import Signal, Slot

try:
    from ui.component.searchable_comboBox import SearchableComboBox
except ImportError:
    SearchableComboBox = QComboBox

import stores.sanner as Scanner
import ui.css as CSS
import zzz.config as CONFIG
import stores.task_manager as TaskMan

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
        
        # 첫 번째 행 - 좌: 캡처 버튼, 우: 자동화/아이템 생성 버튼
        top_row = QHBoxLayout()
        
        # 캡처 시작/중지 버튼 (왼쪽)
        self.capture_btn = QPushButton(self.RUNNER_BUTTON_START_TEXT)
        self.capture_btn.setStyleSheet(CSS.BUTTON_APPLY_BLUESKY)
        self.capture_btn.setFixedWidth(60)
        self.capture_btn.clicked.connect(self.toggle_capture_callback)
        top_row.addWidget(self.capture_btn)

        if not CONFIG.RELEASE_APP:
            # 간격 프레임
            interval_frame = self.create_interval_frame()
            top_row.addWidget(interval_frame)
        
        # 여백 추가 (가운데)
        top_row.addStretch(1)
        
        # 자동화 생성 버튼 (오른쪽)
        self.create_task_btn = QPushButton("자동화")
        self.create_task_btn.setStyleSheet(CSS.BUTTON_APPLY_GREEN)
        self.create_task_btn.clicked.connect(self.openpopup_taskeditor)
        top_row.addWidget(self.create_task_btn)
        
        # 아이템 생성 버튼 (오른쪽 끝)
        self.create_item_btn = QPushButton("아이템")
        self.create_item_btn.setStyleSheet(CSS.BUTTON_ORANGE)
        self.create_item_btn.clicked.connect(self.open_popup_callback)
        top_row.addWidget(self.create_item_btn)
        
        # 첫 번째 행을 메인 레이아웃에 추가
        main_layout.addLayout(top_row)
        
        # 두 번째 행 - 작업 콤보박스와 리로드 버튼
        bottom_row = QHBoxLayout()
        
        # 콤보박스의 최대 너비 설정 (필요시 주석 해제)
        combo_max_width = 508  # 적절한 너비로 조정
        
        # 검색 가능한 콤보박스 추가
        try:
            task_items = [
                "한국노총, 민주당 이재명 대선후보 지지…공동선대위 구성 추진(종합)",
                "각종 유세 지원하고 선거운동원 파견…5월 1일 이 후보와 정책협약",
                "한국노총은 민주당이 이번 대선 지지 정당으로 결정됨에 따라 민주당",
                "이 후보는 정책 협약 체결에 이어 한국노총 노동절 대회에 참석할 예정이다",
            ]
            self.task_combo = SearchableComboBox(items=task_items)
            # self.task_combo.setFixedWidth(480)
            # self.task_combo.addItem("작업 선택...")
        except Exception as e:
            print(f"SearchableComboBox 생성 오류: {e}")
            self.task_combo = QComboBox(self)
            self.task_combo.addItem("작업 선택...")
        
        # 콤보박스 크기 설정 (고정 너비 또는 최소/최대 너비)
        try:
            # self.task_combo.setMinimumWidth(150)
            # self.task_combo.setMaximumWidth(combo_max_width)
            self.task_combo.setFixedWidth(combo_max_width)
            self.task_combo.currentTextChanged.connect(lambda task: self.Change_Task(task))
        except Exception as e:
            print(f"콤보박스 크기 설정 오류: {e}")
        
        bottom_row.addWidget(self.task_combo)
        
        # 리로드 버튼 추가
        try:
            self.reload_btn = QPushButton("🔄 파일 다시 읽기", self)
            self.reload_btn.setToolTip("작업 목록 새로고침")
            self.reload_btn.setFixedWidth(110)
            # self.reload_btn.setFixedSize(30, 30)
            self.reload_btn.clicked.connect(self.reload_tasks)
            bottom_row.addWidget(self.reload_btn)
        except Exception as e:
            print(f"리로드 버튼 생성 오류: {e}")
        
        # 나머지 공간을 여백으로 채움
        bottom_row.addStretch(1)
        
        # 두 번째 행을 메인 레이아웃에 추가
        main_layout.addLayout(bottom_row)
        
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
    
    def Change_Task(self, task):
        # print(f"ControlFrame.Change_Task({task})")
        TaskMan.SetKey_RunningTask(task)
        # pass

    def reload_tasks(self):
        """작업 목록 새로고침"""
        # print("작업 목록 새로고침")

        # pass
        # 콤보박스 내용 업데이트 코드
        TaskMan.Load_Task()
        self.task_combo.clear()
        # self.task_combo.addItem("")

        task_keys = TaskMan.GetAll_Tasks().keys()
        for key in task_keys:
            self.task_combo.addItem(key)
        # print(f"{task_keys}")
    
    def update_capture_button_text(self, is_capturing):
        """캡처 버튼 텍스트 업데이트"""
        text = self.RUNNER_BUTTON_STOP_TEXT if is_capturing else self.RUNNER_BUTTON_START_TEXT
        self.capture_btn.setText(text)

    def on_apply_interval(self):
        """간격 적용 버튼 클릭 처리"""
        value = self.interval_spin.value()
        self.apply_interval_callback(value)