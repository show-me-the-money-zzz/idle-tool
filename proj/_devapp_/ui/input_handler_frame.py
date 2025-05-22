from PySide6.QtWidgets import (QGroupBox, QLabel, QLineEdit, QPushButton, 
                            QSpinBox, QGridLayout, QHBoxLayout, QMessageBox, QWidget)
from PySide6.QtCore import Qt, Signal, Slot
import pyautogui

from core.config import *
from core.window_utils import WindowUtil
from ui.component.searchable_comboBox import SearchableComboBox
from zzz.hotkey import HOTKEYs

class InputHandlerFrame(QGroupBox):
    """입력 처리 프레임 (이전의 자동화 영역)"""
    
    def __init__(self, parent, status_signal):
        super().__init__("입력 처리", parent)
        
        self.status_signal = status_signal
        
        self._setup_ui()
        
        ### DEV TEST
        self.DEVTest_Setup()

    def DEVTest_Setup(self):
        import zzz.app_config as APP_CONFIG
        if "RF 온라인 넥스트" == APP_CONFIG.DEFAULT_APP_NAME:
            self.click_x_spin.setValue(1480)
            self.click_y_spin.setValue(60)
        elif "LORDNINE" == APP_CONFIG.DEFAULT_APP_NAME:
            self.click_x_spin.setValue(1473)
            self.click_y_spin.setValue(70)
        elif "Ymir" == APP_CONFIG.DEFAULT_APP_NAME:
            self.click_x_spin.setValue(1486)
            self.click_y_spin.setValue(64)
        elif "Lust Goddess" == APP_CONFIG.DEFAULT_APP_NAME:
            self.click_x_spin.setValue(1016)
            self.click_y_spin.setValue(774)
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # 메인 레이아웃
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 키 입력 관련 프레임
        key_frame = QWidget(self)
        key_layout = QHBoxLayout(key_frame)
        key_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(key_frame, 0, 0, 1, 3)

        # 키 입력 필드 (SearchableComboBox로 변경)
        key_layout.addWidget(QLabel("입력 키:"))
        
        # HOTKEYs 딕셔너리에서 값 목록을 가져옴
        # hotkey_kyes = [ "", ] + list(HOTKEYs.keys())
        hotkey_kyes = [""] + [f"{key} ({value})" for key, value in HOTKEYs.items()]
        # 기본값으로 "m" 설정
        default_key = hotkey_kyes[0]
        
        # SearchableComboBox 생성
        self.input_key_edit = SearchableComboBox(items=hotkey_kyes)
        self.input_key_edit.setEditable(True)  # 직접 입력 가능하도록 설정
        self.input_key_edit.setEditText(default_key)  # 기본값 설정
        self.input_key_edit.setMinimumWidth(120)  # 너비 설정
        self.input_key_edit.setToolTip("단축키를 선택하거나 직접 입력하세요")
        key_layout.addWidget(self.input_key_edit)
        key_layout.addSpacing(10)

        # 키 입력 버튼
        self.key_btn = QPushButton("키보드 입력")
        self.key_btn.clicked.connect(self.press_key)
        key_layout.addWidget(self.key_btn)

        # # ESC 키 입력 버튼
        # self.esc_btn = QPushButton("ESC 키 입력")
        # self.esc_btn.clicked.connect(self.press_esc_key)
        # key_layout.addWidget(self.esc_btn)

        key_layout.addStretch(1)  # 우측 여백

        # 클릭 관련 프레임 (한 행에 모든 요소 배치)
        click_frame = QWidget(self)
        click_layout = QHBoxLayout(click_frame)
        click_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(click_frame, 1, 0, 1, 3)

        # "클릭:" 라벨 추가
        click_layout.addWidget(QLabel("마우스 클릭:"))

        # X 스핀박스 추가
        self.click_x_spin = QSpinBox(self)
        self.click_x_spin.setRange(0, 99999)
        self.click_x_spin.setValue(int(DEFAULT_CLICK_X))
        self.click_x_spin.setMinimumWidth(80)
        click_layout.addWidget(self.click_x_spin)

        # Y 스핀박스 추가
        self.click_y_spin = QSpinBox(self)
        self.click_y_spin.setRange(0, 99999)
        self.click_y_spin.setValue(int(DEFAULT_CLICK_Y))
        self.click_y_spin.setMinimumWidth(80)
        click_layout.addWidget(self.click_y_spin)

        # 마우스 클릭 버튼
        self.click_btn = QPushButton("왼쪽 버튼")
        self.click_btn.clicked.connect(self.mouse_click)
        # click_layout.addWidget(self.click_btn)

        clickclick_btn = QPushButton("클릭")
        clickclick_btn.clicked.connect(lambda: self.mouse_click2(1))
        click_layout.addWidget(clickclick_btn)
        clickclick_btn = QPushButton("pyautogui")
        clickclick_btn.clicked.connect(lambda: self.mouse_click2(2))
        click_layout.addWidget(clickclick_btn)
        # clickclick_btn = QPushButton("postmessage")
        # clickclick_btn.clicked.connect(lambda: self.mouse_click2(3))
        # click_layout.addWidget(clickclick_btn)
        # clickclick_btn = QPushButton("sendmessage")
        # clickclick_btn.clicked.connect(lambda: self.mouse_click2(4))
        # click_layout.addWidget(clickclick_btn)
        # clickclick_btn = QPushButton("uia")
        # clickclick_btn.clicked.connect(lambda: self.mouse_click2(5))
        # click_layout.addWidget(clickclick_btn)
        # clickclick_btn = QPushButton("interception")
        # clickclick_btn.clicked.connect(lambda: self.mouse_click2(6))
        # click_layout.addWidget(clickclick_btn)
        # clickclick_btn = QPushButton("win32")
        # clickclick_btn.clicked.connect(lambda: self.mouse_click2(7))
        # click_layout.addWidget(clickclick_btn)
        # clickclick_btn = QPushButton("pynput")
        # clickclick_btn.clicked.connect(lambda: self.mouse_click2(8))
        # click_layout.addWidget(clickclick_btn)

        # 현재 위치 복사 버튼
        copy_pos_btn = QPushButton("현재 위치 복사")
        copy_pos_btn.clicked.connect(self.copy_current_mouse_position)
        # click_layout.addWidget(copy_pos_btn)

        click_layout.addStretch(1)  # 우측 여백
        
        # 휠 스크롤 관련 프레임 (한 행에 모든 요소 배치)
        scroll_frame = QWidget(self)
        scroll_layout = QHBoxLayout(scroll_frame)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_frame, 2, 0, 1, 3)
        
        # "마우스 휠 스크롤" 라벨 추가
        scroll_layout.addWidget(QLabel("마우스 휠:"))
        
        # 스크롤 양 스핀박스 추가
        self.scroll_amount_spin = QSpinBox(self)
        self.scroll_amount_spin.setRange(-30, 30)  # 스크롤 단위 (양수만)
        self.scroll_amount_spin.setSingleStep(3)
        self.scroll_amount_spin.setValue(0)
        self.scroll_amount_spin.setMinimumWidth(48)
        self.scroll_amount_spin.setToolTip("스크롤 단위 (1-50)")
        scroll_layout.addWidget(self.scroll_amount_spin)
        
        # 위로 스크롤 버튼
        self.scroll_up_btn = QPushButton("스크롤")
        self.scroll_up_btn.clicked.connect(self.mouse_scroll)
        scroll_layout.addWidget(self.scroll_up_btn)

        help_label_scroll = QLabel("(양수: 위로 / 음수: 아래로 스크롤)")
        help_label_scroll.setStyleSheet("color: gray; font-size: 9pt;")
        scroll_layout.addWidget(help_label_scroll)
        
        # # 아래로 스크롤 버튼
        # self.scroll_down_btn = QPushButton("스크롤 ▼")
        # self.scroll_down_btn.clicked.connect(self.mouse_scroll_down)
        # scroll_layout.addWidget(self.scroll_down_btn)
        
        scroll_layout.addStretch(1)  # 우측 여백

        # 마우스 위치 표시 레이블을 우측 정렬로 배치
        self.mouse_pos_label = QLabel("마우스 위치: 절대(X=0, Y=0) / 상대(X=0, Y=0)")
        main_layout.addWidget(self.mouse_pos_label, 3, 0, 1, 3, Qt.AlignRight)
    
    @Slot()
    def press_key(self):
        """사용자가 지정한 키 입력"""
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return
            
            # 사용자가 입력/선택한 키 가져오기
            key = self.input_key_edit.currentText()
            if not key:
                QMessageBox.information(self, "알림", "입력할 키를 지정해주세요.")
                return
            
            input_key = key
            if 1 < len(key) and '(' in key and ')' in key:
                # print(f"hotkey= {key}")
                sp = key.split(' (')[0] #공백
                # print(f"*{sp}*")
                if sp in HOTKEYs.keys():
                    input_key = HOTKEYs[sp]
                    # print(f"{HOTKEYs[sp]} vs {input_key}")
            # print(f"({key}): {input_key}")
            # print(f"{HOTKEYs.items()}")
            
            # 키 입력
            if WindowUtil.send_key(input_key):
                self.status_signal.emit(f"'{input_key}' 키가 입력되었습니다.")
            else:
                QMessageBox.critical(self, "오류", "키 입력에 실패했습니다.")
                
        except Exception as e:
            QMessageBox.critical(self, "키 입력 오류", f"키 입력 중 오류가 발생했습니다: {str(e)}")

    @Slot()
    def press_esc_key(self):
        """ESC 키 입력"""
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return
            
            # ESC 키 입력
            if WindowUtil.send_key('esc'):
                self.status_signal.emit("'ESC' 키가 입력되었습니다.")
            else:
                QMessageBox.critical(self, "오류", "ESC 키 입력에 실패했습니다.")
                
        except Exception as e:
            QMessageBox.critical(self, "키 입력 오류", f"ESC 키 입력 중 오류가 발생했습니다: {str(e)}")

    @Slot()
    def mouse_click(self):
        """마우스 클릭"""
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return
            
            # 클릭 좌표 계산
            rel_x = self.click_x_spin.value()
            rel_y = self.click_y_spin.value()
            
            if rel_x > 0 and rel_y > 0:
                # 상태 표시 업데이트
                self.status_signal.emit(f"클릭 중... (X={rel_x}, Y={rel_y})")
                
                # 상대 좌표 위치 클릭
                if WindowUtil.click_at_position(rel_x, rel_y):
                    self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                else:
                    QMessageBox.critical(self, "오류", "클릭 작업에 실패했습니다.")
            else:
                QMessageBox.information(self, "알림", "클릭할 좌표를 설정해주세요.")
                
        except Exception as e:
            QMessageBox.critical(self, "마우스 클릭 오류", f"마우스 클릭 중 오류가 발생했습니다: {str(e)}")

    @Slot()
    def mouse_click2(self, index):
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return
            
            # 클릭 좌표 계산
            rel_x = self.click_x_spin.value()
            rel_y = self.click_y_spin.value()
            
            if rel_x > 0 and rel_y > 0:
                # 상태 표시 업데이트
                self.status_signal.emit(f"클릭 중({index})... (X={rel_x}, Y={rel_y})")

                if 1 == index and WindowUtil.click_at_position_original(rel_x, rel_y):
                    self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")

                # elif 2 == index and WindowUtil.click_background_only(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_hardware_injection(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_raw_input(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_with_global_hook(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_at_position_pyautogui(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_with_win32_api(rel_x, rel_y):
                elif 2 == index and WindowUtil.click_with_sendinput(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_with_postmessage(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_stealth(rel_x, rel_y):
                # elif 2 == index and WindowUtil.click_hybrid_approach(rel_x, rel_y):
                    self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")

                # elif 3 == index and WindowUtil.click_at_position_post_message(rel_x, rel_y):
                #     self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                # elif 4 == index and WindowUtil.click_at_position_send_message(rel_x, rel_y):
                #     self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                # elif 5 == index and WindowUtil.click_at_position_uia(rel_x, rel_y):
                #     self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                # elif 6 == index and WindowUtil.click_at_position_interception(rel_x, rel_y):
                #     self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                # elif 7 == index and WindowUtil.click_at_position_win32(rel_x, rel_y):
                #     self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                # elif 8 == index and WindowUtil.click_at_position_pynput(rel_x, rel_y):
                #     self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                else:
                    QMessageBox.critical(self, "오류", "클릭 작업에 실패했습니다.")
                
                # # 상대 좌표 위치 클릭
                # if WindowUtil.click_at_position(rel_x, rel_y):
                #     self.status_signal.emit(f"마우스 클릭 완료 (창 내부 좌표: X={rel_x}, Y={rel_y})")
                # else:
                #     QMessageBox.critical(self, "오류", "클릭 작업에 실패했습니다.")
            else:
                QMessageBox.information(self, "알림", "클릭할 좌표를 설정해주세요.")
                
        except Exception as e:
            QMessageBox.critical(self, "마우스 클릭 오류", f"마우스 클릭 중 오류가 발생했습니다: {str(e)}")        
            
    @Slot()
    def mouse_scroll(self):
        """위로 마우스 휠 스크롤"""
        try:
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
                return
            
            # 스크롤 양 가져오기 (항상 양수)
            amount = self.scroll_amount_spin.value()
            if 0 == amount: return

            way = "위로" if 0 < amount else "아래로"
            # 상태 표시 업데이트
            self.status_signal.emit(f"{way} 스크롤 중... ({abs(amount)}단위)")
            
            # 스크롤 수행 (양수 = 위로)
            if WindowUtil.scroll_mousewheel(amount):
                self.status_signal.emit(f"{way} 마우스 휠 스크롤 완료 ({abs(amount)}단위)")
            else:
                QMessageBox.critical(self, "오류", "스크롤 작업에 실패했습니다.")
                    
        except Exception as e:
            QMessageBox.critical(self, "마우스 스크롤 오류", f"마우스 스크롤 중 오류가 발생했습니다: {str(e)}")

    # @Slot()
    # def mouse_scroll_down(self):
    #     """아래로 마우스 휠 스크롤"""
    #     try:
    #         if not WindowUtil.is_window_valid():
    #             QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
    #             return
            
    #         # 스크롤 양 가져오기 (음수로 변환)
    #         amount = -self.scroll_amount_spin.value()
            
    #         # 상태 표시 업데이트
    #         self.status_signal.emit(f"아래로 스크롤 중... ({abs(amount)}단위)")
            
    #         # 스크롤 수행 (음수 = 아래로)
    #         if WindowUtil.scroll_mousewheel(amount):
    #             self.status_signal.emit(f"아래로 마우스 휠 스크롤 완료 ({abs(amount)}단위)")
    #         else:
    #             QMessageBox.critical(self, "오류", "스크롤 작업에 실패했습니다.")
                    
    #     except Exception as e:
    #         QMessageBox.critical(self, "마우스 스크롤 오류", f"마우스 스크롤 중 오류가 발생했습니다: {str(e)}")
    
    @Slot()
    def copy_current_mouse_position(self):
        """현재 마우스 위치를 클릭 좌표에 복사"""
        if not WindowUtil.is_window_valid():
            QMessageBox.critical(self, "오류", "먼저 창에 연결해주세요.")
            return
        
        # 현재 마우스 위치
        x, y = pyautogui.position()
        
        # 상대 좌표 계산
        rel_x, rel_y = WindowUtil.get_relative_position(x, y)
        
        # 클릭 좌표에 복사
        self.click_x_spin.setValue(rel_x)
        self.click_y_spin.setValue(rel_y)
        
        self.status_signal.emit(f"현재 마우스 위치가 복사되었습니다: X={rel_x}, Y={rel_y}")
    
    def update_mouse_position(self):
        """마우스 위치 업데이트"""
        x, y = pyautogui.position()
        rel_x, rel_y = x, y
        
        # 연결된 창이 있으면 상대 좌표 계산
        if WindowUtil.is_window_valid():
            rel_x, rel_y = WindowUtil.get_relative_position(x, y)
        
        self.mouse_pos_label.setText(f"마우스 위치: 절대(X={x}, Y={y}) / 상대(X={rel_x}, Y={rel_y})")