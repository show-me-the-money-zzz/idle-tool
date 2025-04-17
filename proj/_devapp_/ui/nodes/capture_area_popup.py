from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
                             QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QGridLayout, QComboBox, QTextEdit, QScrollArea,
                             QFrame, QMessageBox, QFileDialog)
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PIL import Image, ImageQt
from datetime import datetime
import time
import os

from zzz.config import *
from stores import areas
from grinder_utils.system import Calc_MS
from core.window_utils import WindowUtil

class CaptureAreaPopup(QDialog):
    """캡처 영역 설정 팝업 창"""
    
    READTEXT_BUTTON_START_TEXT = "글자 읽기 ▶"
    READTEXT_BUTTON_STOP_TEXT = "글자 읽기 ■"

    def __init__(self, parent, region_selector, capture_manager, status_signal, on_close_callback=None):
        super().__init__(parent)
        self.setWindowTitle("캡처 영역 설정")
        self.resize(700, 640)
        
        self.parent = parent
        self.region_selector = region_selector
        self.capture_manager = capture_manager
        self.status_signal = status_signal
        self.on_close_callback = on_close_callback

        self.preview_image = None
        self.preview_pixmap = None
        self.capture_settings = None
        self.reading_text = False
        self.selected_colors = []

        self._setup_ui()

    def _setup_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        
        # 상단 컨트롤 영역
        top_controls = QHBoxLayout()
        
        # 좌측 설정 영역
        settings_group = QGroupBox("위치 및 크기")
        settings_layout = QVBoxLayout(settings_group)
        
        # 캡처 타입 및 키 입력 영역
        key_layout = QHBoxLayout()
        
        # 캡처 방식 선택 콤보박스
        self.capture_type_combo = QComboBox()
        self.capture_type_combo.addItems(["이미지", "빈영역", "텍스트"])
        key_layout.addWidget(self.capture_type_combo)
        
        # KEY 레이블과 입력
        key_layout.addWidget(QLabel("KEY"))
        self.key_input = QLineEdit()
        key_layout.addWidget(self.key_input)
        
        settings_layout.addLayout(key_layout)
        
        # 키워드 안내 텍스트
        keywords_text = f"※ 예약 키워드: {' / '.join(LOOP_TEXT_KEYWORD)} / {' / '.join(LOOP_IMAGE_KEYWORD)}"
        keywords_label = QLabel(keywords_text)
        keywords_label.setWordWrap(True)
        keywords_label.setStyleSheet("font-size: 8pt; color: gray;")
        settings_layout.addWidget(keywords_label)
        
        # 좌표 및 크기 입력 영역
        coords_layout = QGridLayout()
        
        # X 좌표
        coords_layout.addWidget(QLabel("X 좌표:"), 0, 0)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setValue(int(DEFAULT_CAPTURE_X))
        coords_layout.addWidget(self.x_spin, 0, 1)
        
        # Y 좌표
        coords_layout.addWidget(QLabel("Y 좌표:"), 0, 2)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setValue(int(DEFAULT_CAPTURE_Y))
        coords_layout.addWidget(self.y_spin, 0, 3)
        
        # 너비
        coords_layout.addWidget(QLabel("너비:"), 0, 4)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 9999)
        self.width_spin.setValue(int(DEFAULT_CAPTURE_WIDTH))
        coords_layout.addWidget(self.width_spin, 0, 5)
        
        # 높이
        coords_layout.addWidget(QLabel("높이:"), 0, 6)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 9999)
        self.height_spin.setValue(int(DEFAULT_CAPTURE_HEIGHT))
        coords_layout.addWidget(self.height_spin, 0, 7)
        
        settings_layout.addLayout(coords_layout)
        
        # 간격 및 창 내부 선택 옵션
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("글자읽기 간격(초):"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 10.0)
        self.interval_spin.setValue(1.0)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setReadOnly(True)
        options_layout.addWidget(self.interval_spin)
        
        self.window_only_check = QCheckBox("창 내부만 선택")
        self.window_only_check.setChecked(True)
        self.window_only_check.setEnabled(False)
        options_layout.addWidget(self.window_only_check)
        
        settings_layout.addLayout(options_layout)
        
        top_controls.addWidget(settings_group, 3)  # 비율 3
        
        # 우측 버튼 영역
        buttons_group = QGroupBox()
        buttons_layout = QVBoxLayout(buttons_group)
        
        # 동작 버튼 그룹
        action_group = QGroupBox("동작")
        action_layout = QVBoxLayout(action_group)
        
        select_area_btn = QPushButton("영역 선택")
        select_area_btn.clicked.connect(self.select_capture_area)
        action_layout.addWidget(select_area_btn)
        
        preview_btn = QPushButton("미리보기 업뎃")
        preview_btn.clicked.connect(self.update_area_preview)
        action_layout.addWidget(preview_btn)
        
        self.read_text_btn = QPushButton(self.READTEXT_BUTTON_START_TEXT)
        self.read_text_btn.clicked.connect(self.toggle_read_text)
        action_layout.addWidget(self.read_text_btn)
        
        buttons_layout.addWidget(action_group)
        
        # 작업 버튼 그룹
        work_group = QGroupBox("작업")
        work_layout = QVBoxLayout(work_group)
        
        # 저장 버튼 - 녹색 스타일
        save_btn = QPushButton("저장")
        save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        save_btn.clicked.connect(self.apply_settings)
        work_layout.addWidget(save_btn)
        
        # 여백 추가
        work_layout.addStretch(1)
        
        # 취소 버튼 - 빨간색 스타일
        cancel_btn = QPushButton("취소하고 닫기")
        cancel_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        cancel_btn.clicked.connect(self.on_close)
        work_layout.addWidget(cancel_btn)
        
        buttons_layout.addWidget(work_group, 1)  # stretch 1
        
        top_controls.addWidget(buttons_group, 1)  # 비율 1
        
        main_layout.addLayout(top_controls)
        
        # 미리보기 영역
        preview_group = QGroupBox("영역 미리보기")
        preview_layout = QVBoxLayout(preview_group)
        
        # 색상 추출 영역
        color_layout = QHBoxLayout()
        
        self.extract_color_btn = QPushButton("색 추출")
        self.extract_color_btn.clicked.connect(self.extract_color)
        self.extract_color_btn.setEnabled(False)
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
        self.preview_label.setStyleSheet("background-color: lightgray;")
        self.preview_label.setText("영역을 선택하면\n미리보기가 표시됩니다")
        preview_layout.addWidget(self.preview_label)
        
        main_layout.addWidget(preview_group, 1)  # stretch 1
        
        # 로그 영역
        log_group = QGroupBox("인식된 텍스트")
        log_layout = QVBoxLayout(log_group)
        
        # 로그 컨트롤 영역
        log_control = QHBoxLayout()
        
        log_control.addStretch(1)  # 오른쪽 정렬을 위한 빈 공간
        
        clear_log_btn = QPushButton("로그 초기화")
        clear_log_btn.clicked.connect(self.clear_log)
        log_control.addWidget(clear_log_btn)
        
        log_layout.addLayout(log_control)
        
        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group, 1)  # stretch 1
        
        # 테스트용 색상 추가
        self.test_add_colors()

    def test_add_colors(self):
        """테스트용 색상 추가"""
        colors = ["red", "green", "blue", "#ff00ff", "#ffffff"]
        for _ in range(5):  # 5번 반복
            for color in colors:
                self.add_color(color)

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

    def clear_log(self):
        """로그 내용 초기화"""
        self.log_text.clear()

    def toggle_read_text(self):
        """텍스트 읽기 시작/중지"""
        self.reading_text = not self.reading_text
        
        if self.reading_text:
            self.read_text_btn.setText(self.READTEXT_BUTTON_STOP_TEXT)
            self._read_loop_main()
        else:
            self.read_text_btn.setText(self.READTEXT_BUTTON_START_TEXT)

    def _read_loop_main(self):
        """텍스트 읽기 반복 함수"""
        if not self.reading_text:
            return
            
        self.read_text_from_area()
        
        try:
            interval = Calc_MS(float(self.interval_spin.value()))
        except ValueError:
            interval = 2000
            
        QTimer.singleShot(interval, self._read_loop_main)

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
            self.log_text.append(f"[{timestamp}] {recognized_text}")
            
            # 스크롤 맨 아래로 이동
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
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
            self.update_area_preview()
        
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
                
                # 영역 자르기
                cropped_img = full_window_img.crop((
                    max(0, x),
                    max(0, y),
                    min(img_width, x + width),
                    min(img_height, y + height)
                ))
                
                # 캔버스에 맞게 이미지 크기 조정 (비율 유지)
                img_width, img_height = cropped_img.size
                
                # 미리보기 레이블 크기
                preview_width = self.preview_label.width()
                preview_height = self.preview_label.height()
                
                # 비율 계산
                width_ratio = preview_width / img_width
                height_ratio = preview_height / img_height
                scale_ratio = min(width_ratio, height_ratio)
                
                # 이미지가 너무 크면 축소
                if scale_ratio < 1:
                    new_width = int(img_width * scale_ratio)
                    new_height = int(img_height * scale_ratio)
                    resized_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)
                else:
                    resized_img = cropped_img
                
                # PIL 이미지를 QImage로 변환
                self.preview_image = resized_img
                q_image = ImageQt.ImageQt(resized_img)
                self.preview_pixmap = QPixmap.fromImage(q_image)
                
                # 레이블에 이미지 표시
                self.preview_label.setPixmap(self.preview_pixmap)
                
                # 추출 버튼 활성화
                self.extract_color_btn.setEnabled(False)
                
                self.status_signal.emit("영역 미리보기가 업데이트되었습니다.")
                
            except Exception as e:
                QMessageBox.critical(self, "미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
                
        except Exception as e:
            QMessageBox.critical(self, "미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")

    def apply_settings(self):
        """설정 적용 및 저장"""
        mode = self.capture_type_combo.currentText()
        
        if mode == "이미지":
            self.save_as_image()
        elif mode == "빈영역":
            self.save_as_zone()
        elif mode == "텍스트":
            self.save_as_text()

    def save_as_text(self):
        """텍스트 영역으로 저장"""
        try:
            # 설정값 검증
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, interval = capture_info
            key = self.key_input.text()
            
            if not key:
                QMessageBox.critical(self, "오류", "KEY를 입력하세요.")
                return
 
            areas.Add_TextArea(key, {"x": x, "y": y, "width": width, "height": height})
                
            # 설정 저장
            self.capture_settings = capture_info
            
            # 성공 메시지 표시
            self.status_signal.emit("텍스트가 저장되었습니다.")
            
            QMessageBox.information(self, "알림", f"{key} 텍스트 데이터를 추가하였습니다.")
            
            # 창 닫기
            self.on_close()
            
        except Exception as e:
            QMessageBox.critical(self, "설정 오류", f"설정을 적용하는 중 오류가 발생했습니다: {str(e)}")

    def save_as_image(self):
        """이미지로 저장"""
        try:
            # 캡처 영역 좌표 가져오기
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, _ = capture_info
            
            # 창이 유효한지 확인
            if not WindowUtil.is_window_valid():
                QMessageBox.critical(self, "오류", "창이 연결되지 않았습니다.")
                return
            
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
            
            # 저장할 기본 파일명 생성
            key = self.key_input.text().strip()
            if not key:
                QMessageBox.critical(self, "오류", "KEY를 입력하세요.")
                return
            
            # 기본 파일명
            default_filename = key
            
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
            data_path = Path(finder.Get_DataPath())
            file_path_obj = Path(file_path)
            
            try:
                # 상대 경로 생성 시도
                relative_path = file_path_obj.relative_to(data_path)
                stored_path = str(relative_path)
            except ValueError:
                # 상대 경로 생성 실패 시 전체 경로 사용
                stored_path = file_path
            
            # 이미지 정보를 JSON에 저장
            areas.Add_ImageArea(key, {
                "x": x, "y": y, 
                "width": width, "height": height,
                "file": stored_path
            })
            
            self.status_signal.emit(f"이미지가 저장되었습니다: {file_path}")
            
            QMessageBox.information(self, "알림", f"{key} 이미지 데이터를 추가하였습니다.")
            
            # 창 닫기
            self.on_close()
            
        except Exception as e:
            QMessageBox.critical(self, "이미지 저장 오류", f"이미지 저장 중 오류가 발생했습니다: {str(e)}")

    def save_as_zone(self):
        """빈 영역으로 저장"""
        try:
            # 설정값 검증
            capture_info = self.get_capture_info()
            if not capture_info:
                return
            
            x, y, width, height, _ = capture_info
            key = self.key_input.text()
            
            if not key:
                QMessageBox.critical(self, "오류", "KEY를 입력하세요.")
                return
 
            areas.Add_ZoneArea(key, {"x": x, "y": y, "width": width, "height": height})
                
            # 설정 저장
            self.capture_settings = capture_info
            
            # 성공 메시지 표시
            self.status_signal.emit("빈영역이 저장되었습니다.")
            
            QMessageBox.information(self, "알림", f"{key} 빈영역 데이터를 추가하였습니다.")
            
            # 창 닫기
            self.on_close()
            
        except Exception as e:
            QMessageBox.critical(self, "설정 오류", f"설정을 적용하는 중 오류가 발생했습니다: {str(e)}")

    def get_capture_info(self):
        """캡처 정보 가져오기"""
        try:
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value()
            interval = float(self.interval_spin.value())
            
            if width <= 0 or height <= 0 or interval <= 0:
                raise ValueError("너비, 높이, 간격은 양수여야 합니다.")
                
            return (x, y, width, height, interval)
        except ValueError as e:
            QMessageBox.critical(self, "입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
            return None

    def set_capture_info(self, x, y, width, height, interval):
        """캡처 정보 설정"""
        self.x_spin.setValue(x)
        self.y_spin.setValue(y)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        self.interval_spin.setValue(interval)
        
        # 미리보기 업데이트
        self.update_area_preview()

    def on_close(self):
        """창 닫기"""
        self.reading_text = False
        if self.on_close_callback:
            self.on_close_callback(self.capture_settings)
        self.reject()  # 다이얼로그 닫기