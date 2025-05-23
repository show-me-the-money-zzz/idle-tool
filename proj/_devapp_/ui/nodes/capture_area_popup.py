from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
                             QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QGridLayout, QComboBox, QTextEdit, QScrollArea, QApplication,
                             QFrame, QMessageBox, QFileDialog, QListWidget, QInputDialog)
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PIL import Image, ImageQt
from datetime import datetime
import time
import os
from enum import Enum

from core.config import *
import zzz.app_config as APP_CONFIG
import stores.areas as Areas
import grinder_utils.system as SYS_UTIL
from core.window_utils import WindowUtil
from ui.nodes.log_dock_widget import LogDockWidget
from ui.nodes.image_dock_widget import ImageDockWidget
import ui.css as CSS


class CaptureMode(Enum):
    IMAGE = 0
    ZONE = 1
    TEXT = 2
    
class CaptureAreaPopup(QDialog):
    """캡처 영역 설정 팝업 창"""
    
    READTEXT_BUTTON_START_TEXT = "▶️"
    READTEXT_BUTTON_STOP_TEXT = "🟥"
    KindTextList = [ "image", "zone", "text", ] #CaptureMode 순서로

    def __init__(self, parent, region_selector, capture_manager, status_signal, on_close_callback=None):
        super().__init__(parent)
        self.setWindowTitle("아이템 에디터")
        self.resize(900, 720)
        
        self.parent = parent
        self.region_selector = region_selector
        self.capture_manager = capture_manager
        self.status_signal = status_signal
        self.on_close_callback = on_close_callback
        
        self.selectedkey = ""

        self.preview_image = None
        self.preview_pixmap = None
        self.capture_settings = None
        self.reading_text = False
        self.selected_colors = []
        
        self.capturemode = CaptureMode.IMAGE
        
        # 로그 도킹 위젯 생성
        self.log_dock = LogDockWidget(self)
        self.log_dock.setFloating(True)  # 항상 분리된 상태로 설정
        
        # 로그 창 버튼 연결
        self.log_dock.read_text_btn.clicked.connect(self.toggle_read_text)
        self.log_dock.clear_log_btn.clicked.connect(self.clear_log)
        
        self.log_dock.setVisible(False)

         # 이미지 도킹 위젯 생성
        self.image_dock = ImageDockWidget(self)
        self.image_dock.setFloating(True)
        self.image_dock.setVisible(False)
        
        # 타이머 변수 (None으로 초기화)
        self._read_timer = None

        self.selected_color_index = 0   # 현재 선택된 색상 버튼 인덱스

        self._setup_ui()

        self.on_capture_type_changed(CaptureMode.IMAGE)
        self.update_image_viewer()
        
        # 이동 타이머 추가
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_log_dock_position)
        self.move_timer.timeout.connect(self.update_image_dock_position)    # 이미지 도킹 위젯 이동 타이머 연결
        self.move_timer.start(500)  # 0.5초 간격으로 위치 업데이트

    def _setup_ui(self):
        # 메인 레이아웃 - 수직 대신 수평 레이아웃 사용
        main_layout = QHBoxLayout(self)
        
        # 왼쪽 패널 추가 (탭, 리스트, 버튼 포함)
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)
        
        # 오른쪽 패널 (기존 컨트롤들)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # 상단 컨트롤 영역
        top_controls = QHBoxLayout()
        
        # 좌측 설정 영역
        settings_group = QGroupBox("위치 및 크기")
        settings_layout = QVBoxLayout(settings_group)
        
        # 캡처 타입 및 키 입력 영역
        key_layout = QHBoxLayout()
        
        typeitems = [ "이미지", "빈영역", ]
        if APP_CONFIG.USE_OCR:
            typeitems.append("텍스트")
        # 캡처 방식 선택 콤보박스
        self.capture_type_combo = QComboBox()
        self.capture_type_combo.addItems(typeitems)
        # self.capture_type_combo.currentIndexChanged.connect(self.on_capture_type_changed)
        self.capture_type_combo.setEnabled(False)
        key_layout.addWidget(self.capture_type_combo)
        
        # KEY 레이블과 입력
        key_layout.addWidget(QLabel("이름"))
        self.key_input = QLineEdit()
        self.key_input.textChanged.connect(self.update_image_checkbox_state)  # 텍스트 변경 시 체크박스 상태 업데이트
        key_layout.addWidget(self.key_input)
        
        settings_layout.addLayout(key_layout)
        
        # 키워드: 콤보박스 + 버튼 수평 배치
        keywords_layout = QHBoxLayout()

        # 키워드 콤보박스
        self.keywords_combo = QComboBox()
        self.keywords_combo.setFixedWidth(150)  # 폭 줄이기
        keywords_layout.addWidget(self.keywords_combo)

        # "KEY에 입력" 버튼
        self.apply_key_btn = QPushButton("KEY에 입력")
        self.apply_key_btn.clicked.connect(self.apply_keyword_to_key_input)
        self.apply_key_btn.setFixedWidth(90)
        keywords_layout.addWidget(self.apply_key_btn)
        
        if not APP_CONFIG.RELEASE_APP:
            self.DEV_label_key = QLabel("[]")
            self.DEV_label_key.setStyleSheet("color: #ffff00;")
            keywords_layout.addWidget(self.DEV_label_key)

        # 오른쪽 여백 추가 (왼쪽으로 몰기 위해)
        keywords_layout.addStretch(1)

        # 레이아웃 왼쪽 정렬 지정
        settings_layout.addLayout(keywords_layout)
        
        # 좌표 및 크기 입력 영역
        coords_layout = QGridLayout()

        RectSpinBoxWidth = 64
        # X 좌표
        coords_layout.addWidget(QLabel("X 좌표:"), 0, 0)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setFixedWidth(RectSpinBoxWidth)
        self.x_spin.setValue(int(DEFAULT_CAPTURE_X))
        coords_layout.addWidget(self.x_spin, 0, 1)

        # Y 좌표
        coords_layout.addWidget(QLabel("Y 좌표:"), 0, 2)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setFixedWidth(RectSpinBoxWidth)
        self.y_spin.setValue(int(DEFAULT_CAPTURE_Y))
        coords_layout.addWidget(self.y_spin, 0, 3)

        # 너비
        coords_layout.addWidget(QLabel("너비:"), 0, 4)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 9999)
        self.width_spin.setFixedWidth(RectSpinBoxWidth)
        self.width_spin.setValue(int(DEFAULT_CAPTURE_WIDTH))
        coords_layout.addWidget(self.width_spin, 0, 5)

        # 높이
        coords_layout.addWidget(QLabel("높이:"), 0, 6)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 9999)
        self.height_spin.setFixedWidth(RectSpinBoxWidth)
        self.height_spin.setValue(int(DEFAULT_CAPTURE_HEIGHT))
        coords_layout.addWidget(self.height_spin, 0, 7)

        settings_layout.addLayout(coords_layout)

        for spin in (self.x_spin, self.y_spin, self.width_spin, self.height_spin):
            # spin.editingFinished.connect(self.update_area_preview)
            spin.editingFinished.connect(lambda: None)

        # 동작 버튼들 가로 배치
        action_buttons_layout = QHBoxLayout()

        # 영역 선택 버튼
        select_area_btn = QPushButton("영역 선택")
        select_area_btn.clicked.connect(self.select_capture_area)
        action_buttons_layout.addWidget(select_area_btn)

        # 미리보기 업데이트 버튼
        preview_btn = QPushButton("미리보기 업뎃")
        preview_btn.clicked.connect(self.update_area_preview)
        action_buttons_layout.addWidget(preview_btn)

        # # 저장 이미지 보기 체크박스 (이미지 탭에서만 표시)
        # self.show_image_check = QCheckBox("저장 이미지 보기")
        # self.show_image_check.setVisible(False)  # 초기에는 숨김
        # self.show_image_check.stateChanged.connect(self.toggle_image_viewer)
        # action_buttons_layout.addWidget(self.show_image_check)

        # 여백 추가 (오른쪽으로 버튼 밀기)
        action_buttons_layout.addStretch(1)
        
        # 창 내부만 선택 옵션 (우측 끝에 배치)
        self.window_only_check = QCheckBox("창 내부만 선택")
        self.window_only_check.setChecked(True)
        self.window_only_check.setEnabled(False)
        action_buttons_layout.addWidget(self.window_only_check)

        settings_layout.addLayout(action_buttons_layout)

        # 전체 레이아웃에 settings_group 추가
        top_controls.addWidget(settings_group, 1)
        right_layout.addLayout(top_controls)

        # 마우스 클릭 그룹 추가
        mouse_group = QGroupBox("마우스 클릭")
        mouse_layout = QHBoxLayout(mouse_group)

        # "수정" 체크박스
        self.edit_check = QCheckBox("수정")
        self.edit_check.stateChanged.connect(self.update_mouse_controls_state)
        mouse_layout.addWidget(self.edit_check)

        # X 좌표
        mouse_layout.addWidget(QLabel("X"))
        self.click_x_spin = QSpinBox()
        self.click_x_spin.setRange(0, 9999)
        self.click_x_spin.setFixedWidth(64)
        self.click_x_spin.setEnabled(False)  # 초기에는 비활성화
        mouse_layout.addWidget(self.click_x_spin)

        # Y 좌표
        mouse_layout.addWidget(QLabel("Y"))
        self.click_y_spin = QSpinBox()
        self.click_y_spin.setRange(0, 9999)
        self.click_y_spin.setFixedWidth(64)
        self.click_y_spin.setEnabled(False)  # 초기에는 비활성화
        mouse_layout.addWidget(self.click_y_spin)
        
        # "업데이트" 버튼 추가
        self.click_pos_update = QPushButton("적용")
        self.click_pos_update.setEnabled(False)  # 초기에는 비활성화
        self.click_pos_update.clicked.connect(self.update_area_preview)
        mouse_layout.addWidget(self.click_pos_update)

        # "중앙" 버튼 추가
        self.center_btn = QPushButton("중앙")
        self.center_btn.setEnabled(False)  # 초기에는 비활성화
        self.center_btn.clicked.connect(self.set_click_to_center)
        mouse_layout.addWidget(self.center_btn)

        # 여백 추가
        mouse_layout.addStretch(1)

        # 색상 버튼 프레임 (수정 모드일 때만 표시)
        self.mouse_color_frame = QFrame()
        mouse_color_layout = QHBoxLayout(self.mouse_color_frame)
        mouse_color_layout.setContentsMargins(0, 0, 0, 0)
        mouse_color_layout.setSpacing(2)

        # "표시" 체크박스 (색상 버튼 옆에 배치)
        self.show_check = QCheckBox("표시")
        self.show_check.setChecked(True)  # 기본값은 체크 상태
        self.show_check.setEnabled(False)  # 초기에는 비활성화
        mouse_color_layout.addWidget(self.show_check)

        # 색상 버튼 생성 함수
        def create_mouse_color_button(color_hex):
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(f"background-color: {color_hex}; border: 1px solid gray;")
            # 버튼 클릭 이벤트 처리 추가 필요
            return btn

        # 색상 버튼 추가
        self.mouse_color_buttons = []
        mouse_colors = ["#ff0000", "#00ff00", "#ffff00"]
        for color in mouse_colors:
            btn = create_mouse_color_button(color)
            self.mouse_color_buttons.append(btn)
            mouse_color_layout.addWidget(btn)

        # 색상 프레임 추가
        mouse_layout.addWidget(self.mouse_color_frame)
        self.mouse_color_frame.setVisible(False)  # 초기에는 숨김

        # 오른쪽 패널 레이아웃에 마우스 클릭 그룹 추가
        right_layout.addWidget(mouse_group)
        
        # 미리보기 영역
        preview_group = QGroupBox("영역 미리보기")
        preview_layout = QVBoxLayout(preview_group)
        
        # 배경색 선택 영역 추가
        bg_color_layout = QHBoxLayout()
        bg_color_layout.setSpacing(2)

        # 컬러 선택 버튼 레이블
        bg_color_layout.addWidget(QLabel("배경색:"))

        # 색상 버튼 생성 함수
        def create_color_button(color_hex):
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(f"background-color: {color_hex}; border: 1px solid gray;")
            btn.clicked.connect(lambda: self.change_preview_background(color_hex))
            return btn

        # 지정된 색상들로 버튼 추가
        BG_COLORS = [ "#ff00ff", "#0000ff", "#00ff00", "#000000", "#ffffff", "#d3d3d3" ]
        for color in BG_COLORS:
            bg_color_layout.addWidget(create_color_button(color))

        # 오른쪽에 여백 추가
        bg_color_layout.addStretch(1)

        # 레이아웃에 추가
        preview_layout.addLayout(bg_color_layout)
        
        if not APP_CONFIG.RELEASE_APP:
            # 색상 추출 영역
            color_layout = QHBoxLayout()
            
            self.extract_color_btn = QPushButton("색 추출")
            self.extract_color_btn.clicked.connect(self.extract_color)
            color_layout.addWidget(self.extract_color_btn)
            
            # 컬러 스크롤 영역
            color_scroll = QScrollArea()
            color_scroll.setWidgetResizable(True)
            color_scroll.setFixedHeight(30)
            
            self.color_frame = QFrame()
            self.color_frame.setMinimumWidth(200)
            color_frame_layout = QHBoxLayout(self.color_frame)
            color_frame_layout.setContentsMargins(0, 0, 0, 0)
            color_frame_layout.setSpacing(1)
            
            color_scroll.setWidget(self.color_frame)
            color_layout.addWidget(color_scroll)
            
            preview_layout.addLayout(color_layout)
        
        # 미리보기 이미지 영역
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(f"background-color: {BG_COLORS[0]};")
        self.preview_label.setText("영역을 선택하면\n미리보기가 표시됩니다")
        preview_layout.addWidget(self.preview_label)
        
        # 오른쪽 패널 레이아웃에 미리보기 그룹 추가
        right_layout.addWidget(preview_group, 1)  # stretch 1

        # 작업 버튼들 그룹화 및 분리
        work_group = QGroupBox("작업")
        work_layout = QHBoxLayout(work_group)

        # 취소 버튼 - 빨간색 스타일
        cancel_btn = QPushButton("취소하고 닫기")
        cancel_btn.setStyleSheet(CSS.BUTTON_CANCEL)
        cancel_btn.clicked.connect(self.on_close)
        work_layout.addWidget(cancel_btn)
        
        work_layout.addStretch(1)
        
        self.save_value_label = QLabel("너비/높이 수정 시에 사용하지말것(이름, 클릭좌표 용)")
        work_layout.addWidget(self.save_value_label)
        self.save_value_btn = QPushButton("값만 저장")
        self.save_value_btn.clicked.connect(lambda: self.save_as_image(False))
        work_layout.addWidget(self.save_value_btn)
        self.save_value_btn.setEnabled(False)

        # 저장 버튼 - 녹색 스타일
        self.save_btn = QPushButton("저장")        
        self.save_btn.clicked.connect(self.apply_settings)
        work_layout.addWidget(self.save_btn)

        # 오른쪽으로 공간 추가
        # work_layout.addStretch(1)

        right_layout.addWidget(work_group)
        
        # 오른쪽 패널을 메인 레이아웃에 추가
        main_layout.addWidget(right_panel, 1)  # 오른쪽 패널이 더 많은 공간 차지

        # 초기에 컨트롤 비활성화
        self.key_input.setEnabled(False)
        self.x_spin.setEnabled(False)
        self.y_spin.setEnabled(False)
        self.width_spin.setEnabled(False)
        self.height_spin.setEnabled(False)
        self.click_x_spin.setEnabled(False)
        self.click_y_spin.setEnabled(False)
        
        # 저장 버튼 초기에 비활성화
        # for widget in self.findChildren(QPushButton):
        #     if widget.text() == "저장":
        #         widget.setEnabled(False)
        #         break
        self.EnableButton_Save(False)
        
        self._setup_ui_additions()

        if not APP_CONFIG.RELEASE_APP:
            # 테스트용 색상 추가
            self.test_add_colors()

    def _create_left_panel(self):
        """왼쪽 패널 생성 - 탭, 리스트, 버튼 포함"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 탭 위젯 생성
        self.left_tabs = QTabWidget()
        
        # 이미지 탭
        image_tab = self._create_list_tab("이미지", CaptureMode.IMAGE)
        self.left_tabs.addTab(image_tab, "이미지")
        
        # 빈영역 탭
        zone_tab = self._create_list_tab("빈영역", CaptureMode.ZONE)
        self.left_tabs.addTab(zone_tab, "빈영역")
        
        # 텍스트 탭
        if APP_CONFIG.USE_OCR:
            text_tab = self._create_list_tab("텍스트", CaptureMode.TEXT)
            self.left_tabs.addTab(text_tab, "텍스트")
        
        # 탭 변경 이벤트 연결
        self.left_tabs.currentChanged.connect(self._on_tab_changed)
        
        left_layout.addWidget(self.left_tabs)
        
        # 왼쪽 패널 크기 설정
        # left_panel.setMinimumWidth(200)
        # left_panel.setMaximumWidth(300)
        left_panel.setFixedWidth(360)
        
        return left_panel

    def _create_list_tab(self, title, mode):
        """목록 탭 생성 (검색창, 리스트, 버튼 포함)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 검색 영역
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("검색:"))
        
        search_edit = QLineEdit()
        search_edit.setPlaceholderText(f"{title} 검색...")
        search_layout.addWidget(search_edit)
        
        layout.addLayout(search_layout)
        
        # 목록 위젯
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(list_widget)
        
        # 버튼 영역
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("✚")
        add_btn.setToolTip(f"{title} 추가")
        add_btn.setFixedWidth(30)
        buttons_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("━")
        remove_btn.setToolTip(f"선택한 {title} 삭제")
        remove_btn.setFixedWidth(30)
        remove_btn.setEnabled(False)  # 초기에는 비활성화
        buttons_layout.addWidget(remove_btn)
        
        # 여백 추가
        buttons_layout.addStretch(1)
        
        layout.addLayout(buttons_layout)
        
        # 각 요소 저장 및 이벤트 연결
        setattr(self, f"{mode.name.lower()}_search", search_edit)
        setattr(self, f"{mode.name.lower()}_list", list_widget)
        setattr(self, f"{mode.name.lower()}_add_btn", add_btn)
        setattr(self, f"{mode.name.lower()}_remove_btn", remove_btn)
        
        # 이벤트 연결
        search_edit.textChanged.connect(lambda text, w=list_widget, m=mode: self._filter_list(text, w, m))
        
        # 아이템 선택 변경 이벤트 수정
        # 여기서 itemSelectionChanged 대신 currentItemChanged를 사용
        list_widget.currentItemChanged.connect(lambda current, previous, w=list_widget, rm=remove_btn, m=mode: 
                                            self._update_selection_current(current, previous, w, rm, m))
        
        add_btn.clicked.connect(lambda _, m=mode: self._add_new_item(m))
        remove_btn.clicked.connect(lambda _, w=list_widget, m=mode: self._remove_selected_item(w, m))
        
        # 초기 데이터 로드
        self._load_list_data(list_widget, mode)
        
        return tab
    
    def _update_selection_current(self, current_item, previous_item, list_widget, remove_btn, mode):
        """현재 선택된 아이템이 변경되었을 때 호출되는 함수"""
        # 선택 여부 확인
        has_selection = current_item is not None
        remove_btn.setEnabled(has_selection)
        
        # 컨트롤 활성화/비활성화 상태 업데이트
        self.key_input.setEnabled(has_selection)
        self.x_spin.setEnabled(has_selection)
        self.y_spin.setEnabled(has_selection)
        self.width_spin.setEnabled(has_selection)
        self.height_spin.setEnabled(has_selection)
        self.click_x_spin.setEnabled(has_selection and self.edit_check.isChecked())
        self.click_y_spin.setEnabled(has_selection and self.edit_check.isChecked())
        
        # 저장 버튼 활성화/비활성화
        self.EnableButton_Save(has_selection)
        
        if has_selection:
            # 현재 선택된 아이템 정보 로드
            selected_name = current_item.text()
            self._load_item_data(selected_name, mode)
        else:
            self.selectedkey = ""            
            self.DEV_Update_KeyLabel()
            
            # 선택된 항목이 없을 때 필드 초기화
            self.Set_Name("")
            self.x_spin.setValue(0)
            self.y_spin.setValue(0)
            self.width_spin.setValue(0)
            self.height_spin.setValue(0)
            self.click_x_spin.setValue(0)
            self.click_y_spin.setValue(0)
            self.edit_check.setChecked(False)
            
            # 미리보기 초기화
            self.preview_label.clear()
            self.preview_label.setText("영역을 선택하면\n미리보기가 표시됩니다")
            
    def _setup_ui_additions(self):
        # 색상 버튼 이벤트 연결
        for i, btn in enumerate(self.mouse_color_buttons):
            btn.clicked.connect(lambda checked=False, idx=i: self.select_mouse_color(idx))
        
        # 기본적으로 첫 번째 색상 버튼 선택
        self.select_mouse_color(0)
        
        # # 수동 좌표 변경 시 미리보기 업데이트
        # self.click_x_spin.valueChanged.connect(self.update_area_preview)
        # self.click_y_spin.valueChanged.connect(self.update_area_preview)
        
        # 체크박스 상태 변경 시 미리보기 업데이트
        self.edit_check.stateChanged.connect(self.update_area_preview)
        self.show_check.stateChanged.connect(self.update_area_preview)

    def Set_Name(self, name):
        if "" == name: self.key_input.clear()
        else: self.key_input.setText(name)

        if self.image_dock.isVisible(): self.update_image_viewer()

    def _on_tab_changed(self, index):
        """탭이 변경되었을 때 호출"""
        # 이전 탭의 모든 선택 해제
        prev_mode = self.capturemode
        if prev_mode != CaptureMode(index):  # 다른 탭으로 변경된 경우만
            prev_list_widget = getattr(self, f"{prev_mode.name.lower()}_list")
            prev_list_widget.clearSelection()  # 이전 탭의 선택 해제
            
            # # 필드 초기화 - clearSelection()으로 인해 _update_selection이 호출되고
            # # 거기서 필드 초기화하므로 여기서 중복 코드 제거
            # self.Set_Name("")
            # ...
            
            # # 미리보기 초기화
            # self.preview_label.clear()
            # self.preview_label.setText("영역을 선택하면\n미리보기가 표시됩니다")
            
            # self._update_selection_current
        
        # 새 탭 처리
        mode = CaptureMode(index)
        self.capture_type_combo.setCurrentIndex(index)
        
        # 이미지 체크박스 상태 업데이트
        if mode == CaptureMode.IMAGE:
            # 이미지 모드로 변경 시 업데이트
            self.update_image_viewer()
        else:
            # 이미지 모드가 아닐 때
            self.image_dock.setVisible(False)
        self.save_value_btn.setVisible(mode == CaptureMode.IMAGE)
        self.save_value_label.setVisible(mode == CaptureMode.IMAGE)
            
        if CaptureMode.TEXT != mode:
            self.reading_text = False
            self.log_dock.setVisible(False)
        
        self.on_capture_type_changed(mode)

    def _load_list_data(self, list_widget, mode):
        """목록 데이터 로드"""
        list_widget.clear()
        
        try:
            items = []
            if mode == CaptureMode.IMAGE:
                # 이미지 데이터 로드
                for item in Areas.GetAll_ImageAreas().values():
                    items.append(item.name)
            elif mode == CaptureMode.ZONE:
                # 빈영역 데이터 로드
                for item in Areas.GetAll_ZoneAreas().values():
                    items.append(item.name)
            elif mode == CaptureMode.TEXT:
                # 텍스트 데이터 로드
                for item in Areas.GetAll_TextAreas().values():
                    items.append(item.name)
            # else: items = []
                
            # 리스트에 항목 추가
            # for key in sorted(items):
            for key in items:
                list_widget.addItem(key)
                
        except Exception as e:
            print(f"데이터 로드 중 오류: {e}")

    def _filter_list(self, text, list_widget, mode):
        """목록 필터링"""
        text = text.lower()
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def _update_selection(self, list_widget, remove_btn, mode):
        """목록 선택 업데이트"""
        has_selection = len(list_widget.selectedItems()) > 0
        remove_btn.setEnabled(has_selection)
        
        # 컨트롤 활성화/비활성화 상태 업데이트
        self.key_input.setEnabled(False)
        self.x_spin.setEnabled(has_selection)
        self.y_spin.setEnabled(has_selection)
        self.width_spin.setEnabled(has_selection)
        self.height_spin.setEnabled(has_selection)
        self.click_x_spin.setEnabled(has_selection and self.edit_check.isChecked())
        self.click_y_spin.setEnabled(has_selection and self.edit_check.isChecked())
        
        # 저장 버튼 활성화/비활성화
        for widget in self.findChildren(QPushButton):
            if widget.text() == "저장":
                widget.setEnabled(has_selection)
                break
        
        if has_selection:
            selected_name = list_widget.selectedItems()[0].text()
            self._load_item_data(selected_name, mode)
        else:
            # 선택된 항목이 없을 때 필드 초기화
            self.Set_Name("")
            self.x_spin.setValue(0)
            self.y_spin.setValue(0)
            self.width_spin.setValue(0)
            self.height_spin.setValue(0)
            self.click_x_spin.setValue(0)
            self.click_y_spin.setValue(0)
            self.edit_check.setChecked(False)
            
            # 미리보기 초기화
            self.preview_label.clear()
            self.preview_label.setText("영역을 선택하면\n미리보기가 표시됩니다")

    def update_image_dock_position(self):
        """이미지 도킹 위젯 위치 업데이트"""
        if not hasattr(self, 'image_dock') or self.image_dock is None or not self.image_dock.isVisible():
            return
    
        if self.image_dock.isVisible():
            if self.image_dock.isFloating():
                main_geo = self.geometry()
                
                # 새 위치 계산
                space_x = 10
                new_x = 0
                # if "right" == self.image_dock.Get_FloatingPos():
                #     new_x = main_geo.x() + main_geo.width() + space_x
                # elif "left" == self.image_dock.Get_FloatingPos():
                #     new_x = main_geo.x() - self.image_dock.width() - space_x
                new_x = main_geo.x() + main_geo.width() + space_x
                new_y = main_geo.y()
                
                # 위젯 크기 설정
                dock_width = 400
                dock_height = main_geo.height()
                
                # 위치 및 크기 설정
                self.image_dock.setGeometry(new_x, new_y, dock_width, dock_height)

    # 체크박스 상태 업데이트 함수 추가
    def update_image_checkbox_state(self):
        """이미지 체크박스 상태 업데이트"""
        # if self.capturemode == CaptureMode.IMAGE:
        #     # 이미지 모드일 때 항상 체크박스 표시 및 활성화
        #     self.show_image_check.setVisible(True)
        #     self.show_image_check.setEnabled(True)
            
        #     # 체크박스가 체크되어 있으면 도킹 위젯 표시
        #     if self.show_image_check.isChecked():
        #         self.update_image_viewer()
        # else:
        #     # 이미지 모드가 아닐 때
        #     self.show_image_check.setVisible(False)
        #     self.image_dock.setVisible(False)
        pass

    def update_image_viewer(self):
        """이미지 뷰어 업데이트"""
        # print(f"update_image_viewer(): {self.capturemode.name}")

        # if self.capturemode == CaptureMode.IMAGE:
        ## 창 표시 중일 때만 호출할거

        if self.selectedkey:
            image_data = Areas.Get_ImageArea(self.selectedkey)
            if image_data and hasattr(image_data, 'file') and image_data.file:
                # 로컬 경로로 변환
                from grinder_utils import finder
                local_path = finder.Get_LocalPth()
                file_path = os.path.join(local_path, image_data.file)
                
                # 이미지 로드
                if os.path.exists(file_path):
                    self.image_dock.setVisible(True)
                    self.image_dock.load_image(file_path)
                    self.update_image_dock_position()
                    return
            
            # 이미지 파일이 없는 경우
            self.image_dock.image_label.setText("저장된 파일 없음")
            self.image_dock.path_label.setText("파일 경로: 없음")
        else:
            # 키가 없는 경우
            self.image_dock.image_label.setText("선택된 항목 없음")
            self.image_dock.path_label.setText("파일 경로: 없음")
        
        # 도킹 위젯 표시
        self.image_dock.setVisible(True)
        self.update_image_dock_position()

    def toggle_image_viewer(self, state):
        """이미지 뷰어 토글"""
        if state == Qt.Checked:
            # 체크됐을 때 이미지 뷰어 표시
            self.update_image_viewer()
        else:
            # 체크 해제됐을 때 숨김
            self.image_dock.setVisible(False)

    def _load_item_data(self, name, mode):
        """선택된 항목 데이터 로드"""
        try:
            key = ""
            data = None
            
            if mode == CaptureMode.IMAGE:
                key, data = Areas.Get_ImageArea_byName(name)
                
                self.EnableButton_SaveValue("" != data.file)
                
                # 이미지 체크박스 상태 업데이트
                self.update_image_checkbox_state()
            else:
                # 이미지 모드가 아니면 체크박스 숨김
                self.image_dock.setVisible(False)
                
            if CaptureMode.TEXT != mode:
                self.reading_text = False
                self.log_dock.setVisible(False)
                
            if mode == CaptureMode.ZONE:
                key, data = Areas.Get_ZoneArea_byName(name)
            elif mode == CaptureMode.TEXT:
                key, data = Areas.Get_TextArea_byName(name)
            
            if data:
                self.selectedkey = key
                self.DEV_Update_KeyLabel()
                
                # 키 입력 필드 업데이트
                self.Set_Name(data.name)
                
                # 좌표 및 크기 업데이트
                self.x_spin.setValue(data.x)
                self.y_spin.setValue(data.y)
                self.width_spin.setValue(data.width)
                self.height_spin.setValue(data.height)
                
                self.click_x_spin.setValue(data.clickx)
                self.click_y_spin.setValue(data.clicky)
                
                # 클릭 설정이 있으면 수정 모드 활성화
                has_click = data.clickx > 0 or data.clicky > 0
                self.edit_check.setChecked(has_click)
                
                # 미리보기 업데이트
                self.update_area_preview()
            
        except Exception as e:
            print(f"항목 데이터 로드 중 오류: {e}")

    def _on_item_double_clicked(self, item, mode):
        """항목 더블 클릭 처리"""
        name = item.text()
        self._load_item_data(name, mode)

    def _add_new_item(self, mode):
        """새 항목 추가"""
        # 현재 선택된 모드에 맞는 리스트 위젯 가져오기
        list_widget = getattr(self, f"{mode.name.lower()}_list")
        
        # 현재 항목 수 기반으로 기본 이름 생성
        count = list_widget.count()
        type_name = self.left_tabs.tabText(mode.value)
        default_name = f"새 {type_name} {count + 1}"

        new_text, ok = QInputDialog.getText(self, f"{type_name} 추가",
                                            "이름을 입력하세요:",
                                            QLineEdit.Normal, default_name)
        
        # print(SYS_UTIL.GetKey(CaptureAreaPopup.KindTextList[mode.value]))
        
        if ok and new_text.strip():
            # 키 중복 체크
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if new_text == item.text():
                    QMessageBox.critical(self, "중복 이름",
                                        "이름이 중복됩니다. 다른 이름을 사용하세요.")
                    return
                
            
            key = SYS_UTIL.GetKey(CaptureAreaPopup.KindTextList[mode.value])
            name = new_text

            # 캡처 타입 콤보박스 업데이트
            self.capture_type_combo.setCurrentIndex(mode.value)
            
            # 기본 데이터 준비
            default_data = {
                "name": name,
                "x": 10,
                "y": 10,
                "width": 100,
                "height": 100,
                "clickx": 0,
                "clicky": 0
            }
            
            # 모드에 따라 Areas에 데이터 추가
            if mode == CaptureMode.IMAGE:
                default_data["file"] = ""  # 파일 경로는 비어 있음
                Areas.Add_ImageArea(key, default_data, False)
            elif mode == CaptureMode.ZONE:
                Areas.Add_ZoneArea(key, default_data, False)
            elif mode == CaptureMode.TEXT:
                Areas.Add_TextArea(key, default_data, False)
            
            # 새 항목 추가
            list_widget.addItem(name)
            
            # 새 항목을 선택
            for i in range(list_widget.count()):
                if list_widget.item(i).text() == name:
                    list_widget.setCurrentRow(i)
                    break
                
            self.selectedkey = key
            self.DEV_Update_KeyLabel()
            
            # 컨트롤 활성화 및 기본값 설정
            self.key_input.setEnabled(True)
            self.x_spin.setEnabled(True)
            self.y_spin.setEnabled(True)
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
            
            self.Set_Name(name)
            self.x_spin.setValue(default_data["x"])
            self.y_spin.setValue(default_data["y"])
            self.width_spin.setValue(default_data["width"])
            self.height_spin.setValue(default_data["height"])
            self.click_x_spin.setValue(default_data["clickx"])
            self.click_y_spin.setValue(default_data["clicky"])
            self.edit_check.setChecked(False)
            
            # 저장 버튼 활성화
            self.EnableButton_Save(True)
            
            # 미리보기 초기화
            self.preview_label.clear()
            self.preview_label.setText("영역을 선택하면\n미리보기가 표시됩니다")

    def _remove_selected_item(self, list_widget, mode):
        """선택한 항목 삭제"""
        selected_items = list_widget.selectedItems()
        if not selected_items or not self.selectedkey:
            return
            
        name = selected_items[0].text()
        
        # 삭제 전 확인 대화상자
        reply = QMessageBox.question(
            self, 
            '항목 삭제', 
            f"'{name}' 항목을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 데이터 저장소에서 삭제
                if mode == CaptureMode.IMAGE:
                    saved_filepath = Areas.Get_ImageArea(self.selectedkey).file
                    # print(saved_filepath)
                    
                    Areas.Delete_ImageArea(self.selectedkey)
                    
                    if saved_filepath and os.path.exists(saved_filepath):
                        os.remove(saved_filepath)
        
                elif mode == CaptureMode.ZONE:
                    Areas.Delete_ZoneArea(self.selectedkey)
                elif mode == CaptureMode.TEXT:
                    Areas.Delete_TextArea(self.selectedkey)
                
                # 상태 메시지 업데이트
                self.status_signal.emit(f"'{name}' 항목이 삭제되었습니다.")
                    
                # UI에서 삭제
                row = list_widget.row(selected_items[0])
                list_widget.takeItem(row)
                
                # 필드 초기화
                # self.Set_Name("")
                
            except Exception as e:
                QMessageBox.critical(self, "삭제 오류", f"항목 삭제 중 오류가 발생했습니다: {str(e)}")
        
    def select_mouse_color(self, index):
        """마우스 색상 선택"""
        # 모든 버튼의 테두리 초기화
        for btn in self.mouse_color_buttons:
            btn.setStyleSheet(btn.styleSheet().replace("border: 3px solid black;", "border: 1px solid gray;"))
        
        # 선택된 버튼 테두리 강조
        if 0 <= index < len(self.mouse_color_buttons):
            selected_btn = self.mouse_color_buttons[index]
            style = selected_btn.styleSheet()
            style = style.replace("border: 1px solid gray;", "border: 3px solid black;")
            selected_btn.setStyleSheet(style)
            
            # 현재 선택된 색상 인덱스 저장
            self.selected_color_index = index
            
            # 미리보기 업데이트 (원 색상 반영)
            self.update_area_preview()

    def test_add_colors(self):
        """테스트용 색상 추가"""
        self.add_color("red")
        self.add_color("#00ff00")
        self.add_color("#0000ff")
        self.add_color("#000000")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("#00ff00")
        self.add_color("#0000ff")
        self.add_color("#000000")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("#00ff00")
        self.add_color("#0000ff")
        self.add_color("#000000")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("#00ff00")
        self.add_color("#0000ff")
        self.add_color("#000000")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("#00ff00")
        self.add_color("#0000ff")
        self.add_color("#000000")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("#00ff00")
        self.add_color("#0000ff")
        self.add_color("#000000")
        self.add_color("#ffffff")
        self.add_color("red")
        self.add_color("#00ff00")
        self.add_color("#0000ff")
        self.add_color("#000000")
        self.add_color("#ffffff")
        # colors = ["red", "green", "blue", "#ff00ff", "#ffffff"]
        # for _ in range(5):  # 5번 반복
        #     for color in colors:
        #         self.add_color(color)

    def add_color(self, color):
        """컬러 버튼 추가"""
        color_btn = QPushButton()
        color_btn.setFixedSize(20, 20)
        color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid gray;")
        self.color_frame.layout().addWidget(color_btn)

    def extract_color(self):
        """색상 추출"""
        if not self.preview_image:
            QMessageBox.information(self, "알림", "먼저 영역을 선택하고 미리보기를 업데이트해주세요.")
            return
        
        # 색상 선택 팝업 생성 (PySide6 버전)
        # 임포트 경로는 프로젝트 구조에 맞게 조정
        from ui.nodes.color_picker_popup import ColorPickerPopup
        
        # 색상 선택 결과 처리 콜백
        def handle_color_selection(selected_colors, processed_image):
            if selected_colors:
                # 선택된 색상들 처리
                for color_hex in selected_colors:
                    self.add_color(color_hex)
                
                # 상태 업데이트
                self.status_signal.emit(f"색상이 선택되었습니다: {len(selected_colors)}개")
        
        # PySide6 ColorPickerPopup 인스턴스 생성 및 표시
        picker = ColorPickerPopup(self, self.preview_image, callback=handle_color_selection)
        picker.exec()  # 모달 다이얼로그로 표시 (이전 .mainloop() 대신)
        
    def change_preview_background(self, color_hex):
        # print(f"change_preview_background({color_hex})")
        self.preview_label.setStyleSheet(f"background-color: {color_hex};")
        if hasattr(self, 'preview_pixmap') and self.preview_pixmap:
            self.preview_label.setPixmap(self.preview_pixmap)
        
    # 캡처 타입 변경 핸들러 함수 추가
    def on_capture_type_changed(self, index):
        # print(f"on_capture_type_changed({index})")
        """캡처 타입이 변경되었을 때 호출되는 함수"""
        mode = CaptureMode(index)
        
        keyword_list = []  # zone은 키워드 없음
        
        # 선택된 캡처 타입에 따라 UI 요소 조정
        if mode == CaptureMode.IMAGE:
            self.key_input.setPlaceholderText("이미지 키 입력...")
            self.status_signal.emit("이미지 모드로 변경되었습니다.")
            keyword_list = LOOP_IMAGE_KEYWORD
        elif mode == CaptureMode.ZONE:
            self.key_input.setPlaceholderText("빈영역 키 입력...")
            self.status_signal.emit("빈영역 모드로 변경되었습니다.")
        elif mode == CaptureMode.TEXT:
            self.key_input.setPlaceholderText("텍스트 키 입력...")
            self.status_signal.emit("텍스트 모드로 변경되었습니다.")
            keyword_list = LOOP_TEXT_KEYWORD
            
        # keyword 콤보박스 업데이트
        self.keywords_combo.clear()
        self.keywords_combo.addItems(keyword_list)
        
        isExistKeywordList = 0 < len(keyword_list)
        self.keywords_combo.setEnabled(isExistKeywordList)
        self.apply_key_btn.setEnabled(isExistKeywordList)
            
        if self.reading_text: self.toggle_read_text()
        if CaptureMode.TEXT == mode:
            self.log_dock.setVisible(True)
            # 적절한 위치로 도킹 위젯 이동
            self.update_log_dock_position()
        elif CaptureMode.IMAGE == mode:
            self.image_dock.setVisible(True)
            self.update_image_dock_position()
        else:
            self.log_dock.setVisible(False)
            self.image_dock.setVisible(False)
        
        # 객체에 현재 캡처 타입 저장
        self.capturemode = mode
        
    def update_log_dock_position(self):
        """로그 도킹 위젯 위치 업데이트"""
        if not hasattr(self, 'log_dock') or self.log_dock is None or not self.log_dock.isVisible():
            return
    
        SpaceX = 10
        if self.log_dock.isVisible():
            # 위젯이 도킹되었는지 분리되었는지 확인
            if self.log_dock.isFloating():
                # 메인 창의 오른쪽에 위치시킴
                main_geo = self.geometry()
                
                # 새 위치 계산
                new_x = 0
                # if "right" == self.log_dock.Get_FloatingPos():
                #     new_x = main_geo.x() + main_geo.width() + SpaceX
                # elif "left" == self.log_dock.Get_FloatingPos():
                #     new_x = main_geo.x() - self.log_dock.width() - SpaceX
                new_x = main_geo.x() - self.log_dock.width() - SpaceX
                new_y = main_geo.y()
                
                # 위젯 크기 설정 (필요한 경우)
                dock_width = 400  # 적절한 너비
                dock_height = main_geo.height()  # 메인 창과 동일한 높이
                
                # 위치 및 크기 설정
                self.log_dock.setGeometry(new_x, new_y, dock_width, dock_height)
            # 도킹된 상태에서는 위치 설정이 필요 없음 (자동으로 관리됨)

    # 체크박스 상태에 따라 컨트롤 상태 업데이트하는 메서드 추가
    def update_mouse_controls_state(self):
        # 수정 체크박스 상태 확인
        is_checked = self.edit_check.isChecked()
        has_selection = len(getattr(self, f"{self.capturemode.name.lower()}_list").selectedItems()) > 0
        
        # 스핀박스 활성화/비활성화 - 아이템이 선택된 상태에서만 활성화
        self.click_x_spin.setEnabled(is_checked and has_selection)
        self.click_y_spin.setEnabled(is_checked and has_selection)
        self.click_pos_update.setEnabled(is_checked and has_selection)
        self.center_btn.setEnabled(is_checked and has_selection)
        self.show_check.setEnabled(is_checked and has_selection)
        
        # 색상 프레임 표시/숨김
        self.mouse_color_frame.setVisible(is_checked)
        
        if is_checked and has_selection:
            x = self.click_x_spin.value()
            y = self.click_y_spin.value()
            if 0 == x and 0 == y:
                self.set_click_to_center()

    def set_click_to_center(self):
        """클릭 위치를 영역의 중앙으로 설정"""
        if not self.edit_check.isChecked():
            return
            
        # 영역 너비와 높이 가져오기
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        # 중앙 좌표 계산
        center_x = width // 2
        center_y = height // 2
        
        # 클릭 좌표 설정
        self.click_x_spin.setValue(center_x)
        self.click_y_spin.setValue(center_y)
        
        self.update_area_preview()
            
    def moveEvent(self, event):
        """창 이동 시 로그 창도 함께 이동"""
        super().moveEvent(event)
        
        self.update_log_dock_position()
        self.update_image_dock_position()

    def clear_log(self):
        """로그 내용 초기화"""
        self.log_dock.clear_log()

    def toggle_read_text(self):
        """텍스트 읽기 시작/중지"""
        self.reading_text = not self.reading_text
        
        # 기존 타이머 중지
        if self._read_timer is not None:
            self._read_timer.stop()
            self._read_timer = None
        
        if self.reading_text:
            self.log_dock.read_text_btn.setText(self.READTEXT_BUTTON_STOP_TEXT)
            self._read_loop_main()
        else:
            self.log_dock.read_text_btn.setText(self.READTEXT_BUTTON_START_TEXT)

    def _read_loop_main(self):
        """텍스트 읽기 반복 함수"""
        # 창이 닫혔거나 읽기 상태가 아니면 종료
        if not self.isVisible() or not self.reading_text:
            return
        
        # 텍스트 읽기 실행
        self.read_text_from_area()
        
        # 타이머 설정 (간격은 로그 창에서 가져옴)
        interval = 1000  # 기본값
        try:
            if hasattr(self, 'log_dock') and self.log_dock:
                interval = int(self.log_dock.interval_spin.value() * 1000)
        except:
            pass
        
        # 새 타이머 생성 (이전 타이머는 이미 중지됨)
        self._read_timer = QTimer(self)
        self._read_timer.setSingleShot(True)
        self._read_timer.timeout.connect(self._read_loop_main)
        self._read_timer.start(interval)

    def read_text_from_area(self):
        """지정된 영역에서 텍스트 읽기"""
        try:
            if not WindowUtil.is_window_valid():
                return
                
            x, y = self.x_spin.value(), self.y_spin.value()
            width, height = self.width_spin.value(), self.height_spin.value()
            
            if width <= 0 or height <= 0:
                return
                
            full_window_img = self.capture_manager.capture_full_window()
            if not full_window_img:
                return
                
            img_width, img_height = full_window_img.size
            crop_region = (
                max(0, x), 
                max(0, y), 
                min(img_width, x + width), 
                min(img_height, y + height)
            )
            
            cropped_img = full_window_img.crop(crop_region)
            
            from core.ocr_engine import image_to_text
            recognized_text = image_to_text(cropped_img)
            
            if not recognized_text or recognized_text.strip() == "":
                recognized_text = "(인식된 텍스트 없음)\n"
                
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_dock.append_log(f"[{timestamp}] {recognized_text}")
    
            self.status_signal.emit("영역에서 텍스트 읽기 완료")
            
        except Exception as e:
            print(f"텍스트 인식 오류: {e}")

    def select_capture_area(self):
        """드래그로 캡처 영역 선택"""
        # 창이 연결되어 있고 '창 내부만 선택' 옵션이 활성화된 경우에만 창 내부로 제한
        target_window_only = self.window_only_check.isChecked() and WindowUtil.is_window_valid()
        
        if target_window_only and not WindowUtil.is_window_valid():
            QMessageBox.critical(self, "오류", "창 내부 선택을 위해서는 먼저 창에 연결해주세요.")
            return
        
        # 선택 임시 중단을 알림
        self.status_signal.emit("영역 선택 중... (ESC 키를 누르면 취소)")
        
        # 현재 창 숨기기 (선택 화면이 가려지지 않도록)
        self.setVisible(False)
        
        # 직접 콜백 함수 사용
        def handle_selection_complete(region_info):
            # 다시 창 표시 (취소 여부와 관계없이 항상 실행)
            self.setVisible(True)
            self.activateWindow()  # 창 활성화
            
            # 취소된 경우
            if not region_info:
                self.status_signal.emit("영역 선택이 취소되었습니다.")
                return
            
            # 선택된 영역 정보를 UI에 업데이트
            rel_x1, rel_y1, rel_x2, rel_y2 = region_info["rel"]
            width = region_info["width"]
            height = region_info["height"]
            
            self.x_spin.setValue(rel_x1)
            self.y_spin.setValue(rel_y1)
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            
            self.status_signal.emit(f"영역이 선택되었습니다: X={rel_x1}, Y={rel_y1}, 너비={width}, 높이={height}")
            
            # 선택 후 미리보기 업데이트
            # self.update_area_preview()
            # 기다렸다가 미리보기 업데이트
            QTimer.singleShot(150, self.update_area_preview)
        
        # 영역 선택 시작 (콜백 전달)
        self.region_selector.start_selection(
            callback=handle_selection_complete,
            target_window_only=target_window_only
        )

    def handle_region_selection(self, region_info):
        """영역 선택 결과 처리"""
        if not region_info:
            self.status_signal.emit("영역 선택이 취소되었습니다.")
            return
        
        # 선택된 영역 정보를 UI에 업데이트
        rel_x1, rel_y1, rel_x2, rel_y2 = region_info["rel"]
        width = region_info["width"]
        height = region_info["height"]
        
        self.x_spin.setValue(rel_x1)
        self.y_spin.setValue(rel_y1)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        
        self.status_signal.emit(f"영역이 선택되었습니다: X={rel_x1}, Y={rel_y1}, 너비={width}, 높이={height}")
        
        # 선택 후 미리보기 업데이트
        self.update_area_preview()

    def update_area_preview(self):
        """캡처 영역 미리보기 업데이트"""
        try:
            # 창이 연결되어 있는지 확인
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return
            
            # 캡처 영역 좌표 가져오기
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value()
            
            if width <= 0 or height <= 0:
                QMessageBox.critical(self, "입력 오류", "너비와 높이는 양수여야 합니다.")
                return
            
            # 전체 창 캡처
            full_window_img = self.capture_manager.capture_full_window()
            if not full_window_img:
                QMessageBox.critical(self, "오류", "창 캡처에 실패했습니다.")
                return
            
            # 캡처 영역 추출
            try:
                # PIL 이미지에서 영역 추출
                img_width, img_height = full_window_img.size
                
                # 영역이 이미지 범위를 벗어나는지 확인
                if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
                    QMessageBox.warning(self, "영역 경고", "설정한 영역이 창 범위를 벗어납니다. 일부만 표시됩니다.")
                
                # full_window_img.save("full_window_img.png", format="PNG") #DEV
                
                # 영역 자르기
                cropped_img = full_window_img.crop((
                    max(0, x),
                    max(0, y),
                    min(img_width, x + width),
                    min(img_height, y + height)
                ))
                # cropped_img.save("cropped_img.png", format="PNG") #DEV
                
                # 캔버스에 맞게 이미지 크기 조정 (비율 유지하면서 최대한 크게)
                img_width, img_height = cropped_img.size

                # 미리보기 레이블 크기
                preview_width = self.preview_label.width()
                preview_height = self.preview_label.height()

                # 비율 계산 - 이미지가 영역을 벗어나지 않으면서 최대한 크게 표시
                width_ratio = preview_width / img_width
                height_ratio = preview_height / img_height

                # 이미지가 영역 안에 들어가도록 더 작은 비율 선택
                scale_ratio = min(width_ratio, height_ratio)

                # 이미지 크기 조정
                new_width = int(img_width * scale_ratio)
                new_height = int(img_height * scale_ratio)
                resized_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)
                # resized_img.save("resized_img.png", format="PNG") #DEV

                # PIL 이미지를 QImage로 변환
                self.preview_image = resized_img
                q_image = ImageQt.ImageQt(resized_img)
                
                # QPixmap으로 변환하여 그리기 가능하게 함
                pixmap = QPixmap.fromImage(q_image)
                
                # 원 그리기 여부 확인
                should_draw_circle = self.edit_check.isChecked() and self.show_check.isChecked()
                
                if should_draw_circle:
                    # QPainter 생성
                    painter = QPainter(pixmap)
                    
                    # 클릭 좌표 설정
                    click_x = self.click_x_spin.value()
                    click_y = self.click_y_spin.value()
                    
                    # 좌표를 미리보기 이미지 스케일에 맞게 조정
                    scaled_x = int(click_x * scale_ratio)
                    scaled_y = int(click_y * scale_ratio)
                    
                    # 원 크기 설정 (픽셀)
                    circle_radius = 10
                    
                    # 현재 선택된 색상 버튼 가져오기
                    if hasattr(self, 'selected_color_index') and 0 <= self.selected_color_index < len(self.mouse_color_buttons):
                        color_btn = self.mouse_color_buttons[self.selected_color_index]
                    else:
                        color_btn = self.mouse_color_buttons[0]  # 기본값은 첫 번째 색상
                    
                    # 스타일시트에서 색상 코드 추출
                    import re
                    color_str = color_btn.styleSheet()
                    color_match = re.search(r'background-color:\s*([^;]+)', color_str)
                    
                    if color_match:
                        color_hex = color_match.group(1).strip()
                        # QColor로 변환
                        color = QColor(color_hex)
                    else:
                        # 기본 색상 (빨간색)
                        color = QColor(255, 0, 0)
                    
                    # 반투명 원 그리기 설정
                    color.setAlpha(200)  # 투명도 설정 (0-255)
                    painter.setPen(Qt.NoPen)  # 테두리 없음
                    painter.setBrush(color)
                    
                    # 원 그리기
                    painter.drawEllipse(scaled_x - circle_radius//2, scaled_y - circle_radius//2, 
                                    circle_radius, circle_radius)
                    
                    # 페인터 종료
                    painter.end()
                
                # 이미지 저장
                self.preview_pixmap = pixmap

                # 레이블에 이미지 표시 (중앙 정렬)
                self.preview_label.setPixmap(self.preview_pixmap)
                self.preview_label.setAlignment(Qt.AlignCenter)
                
                self.status_signal.emit("영역 미리보기가 업데이트되었습니다.")
                
            except Exception as e:
                QMessageBox.critical(self, "미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            QMessageBox.critical(self, "미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()

    def apply_settings(self):
        """설정 적용 및 저장"""
        if CaptureMode.IMAGE == self.capturemode:
            self.save_as_image()
        elif CaptureMode.ZONE == self.capturemode:
            self.save_as_zone()
        elif CaptureMode.TEXT == self.capturemode:
            self.save_as_text()

        # 현재 탭의 목록 새로고침
        current_mode = CaptureMode(self.left_tabs.currentIndex())
        list_widget = getattr(self, f"{current_mode.name.lower()}_list")
        self._load_list_data(list_widget, current_mode)

    def save_as_text(self):
        """텍스트 영역으로 저장"""
        try:
            # 설정값 검증
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, clickx, clicky, interval = capture_info
            
            if not self.selectedkey:
                QMessageBox.critical(self, "에러", "선택된 키가 없어요")
                return
            
            name = self.key_input.text()
            if not name:
                QMessageBox.critical(self, "오류", "이름을 입력하세요.")
                return
 
            Areas.Add_TextArea(self.selectedkey, {"name": name,
                                     "x": x, "y": y, "width": width, "height": height,
                                     "clickx": clickx, "clicky": clicky,
                                     })
                
            # 설정 저장
            self.capture_settings = capture_info
            
            # 성공 메시지 표시
            self.status_signal.emit("텍스트가 저장되었습니다.")
            
            QMessageBox.information(self, "알림", f"[{name}] 텍스트 데이터가 저장되었습니다.")
            
            # # 창 닫기
            # self.on_close()
            
        except Exception as e:
            QMessageBox.critical(self, "설정 오류", f"설정을 적용하는 중 오류가 발생했습니다: {str(e)}")

    def save_as_image(self, isSaveFile = True):
        """이미지로 저장"""
        try:
            # 캡처 영역 좌표 가져오기
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, clickx, clicky, _ = capture_info
            
            # 창이 유효한지 확인
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", "창이 연결되지 않았습니다.")
                return
            
            stored_path = ""
            file_path = ""
                
            # 저장할 기본 파일명 생성
            name = self.key_input.text().strip()
            if not name:
                QMessageBox.critical(self, "오류", "이름을 입력하세요.")
                return
            
            if isSaveFile:
                # 전체 창 캡처
                full_window_img = self.capture_manager.capture_full_window()
                if not full_window_img:
                    QMessageBox.critical(self, "오류", "창 캡처에 실패했습니다.")
                    return
            
                # 지정된 영역 추출
                img_width, img_height = full_window_img.size
                crop_region = (
                    max(0, x),
                    max(0, y),
                    min(img_width, x + width),
                    min(img_height, y + height)
                )
                
                cropped_img = full_window_img.crop(crop_region)
                
                if not self.selectedkey:
                    QMessageBox.critical(self, "에러", "선택된 키가 없어요")
                    return
                
                # 기본 파일명
                default_filename = name
                
                # 기본 저장 경로 가져오기
                from grinder_utils import finder
                default_dir = finder.Get_DataPath()
                
                # 파일 저장 다이얼로그 표시
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "이미지 저장",
                    os.path.join(default_dir, default_filename),
                    "PNG 이미지 (*.png);;JPEG 이미지 (*.jpg);;모든 파일 (*.*)"
                )
                
                # 사용자가 취소를 눌렀으면 종료
                if not file_path:
                    return
                
                # 이미지 저장
                cropped_img.save(file_path)
                
                # 상대 경로로 변환
                from pathlib import Path
                local_path = Path(finder.Get_LocalPth())
                file_path_obj = Path(file_path)
                
                try:
                    # 상대 경로 생성 시도
                    local_path = Path(finder.Get_LocalPth())
                    relative_path = file_path_obj.relative_to(local_path)
                    stored_path = str(relative_path)
                except ValueError:
                    # 상대 경로 생성 실패 시 전체 경로 사용
                    stored_path = file_path
            else:
                stored_path = Areas.Get_ImageArea(self.selectedkey).file
            
            # 이미지 정보를 JSON에 저장
            Areas.Add_ImageArea(self.selectedkey, {"name": name,
                "x": x, "y": y, 
                "width": width, "height": height,
                "file": stored_path,
                "clickx": clickx, "clicky": clicky,
            })
            
            # # 체크 상태이면 새로 저장된 이미지 표시
            # if self.show_image_check.isChecked():
            #     # 이미지 도킹 위젯 업데이트
            #     self.update_image_viewer()
            self.update_image_viewer()
            
            self.status_signal.emit(f"이미지가 저장되었습니다: {file_path}")
            
            QMessageBox.information(self, "알림", f"[{name}] 이미지 데이터가 저장되었습니다.")
            
            # # 창 닫기
            # self.on_close()
            
        except Exception as e:
            QMessageBox.critical(self, "이미지 저장 오류", f"이미지 저장 중 오류가 발생했습니다: {str(e)}")

    def save_as_zone(self):
        """빈 영역으로 저장"""
        try:
            # 설정값 검증
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, clickx, clicky, _ = capture_info
            
            if not self.selectedkey:
                QMessageBox.critical(self, "에러", "선택된 키가 없어요")
                return
            
            name = self.key_input.text()
            if not name:
                QMessageBox.critical(self, "오류", "KEY를 입력하세요.")
                return
 
            Areas.Add_ZoneArea(self.selectedkey, {"name": name,
                                     "x": x, "y": y, "width": width, "height": height,
                                     "clickx": clickx, "clicky": clicky,
                                     })
                
            # 설정 저장
            self.capture_settings = capture_info
            
            # 성공 메시지 표시
            self.status_signal.emit("빈영역이 저장되었습니다.")
            
            QMessageBox.information(self, "알림", f"[{name}] 빈영역 데이터가 저장되었습니다.")
            
            # # 창 닫기
            # self.on_close()
            
        except Exception as e:
            QMessageBox.critical(self, "설정 오류", f"설정을 적용하는 중 오류가 발생했습니다: {str(e)}")

    def get_capture_info(self):
        """캡처 정보 가져오기"""
        try:
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value()
            interval = float(self.log_dock.interval_spin.value())
            
            clickx = self.click_x_spin.value()
            clicky = self.click_y_spin.value()
            
            if width <= 0 or height <= 0 or interval <= 0:
                raise ValueError("너비, 높이, 간격은 양수여야 합니다.")
                
            return (x, y, width, height, clickx, clicky
                    , interval
                    )
        except ValueError as e:
            QMessageBox.critical(self, "입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            return None

    # def set_capture_info(self, x, y, width, height, interval):
    #     """캡처 정보 설정"""
    #     self.x_spin.setValue(x)
    #     self.y_spin.setValue(y)
    #     self.width_spin.setValue(width)
    #     self.height_spin.setValue(height)
        
    #     # 미리보기 업데이트
    #     self.update_area_preview()
        
    def apply_keyword_to_key_input(self):
        keyword = self.keywords_combo.currentText()        
        self.Set_Name(keyword)
        
    def closeEvent(self, event):
        # print("[DEBUG] closeEvent triggered from X 버튼")
        self.on_close()
        event.accept()
    
    def on_close(self):
        """창 닫기"""
        # print("CaptureAreaPopup closing...")
        
        # 읽기 상태 중지
        self.reading_text = False
        
        # 모든 타이머 중지
        if hasattr(self, '_read_timer') and self._read_timer is not None:
            self._read_timer.stop()
            self._read_timer = None
        
        if hasattr(self, 'move_timer') and self.move_timer is not None:
            self.move_timer.stop()
            self.move_timer = None

        # # 이미지 도킹 위젯 닫기
        # if hasattr(self, 'image_dock') and self.image_dock is not None:
        #     self.image_dock.close()
            
        try:
            self.log_dock.close()
            # print("로그 도킹 위젯 닫기")
            self.image_dock.close()
        except Exception as e:
            print(f"로그 도킹 위젯 닫기 실패: {e}")
        
        # 콜백 호출
        if self.on_close_callback:
            self.on_close_callback(self.capture_settings)
        
        # print("CaptureAreaPopup 종료 완료")
        self.reject()

    def EnableButton_Save(self, ennable):
        css = CSS.BUTTON_APPLY_GREEN if ennable else CSS.BUTTON_DISABLE
        self.save_btn.setStyleSheet(css)
        self.save_btn.setEnabled(ennable)
    def EnableButton_SaveValue(self, ennable):
        css = CSS.BUTTON_APPLY_BLUESKY if ennable else CSS.BUTTON_DISABLE
        self.save_value_btn.setStyleSheet(css)
        self.save_value_btn.setEnabled(ennable)
            
    def DEV_Update_KeyLabel(self):
        if APP_CONFIG.RELEASE_APP: return
        self.DEV_label_key.setText(f"[{self.selectedkey}]")