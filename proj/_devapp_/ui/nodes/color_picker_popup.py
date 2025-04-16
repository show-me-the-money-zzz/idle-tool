from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QFrame, QCheckBox, QDoubleSpinBox, QWidget,
                             QSizePolicy)
from PySide6.QtGui import (QPixmap, QImage, QPainter, QColor, QPen, QCursor, QKeyEvent,
                          QResizeEvent, QMouseEvent)
from PySide6.QtCore import Qt, QPoint, QSize, QTimer, Signal, Slot
from PIL import Image, ImageDraw, ImageQt
import numpy as np
import os

from zzz.config import COLOR_EXTRACT_MODE_SWAP_KEY


class ColorPickerPopup(QDialog):
    """색상 선택 팝업 창"""
    
    PIPETTE_OFF_TEXT = "💉"
    PIPETTE_OFF_COLOR_BG = "#f0f0f0"
    PIPETTE_OFF_COLOR_TEXT = "black"
    PIPETTE_ON_TEXT = "💢"
    PIPETTE_ON_COLOR_BG = "#ff6347"
    PIPETTE_ON_COLOR_TEXT = "white"
    
    DEFAULT_ZOOM = 1.5
    
    def __init__(self, parent, image, callback=None):
        super().__init__(parent)
        self.setWindowTitle("색상 추출")
        self.resize(900, 800)  # 창 크기를 900x800으로 설정
        self.setModal(True)  # 모달 창으로 설정
        
        self.parent = parent
        self.callback = callback
        
        # 이미지 로드 (PIL Image 직접 사용)
        if isinstance(image, str):
            # 파일 경로인 경우
            if os.path.exists(image):
                self.original_image = Image.open(image)
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "오류", "이미지 파일을 찾을 수 없습니다.")
                self.reject()
                return
        elif isinstance(image, Image.Image):
            # PIL Image 객체인 경우
            self.original_image = image.copy()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "오류", "지원되지 않는 이미지 형식입니다.")
            self.reject()
            return
        
        self.processed_image = self.original_image.copy()
        
        # 상태 변수
        self.is_picking = False  # 색상 추출 모드 상태
        self.selected_colors = []  # 선택된 색상 목록
        self.zoom_factor = ColorPickerPopup.DEFAULT_ZOOM  # 확대/축소 비율
        self.image_position = QPoint(0, 0)  # 이미지 드래그 위치
        self.drag_start = None  # 드래그 시작 위치
        self.show_grid = False  # 그리드 표시 여부
        
        # UI 컴포넌트
        self._setup_ui()
        
        # 리사이즈 이벤트 연결
        self.resizeEvent = self.on_resize
        
        # 처음 이미지 로드
        QTimer.singleShot(100, self.update_top_image)
        QTimer.singleShot(100, self.update_bottom_image)
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 상단 컨트롤 프레임
        control_frame = QWidget()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(control_frame)
        
        # 스포이드 버튼 (왼쪽)
        self.eyedropper_btn = QPushButton(ColorPickerPopup.PIPETTE_OFF_TEXT)
        self.eyedropper_btn.setFixedWidth(30)
        self.eyedropper_btn.setStyleSheet(
            f"background-color: {ColorPickerPopup.PIPETTE_OFF_COLOR_BG}; "
            f"color: {ColorPickerPopup.PIPETTE_OFF_COLOR_TEXT};"
        )
        self.eyedropper_btn.clicked.connect(self.toggle_picking_mode)
        control_layout.addWidget(self.eyedropper_btn)
        
        # 색상 팔레트 프레임 (중앙)
        palette_frame = QWidget()
        palette_layout = QVBoxLayout(palette_frame)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        palette_layout.setSpacing(0)
        control_layout.addWidget(palette_frame, 1)  # 1은 stretch factor
        
        # 색상 스크롤 영역
        self.color_scroll = QScrollArea()
        self.color_scroll.setWidgetResizable(True)
        self.color_scroll.setFixedHeight(40)
        self.color_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.color_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        palette_layout.addWidget(self.color_scroll)
        
        # 색상 프레임
        self.color_frame = QFrame()
        self.color_frame.setStyleSheet("background-color: transparent;")
        self.color_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        color_frame_layout = QHBoxLayout(self.color_frame)
        color_frame_layout.setContentsMargins(0, 0, 0, 0)
        color_frame_layout.setSpacing(2)
        color_frame_layout.addStretch(1)  # 오른쪽 정렬을 위한 왼쪽 빈 공간
        
        self.color_scroll.setWidget(self.color_frame)
        
        # 상단 이미지 프레임
        top_image_frame = QWidget()
        top_image_layout = QHBoxLayout(top_image_frame)
        top_image_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(top_image_frame, 1)  # 1은 stretch factor
        
        # 좌측 확대/축소 컨트롤
        zoom_control = QWidget()
        zoom_control_layout = QVBoxLayout(zoom_control)
        zoom_control_layout.setContentsMargins(0, 0, 0, 0)
        top_image_layout.addWidget(zoom_control)
        
        # 확대율 라벨
        zoom_label = QLabel("확대율")
        zoom_control_layout.addWidget(zoom_label)
        
        # 확대율 스핀박스
        self.zoom_spinbox = QDoubleSpinBox()
        self.zoom_spinbox.setRange(1.0, 15.0)
        self.zoom_spinbox.setSingleStep(0.5)
        self.zoom_spinbox.setValue(ColorPickerPopup.DEFAULT_ZOOM)
        self.zoom_spinbox.setDecimals(1)
        self.zoom_spinbox.valueChanged.connect(self.update_zoom_from_spinbox)
        zoom_control_layout.addWidget(self.zoom_spinbox)
        
        # 그리드 표시 체크박스
        self.grid_checkbox = QCheckBox("Grid")
        self.grid_checkbox.setChecked(False)
        self.grid_checkbox.clicked.connect(self.toggle_grid)
        zoom_control_layout.addWidget(self.grid_checkbox)
        
        # 이미지 초기 위치로 리셋 버튼
        reset_pos_btn = QPushButton("📌")
        reset_pos_btn.setFixedWidth(30)
        reset_pos_btn.clicked.connect(self.reset_image_position)
        reset_pos_btn.setStyleSheet("background-color: #f0f0f0; color: black;")
        zoom_control_layout.addWidget(reset_pos_btn)
        
        # 여백 추가
        zoom_control_layout.addStretch(1)
        
        # 상단 이미지 캔버스 (QLabel로 구현)
        self.top_canvas = QLabel()
        self.top_canvas.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
        self.top_canvas.setAlignment(Qt.AlignCenter)
        self.top_canvas.setMinimumSize(QSize(200, 200))
        self.top_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.top_canvas.setMouseTracking(True)
        
        # 마우스 이벤트 연결
        self.top_canvas.mousePressEvent = self.handle_canvas_press
        self.top_canvas.mouseMoveEvent = self.handle_canvas_move
        self.top_canvas.mouseReleaseEvent = self.handle_canvas_release
        
        top_image_layout.addWidget(self.top_canvas, 1)  # 1은 stretch factor
        
        # 안내 메시지
        info_text = f"<{COLOR_EXTRACT_MODE_SWAP_KEY}> 키로 모드를 변경할 수 있습니다. 그리드는 1.5 이상부터 보입니다.\n이미지 드래그는 모드 OFF 에만 가능합니다. 드래그 한 이미지의 위치를 초기화 하려면 📌 버튼을 누르세요."
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # 하단 이미지 캔버스
        self.bottom_canvas = QLabel()
        self.bottom_canvas.setStyleSheet("background-color: lightgray; border: 1px solid white;")
        self.bottom_canvas.setAlignment(Qt.AlignCenter)
        self.bottom_canvas.setMinimumSize(QSize(200, 200))
        self.bottom_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.bottom_canvas, 1)  # 1은 stretch factor
        
        # 버튼 프레임
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(button_frame)
        
        # 여백 추가
        button_layout.addStretch(1)
        
        # 적용 버튼
        apply_btn = QPushButton("적용")
        apply_btn.clicked.connect(self.apply)
        button_layout.addWidget(apply_btn)
        
        # 취소 버튼
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.cancel)
        button_layout.addWidget(cancel_btn)
        
        # 키 이벤트 필터 설치
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """이벤트 필터 (키 이벤트 처리)"""
        if event.type() == QKeyEvent.Type.KeyPress:
            key = event.key()
            # Z 키 처리 (대소문자 구분 없이)
            if event.text().lower() == COLOR_EXTRACT_MODE_SWAP_KEY.lower():
                # Spinbox에 포커스가 없을 때만 모드 전환
                if self.zoom_spinbox != self.focusWidget():
                    self.toggle_picking_mode()
                    return True
        
        return super().eventFilter(obj, event)
    
    def toggle_picking_mode(self):
        """색상 추출 모드 토글"""
        self.is_picking = not self.is_picking
        
        if self.is_picking:
            self.eyedropper_btn.setText(ColorPickerPopup.PIPETTE_ON_TEXT)
            self.eyedropper_btn.setStyleSheet(
                f"background-color: {ColorPickerPopup.PIPETTE_ON_COLOR_BG}; "
                f"color: {ColorPickerPopup.PIPETTE_ON_COLOR_TEXT};"
            )
            self.top_canvas.setCursor(Qt.CrossCursor)  # 십자 커서
        else:
            self.eyedropper_btn.setText(ColorPickerPopup.PIPETTE_OFF_TEXT)
            self.eyedropper_btn.setStyleSheet(
                f"background-color: {ColorPickerPopup.PIPETTE_OFF_COLOR_BG}; "
                f"color: {ColorPickerPopup.PIPETTE_OFF_COLOR_TEXT};"
            )
            self.top_canvas.setCursor(Qt.ArrowCursor)  # 기본 커서
    
    def toggle_grid(self):
        """그리드 표시 토글"""
        self.show_grid = self.grid_checkbox.isChecked()
        self.update_top_image()
    
    def handle_canvas_press(self, event):
        """캔버스 마우스 클릭 이벤트"""
        if self.is_picking:
            # 색상 추출 모드일 때
            self.on_canvas_click(event)
        else:
            # 드래그 모드일 때
            self.start_drag(event)
    
    def handle_canvas_move(self, event):
        """캔버스 마우스 이동 이벤트"""
        if not self.is_picking and self.drag_start is not None:
            self.drag_image(event)
    
    def handle_canvas_release(self, event):
        """캔버스 마우스 릴리스 이벤트"""
        self.stop_drag(event)
    
    def on_canvas_click(self, event):
        """캔버스 클릭 이벤트 처리 (색상 추출)"""
        if not self.is_picking:
            return
        
        # 클릭한 위치의 픽셀 색상 가져오기
        x, y = self.get_image_coordinates(event.position().x(), event.position().y())
        
        if 0 <= x < self.original_image.width and 0 <= y < self.original_image.height:
            color = self.original_image.getpixel((x, y))
            
            # RGB 형식으로 변환
            if isinstance(color, int):  # 그레이스케일
                hex_color = f"#{color:02x}{color:02x}{color:02x}"
            elif len(color) >= 3:  # RGB 또는 RGBA
                hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            else:
                return
            
            # 색상 추가
            self.add_color(hex_color)
            
            # 하단 이미지 업데이트
            self.update_bottom_image()
    
    def get_image_coordinates(self, canvas_x, canvas_y):
        """캔버스 좌표를 이미지 좌표로 변환"""
        # 확대/축소 및 위치 오프셋 고려
        image_x = int((canvas_x - self.image_position.x()) / self.zoom_factor)
        image_y = int((canvas_y - self.image_position.y()) / self.zoom_factor)
        return image_x, image_y
    
    def add_color(self, color_hex):
        """색상 팔레트에 색상 추가"""
        # 동일한 색상이 이미 있으면 추가하지 않음
        if color_hex in self.selected_colors:
            return
        
        # 색상을 목록에 추가
        self.selected_colors.append(color_hex)
        
        # 색상 버튼 생성
        color_btn = QPushButton()
        color_btn.setFixedSize(30, 30)
        color_btn.setStyleSheet(f"background-color: {color_hex}; border: 1px solid gray;")
        
        # 버튼에 색상 정보 저장 (속성으로)
        color_btn.color = color_hex
        
        # 버튼 클릭 이벤트 연결
        color_btn.clicked.connect(lambda: self.remove_color(color_hex))
        
        # 버튼을 색상 프레임에 추가 (왼쪽으로 정렬)
        self.color_frame.layout().insertWidget(0, color_btn)
        
        # 하단 캔버스 테두리 색상을 흰색으로 변경
        self.bottom_canvas.setStyleSheet("background-color: lightgray; border: 1px solid white;")
    
    def remove_color(self, color_hex):
        """색상 팔레트에서 색상 제거"""
        if color_hex in self.selected_colors:
            self.selected_colors.remove(color_hex)
            
            # 해당 색상 버튼 제거
            for i in range(self.color_frame.layout().count()):
                widget = self.color_frame.layout().itemAt(i).widget()
                if widget and hasattr(widget, 'color') and widget.color == color_hex:
                    widget.deleteLater()
                    break
            
            # 선택된 색상이 없으면 테두리 색상을 원래대로 변경
            if not self.selected_colors:
                self.bottom_canvas.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
            
            # 하단 이미지 업데이트
            self.update_bottom_image()
    
    def update_top_image(self):
        """상단 이미지 캔버스 업데이트 (픽셀 확대 지원)"""
        if not hasattr(self, 'original_image'):
            return
        
        # 캔버스 크기 가져오기
        canvas_width = self.top_canvas.width()
        canvas_height = self.top_canvas.height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # 아직 캔버스가 렌더링되지 않은 경우
            QTimer.singleShot(100, self.update_top_image)
            return
        
        # 원본 이미지 리사이징 (확대/축소 비율 적용)
        img_width = int(self.original_image.width * self.zoom_factor)
        img_height = int(self.original_image.height * self.zoom_factor)
        
        # 픽셀 단위로 확대하기 위해 새 이미지 생성
        resized_img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(resized_img)
        
        # 원본 이미지의 각 픽셀을 확대하여 그리기
        for y in range(self.original_image.height):
            for x in range(self.original_image.width):
                # 원본 픽셀 색상 가져오기
                pixel = self.original_image.getpixel((x, y))
                
                # RGB 또는 RGBA 포맷 처리
                if isinstance(pixel, int):  # 그레이스케일
                    color = (pixel, pixel, pixel)
                elif len(pixel) >= 3:  # RGB 또는 RGBA
                    color = pixel[:3]
                else:
                    color = (0, 0, 0)  # 기본값
                
                # 확대된 픽셀 좌표 계산
                x1 = int(x * self.zoom_factor)
                y1 = int(y * self.zoom_factor)
                x2 = int((x + 1) * self.zoom_factor)
                y2 = int((y + 1) * self.zoom_factor)
                
                # 픽셀 그리기
                draw.rectangle([x1, y1, x2-1, y2-1], fill=color)
        
        if self.show_grid and self.zoom_factor >= 1.5:
            grid_color = (100, 100, 100)
            grid_width = max(1, int(self.zoom_factor / 10))  # 확대율에 따라 선 굵기만 유동

            for y in range(self.original_image.height + 1):
                y_pos = int(y * self.zoom_factor)
                draw.line([(0, y_pos), (img_width, y_pos)], fill=grid_color, width=grid_width)

            for x in range(self.original_image.width + 1):
                x_pos = int(x * self.zoom_factor)
                draw.line([(x_pos, 0), (x_pos, img_height)], fill=grid_color, width=grid_width)
        
        # PIL 이미지를 QPixmap으로 변환
        q_image = ImageQt.ImageQt(resized_img)
        pixmap = QPixmap.fromImage(q_image)
        
        # 이미지 표시
        painter = QPainter()
        result_pixmap = QPixmap(canvas_width, canvas_height)
        result_pixmap.fill(QColor(240, 240, 240))  # 배경 색상
        
        painter.begin(result_pixmap)
        
        # 이미지 그리기 (중앙 정렬)
        x_pos = max(0, (canvas_width - img_width) // 2) + self.image_position.x()
        y_pos = max(0, (canvas_height - img_height) // 2) + self.image_position.y()
        painter.drawPixmap(x_pos, y_pos, pixmap)
        
        painter.end()
        
        # 최종 이미지 표시
        self.top_canvas.setPixmap(result_pixmap)
        
        # 확대 비율 업데이트
        self.zoom_spinbox.setValue(self.zoom_factor)
    
    def update_bottom_image(self):
        """하단 이미지 캔버스 업데이트 (선택된 색상만 표시, 원본 크기로 출력)"""
        if not hasattr(self, 'original_image'):
            return
        
        # 선택된 색상이 없으면 원본 이미지 표시
        if not self.selected_colors:
            img_to_display = self.original_image
            self.processed_image = self.original_image.copy()
        else:
            # 선택된 색상만 마스킹
            img_array = np.array(self.original_image)
            mask = np.zeros_like(img_array)
            
            for color_hex in self.selected_colors:
                r = int(color_hex[1:3], 16)
                g = int(color_hex[3:5], 16)
                b = int(color_hex[5:7], 16)
                
                threshold = 10
                color_mask = (
                    (np.abs(img_array[:, :, 0] - r) <= threshold) &
                    (np.abs(img_array[:, :, 1] - g) <= threshold) &
                    (np.abs(img_array[:, :, 2] - b) <= threshold)
                )
                
                mask[color_mask] = img_array[color_mask]
            
            img_to_display = Image.fromarray(mask)
            self.processed_image = img_to_display
        
        # 캔버스 크기 가져오기
        canvas_width = self.bottom_canvas.width()
        canvas_height = self.bottom_canvas.height()
        
        # PIL 이미지를 QPixmap으로 변환
        q_image = ImageQt.ImageQt(img_to_display)
        pixmap = QPixmap.fromImage(q_image)
        
        # 이미지 크기 조정 (캔버스에 맞게)
        scaled_pixmap = pixmap.scaled(
            canvas_width,
            canvas_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # 이미지 표시
        self.bottom_canvas.setPixmap(scaled_pixmap)
    
    def reset_image_position(self):
        """이미지 위치를 초기 상태로 리셋"""
        self.image_position = QPoint(0, 0)
        self.update_top_image()
    
    def update_zoom_from_spinbox(self):
        """스핀박스에서 확대/축소 값 업데이트"""
        value = self.zoom_spinbox.value()
        if value >= 0.5:  # 최소 0.5 이상
            self.zoom_factor = value
            self.update_top_image()
    
    def start_drag(self, event):
        """이미지 드래그 시작"""
        if not self.is_picking:  # 색상 추출 모드가 아닐 때만 드래그 가능
            self.drag_start = event.position()
    
    def drag_image(self, event):
        """이미지 드래그 중"""
        if self.drag_start and not self.is_picking:
            # 드래그 거리 계산
            dx = event.position().x() - self.drag_start.x()
            dy = event.position().y() - self.drag_start.y()
            
            # 이미지 위치 업데이트
            self.image_position = QPoint(
                self.image_position.x() + int(dx),
                self.image_position.y() + int(dy)
            )
            
            # 드래그 시작점 업데이트
            self.drag_start = event.position()
            
            # 이미지 위치 업데이트
            self.update_top_image()
    
    def stop_drag(self, event):
        """이미지 드래그 종료"""
        self.drag_start = None
    
    def on_resize(self, event):
        """창 크기 변경 시 이미지 업데이트"""
        # 창 크기가 변경될 때 이미지 업데이트
        QTimer.singleShot(50, self.update_top_image)
        QTimer.singleShot(50, self.update_bottom_image)
    
    def cancel(self):
        """취소 버튼 클릭 처리"""
        self.reject()
    
    def apply(self):
        """적용 버튼 클릭 처리"""
        # 콜백 함수 호출
        if self.callback:
            self.callback(self.selected_colors, self.processed_image)
        
        self.accept()