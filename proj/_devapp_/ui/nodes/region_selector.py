import sys
import mss
import keyboard
from PIL import Image, ImageQt
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QWidget)
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen, QFont, QImage, QCursor
from PySide6.QtCore import Qt, QRect, QPoint, QSize, QTimer, Signal

from core.config import *
from core.window_utils import WindowUtil


class ZoomWindow(QWidget):
    """마우스 위치 주변을 확대하여 보여주는 창"""
    
    def __init__(self, parent=None):
        # 단순하게 최상위 창으로만 설정
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowTitle("Magnifier")
        
        # 창 속성 설정
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # 불투명 배경
        self.setWindowOpacity(1.0)  # 완전 불투명
        
        # 눈에 띄는 스타일
        self.setStyleSheet("QWidget { background-color: black; border: 3px solid red; }")
        
        self.zoom_size = 150  # 확대 창 크기
        self.zoom_factor = DRAG_ZOOM_FACTOR  # 확대 배율
        
        # 창 크기 설정
        self.setFixedSize(self.zoom_size, self.zoom_size + 25)
        
        # 스크린샷 저장 변수
        self.screenshot_pixmap = None
        self.parent_widget = parent  # 부모 위젯 참조 저장
        
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 확대 이미지 레이블
        self.zoom_label = QLabel()
        self.zoom_label.setFixedSize(self.zoom_size, self.zoom_size)
        self.zoom_label.setStyleSheet("background-color: black;")
        layout.addWidget(self.zoom_label)
        
        # 상태 레이블
        self.status_label = QLabel("준비됨")
        self.status_label.setFixedHeight(25)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setStyleSheet("background-color: #000000; color: #ffffff; font-weight: bold; padding: 2px;")
        layout.addWidget(self.status_label)
        
        # 명시적으로 show() 호출
        self.show()
        self.raise_()
        
        # 마우스 트래킹 타이머
        self.track_timer = QTimer(self)
        self.track_timer.timeout.connect(self.follow_mouse)
        self.track_timer.start(30)  # 30ms 간격으로 업데이트 (더 빠르게)
        
        # print("ZoomWindow 초기화 완료")
    
    # def __del__(self):
    #     print("소멸~~")

    def update_status(self, text, bg_color="lightgray"):
        """상태 텍스트 업데이트"""
        # print(bg_color)
        # bg_color="#000000"
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"background-color: {bg_color}; color: #000000; padding: 2px;")
        # self.status_label.setStyleSheet(
        #     f"background-color: {bg_color}; color: #00ff00; "
        #     "padding: 2px;"
        # )
    
    def set_screenshot(self, pixmap):
        """스크린샷 설정"""
        self.screenshot_pixmap = pixmap
    
    def follow_mouse(self):
        """마우스 커서 위치 따라 이동 (X는 고정, Y만 따라감)"""
        # 전역 커서 위치 가져오기
        cursor_pos = QCursor.pos()
        
        # 부모 위젯이 있는 경우 부모의 중앙 X 좌표 계산
        parent_size = QSize(0, 0)
        if hasattr(self, 'parent_widget') and self.parent_widget:
            # 부모 위젯의 중앙 계산
            geometry = self.parent_widget.geometry()
            parent_center_x = geometry.center().x()
            parent_size = geometry.size()
            screen_center_x = parent_center_x
        else:
            # 부모가 없으면 화면 중앙 사용
            screen_width = QApplication.primaryScreen().size().width()
            screen_center_x = screen_width // 2
        
        # X 위치 고정 (화면 중앙 기준 왼쪽 또는 오른쪽)
        if cursor_pos.x() < screen_center_x:
            zoom_x = screen_center_x - (parent_size.width() / 2) - self.width()
        else:
            zoom_x = screen_center_x + (parent_size.width() / 2)
            # zoom_x += self.width()
        
        # Y 위치는 마우스 위치 따라감
        zoom_y = cursor_pos.y() - self.height() // 2  # 마우스 위치 중앙에 맞춤
        
        # 화면 경계 벗어나지 않도록 보정
        screen_height = QApplication.primaryScreen().size().height()
        if zoom_y < 0:
            zoom_y = 0
        elif zoom_y + self.height() > screen_height:
            zoom_y = screen_height - self.height()
        
        # 현재 위치와 다를 때만 이동 (성능 향상)
        current_pos = self.pos()
        if (abs(current_pos.x() - zoom_x) > 5 or 
            abs(current_pos.y() - zoom_y) > 5):
            self.move(zoom_x, zoom_y)
        
        # 확대 뷰 업데이트 (부모 위젯이 있을 경우)
        if hasattr(self, 'parent_widget') and self.parent_widget:
            window_pos = self.parent_widget.mapFromGlobal(cursor_pos)
            self.update_zoom_view(window_pos.x(), window_pos.y())
        
        self.raise_()  # 항상 최상위에 유지
    
    def update_zoom_view(self, x, y):
        """확대 이미지 업데이트"""
        if not self.screenshot_pixmap:
            return
            
        try:
            # 확대할 영역 반경 계산
            zoom_radius = int(self.zoom_size / (2 * self.zoom_factor))
            
            # 영역 계산
            left = max(0, int(x - zoom_radius))
            top = max(0, int(y - zoom_radius))
            width = min(zoom_radius * 2, self.screenshot_pixmap.width() - left)
            height = min(zoom_radius * 2, self.screenshot_pixmap.height() - top)
            
            if width <= 0 or height <= 0:
                return
                
            # 영역 크롭
            crop_pixmap = self.screenshot_pixmap.copy(left, top, width, height)
            
            # 확대
            zoom_pixmap = crop_pixmap.scaled(
                self.zoom_size, 
                self.zoom_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # 십자선 추가 (더 밝은 색상으로)
            painter = QPainter(zoom_pixmap)
            
            # 십자선 (밝은 빨간색)
            pen = QPen(QColor(255, 50, 50))
            pen.setWidth(2)  # 선 두께 증가
            painter.setPen(pen)
            
            # 가로선
            painter.drawLine(0, self.zoom_size//2, self.zoom_size, self.zoom_size//2)
            # 세로선
            painter.drawLine(self.zoom_size//2, 0, self.zoom_size//2, self.zoom_size)
            
            painter.end()
            
            # 결과 이미지 표시
            self.zoom_label.setPixmap(zoom_pixmap)
            
        except Exception as e:
            print(f"확대 뷰 업데이트 오류: {e}")


class RegionSelectorDialog(QDialog):
    """모달 대화상자로 구현한 영역 선택기"""
    
    # 영역 선택 완료 시 발생하는 신호
    region_selected = Signal(dict)
    
    def __init__(self, parent=None, target_window_only=False):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        self.target_window_only = target_window_only
        self.window_rect = (0, 0, 0, 0)
        self.screenshot = None
        self.screenshot_pixmap = None
        
        # 드래그 관련 변수
        self.dragging = False
        self.start_point = None
        self.current_point = None
        self.selected_region = None
        
        # 고정 치수 관련 변수
        self.fixed_width = None
        self.fixed_height = None
        
        # UI 초기화
        self.init_ui()
        
        # 마우스 추적 활성화
        self.setMouseTracking(True)
        
        # 창 속성 설정
        self.setWindowOpacity(0.9)
        
        # ESC 키로 닫기 설정
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        # 캡처 영역 초기화
        self.capture_screenshot()
        
        # 확대 창 생성
        self.zoom_window = ZoomWindow(self)  # 자신을 부모로 전달
        self.zoom_window.set_screenshot(self.screenshot_pixmap)
        
        # 마우스 추적 타이머
        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.track_mouse)
        self.mouse_timer.start(50)  # 50ms 간격으로 업데이트
    
    def init_ui(self):
        """UI 구성요소 초기화"""
        # 메인 레이아웃
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 안내 레이블
        self.info_label = QLabel(self)
        self.info_label.setStyleSheet(
            "background-color: #0000ff; color: #ffffff; "
            "font-weight: bold; padding: 5px; border: 1px solid black;"
        )
        self.info_label.setText(
            f"[{DRAG_FIXED_WIDTH_KEY}] 너비 고정 / [{DRAG_FIXED_HEIGHT_KEY}] 높이 고정 / "
            f"[{DRAG_KEEP_SQUARE_KEY}] 정사각 비율 / [{DRAG_ASPECT_RATIO_KEY}] {DRAG_ASPECT_RATIO_TEXT} 비율 / "
            f"[ESC] 취소"
        )
        self.info_label.setGeometry(10, 10, 700, 30)
        self.info_label.adjustSize()
        
        # # 크기 정보 레이블
        # self.size_label = QLabel(self)
        # self.size_label.setStyleSheet(
        #     "background-color: rgba(0,0,0,180); color: white; "
        #     "font-weight: bold; padding: 5px; border-radius: 3px;"
        # )
        # self.size_label.setText("드래그하여 영역을 선택하세요")
        # self.size_label.adjustSize()
        # self.size_label.move(10, 50)
        
        self.setCursor(Qt.CrossCursor)
    
    def capture_screenshot(self):
        """스크린샷 캡처"""
        # 타겟 윈도우만 캡처할지 전체 화면을 캡처할지 결정
        if self.target_window_only and WindowUtil and WindowUtil.is_window_valid():
            # 타겟 윈도우 기준
            self.window_rect = WindowUtil.get_window_rect()
            left, top, right, bottom = self.window_rect
            width = right - left
            height = bottom - top
            
            # 창 위치 및 크기 설정
            self.setGeometry(left, top, width, height)
            
            # 타겟 윈도우 스크린샷
            with mss.mss() as sct:
                monitor = {"top": top, "left": left, "width": width, "height": height}
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                self.screenshot = img
        else:
            # 전체 화면
            screen = QApplication.primaryScreen()
            geometry = screen.geometry()
            left, top, width, height = geometry.x(), geometry.y(), geometry.width(), geometry.height()
            
            # 전체 화면 크기로 설정
            self.setGeometry(left, top, width, height)
            self.window_rect = (left, top, left + width, top + height)
            
            # 전체 화면 스크린샷
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                self.screenshot = img
        
        # PIL 이미지를 QPixmap으로 변환
        img_qt = QImage(
            self.screenshot.tobytes(),
            self.screenshot.width,
            self.screenshot.height,
            3 * self.screenshot.width,  # 바이트 수 (RGB)
            QImage.Format_RGB888
        )
        self.screenshot_pixmap = QPixmap.fromImage(img_qt)
        
        # 창 업데이트
        self.update()
    
    def track_mouse(self):
        """마우스 위치 추적 및 확대 창 업데이트"""
        if not hasattr(self, 'zoom_window') or not self.zoom_window:
            return
            
        # 현재 마우스 위치 가져오기
        cursor_pos = QCursor.pos()
        
        # 화면 내 상대 좌표로 변환
        window_pos = self.mapFromGlobal(cursor_pos)
        
        # 창 안에 있는지 확인
        if self.rect().contains(window_pos):
            # 확대 창 업데이트
            self.zoom_window.update_zoom_view(window_pos.x(), window_pos.y())
    
    def paintEvent(self, event):
        """화면 그리기 이벤트"""
        painter = QPainter(self)
        
        # 스크린샷 그리기
        if self.screenshot_pixmap:
            painter.drawPixmap(0, 0, self.screenshot_pixmap)
        
        # 선택 영역이 있으면 그리기
        if self.start_point and self.current_point:
            # 좌표 계산
            x1 = min(self.start_point.x(), self.current_point.x())
            y1 = min(self.start_point.y(), self.current_point.y())
            x2 = max(self.start_point.x(), self.current_point.x())
            y2 = max(self.start_point.y(), self.current_point.y())
            width = x2 - x1
            height = y2 - y1
            
            # 반투명 오버레이 생성 (선택 영역 제외한 영역을 어둡게)
            overlay_color = QColor(0, 0, 0, 128)  # 반투명 검은색
            
            # 위쪽 영역
            if y1 > 0:
                painter.fillRect(0, 0, self.width(), y1, overlay_color)
            
            # 아래쪽 영역
            if y2 < self.height():
                painter.fillRect(0, y2, self.width(), self.height() - y2, overlay_color)
            
            # 왼쪽 영역
            if x1 > 0:
                painter.fillRect(0, y1, x1, height, overlay_color)
            
            # 오른쪽 영역
            if x2 < self.width():
                painter.fillRect(x2, y1, self.width() - x2, height, overlay_color)
            
            # 선택 영역 테두리 (빨간색)
            pen = QPen(Qt.red)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(x1, y1, width, height)
            
            # 크기 표시 업데이트
            # self.update_size_label(width, height)
            
            # 확대 창 상태 업데이트
            if hasattr(self, 'zoom_window') and self.zoom_window:
                status_text = f"{int(width)} x {int(height)}"
                
                is_square_key_pressed = keyboard.is_pressed(DRAG_KEEP_SQUARE_KEY)
                is_width_key_pressed = keyboard.is_pressed(DRAG_FIXED_WIDTH_KEY)
                is_height_key_pressed = keyboard.is_pressed(DRAG_FIXED_HEIGHT_KEY)
                is_ratio_key_pressed = keyboard.is_pressed(DRAG_ASPECT_RATIO_KEY)
                
                if is_ratio_key_pressed:
                    ratio_text = f"{DRAG_ASPECT_RATIO:.1f}"
                    if DRAG_ASPECT_RATIO == 16/9:
                        ratio_text = "16:9"
                    elif DRAG_ASPECT_RATIO == 4/3:
                        ratio_text = "4:3"
                    status_text = f"{ratio_text} | " + status_text
                    bg_color = "#ff6775"  # 연한 빨간색
                else:
                    if is_square_key_pressed:
                        status_text = f"정사각형 | " + status_text
                        bg_color = "#ffad57"  # 연한 주황색
                    elif is_width_key_pressed:
                        status_text = f"너비 고정 | " + status_text
                        bg_color = "#6eb5ff"  # 연한 파란색
                    elif is_height_key_pressed:
                        status_text = f"높이 고정 | " + status_text
                        bg_color = "#4dff78"  # 연한 녹색
                    else:
                        bg_color = "#0cffcc"
                
                self.zoom_window.update_status(status_text, bg_color)
    
    # def update_size_label(self, width, height):
    #     """크기 정보 업데이트"""
    #     self.size_label.setText(f"{int(width)} × {int(height)} 픽셀")
    #     self.size_label.adjustSize()
        
    #     # 상단에 표시
    #     self.size_label.move(10, 50)
    
    def mousePressEvent(self, event):
        """마우스 버튼 누를 때"""
        if event.button() == Qt.LeftButton:
            # 드래그 시작할 때 커서 변경
            self.setCursor(Qt.ClosedHandCursor)  # 주먹 모양 커서
        
            x = int(event.position().x())
            y = int(event.position().y())
            
            self.dragging = True
            self.start_point = QPoint(x, y)
            self.current_point = QPoint(x, y)
            self.update()
    
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if not self.dragging or not self.start_point:
            return
        
        # 좌표 가져오기
        current_x = int(event.position().x())
        current_y = int(event.position().y())
        
        # 키보드 상태 확인
        is_square_key_pressed = keyboard.is_pressed(DRAG_KEEP_SQUARE_KEY)
        is_width_key_pressed = keyboard.is_pressed(DRAG_FIXED_WIDTH_KEY)
        is_height_key_pressed = keyboard.is_pressed(DRAG_FIXED_HEIGHT_KEY)
        is_ratio_key_pressed = keyboard.is_pressed(DRAG_ASPECT_RATIO_KEY)
        
        # 첫 드래그 시 고정 치수 설정
        if self.fixed_width is None and is_width_key_pressed:
            self.fixed_width = abs(current_x - self.start_point.x())
        
        if self.fixed_height is None and is_height_key_pressed:
            self.fixed_height = abs(current_y - self.start_point.y())
        
        # 키 상태에 따라 좌표 조정
        if is_ratio_key_pressed:
            # 특정 비율 유지 (16:9 등)
            width = abs(current_x - self.start_point.x())
            height = width / DRAG_ASPECT_RATIO
            
            if current_y >= self.start_point.y():
                current_y = self.start_point.y() + height
            else:
                current_y = self.start_point.y() - height
        else:
            if is_square_key_pressed:
                # 정사각형 유지
                size = max(abs(current_x - self.start_point.x()), abs(current_y - self.start_point.y()))
                if current_x >= self.start_point.x():
                    current_x = self.start_point.x() + size
                else:
                    current_x = self.start_point.x() - size
                    
                if current_y >= self.start_point.y():
                    current_y = self.start_point.y() + size
                else:
                    current_y = self.start_point.y() - size
            
            elif is_width_key_pressed and self.fixed_width is not None:
                # 너비 고정
                if current_x >= self.start_point.x():
                    current_x = self.start_point.x() + self.fixed_width
                else:
                    current_x = self.start_point.x() - self.fixed_width
            
            elif is_height_key_pressed and self.fixed_height is not None:
                # 높이 고정
                if current_y >= self.start_point.y():
                    current_y = self.start_point.y() + self.fixed_height
                else:
                    current_y = self.start_point.y() - self.fixed_height
        
        # 현재 위치 업데이트
        self.current_point = QPoint(current_x, current_y)
        self.update()
    
    def mouseReleaseEvent(self, event):
        """마우스 버튼 놓을 때"""
        if not self.dragging or event.button() != Qt.LeftButton:
            return
        
        # 드래그 끝날 때 다시 십자 커서로 변경
        self.setCursor(Qt.CrossCursor)
        
        self.dragging = False
        
        # 최종 좌표 조정 (키 상태에 따라)
        is_square_key_pressed = keyboard.is_pressed(DRAG_KEEP_SQUARE_KEY)
        is_width_key_pressed = keyboard.is_pressed(DRAG_FIXED_WIDTH_KEY)
        is_height_key_pressed = keyboard.is_pressed(DRAG_FIXED_HEIGHT_KEY)
        is_ratio_key_pressed = keyboard.is_pressed(DRAG_ASPECT_RATIO_KEY)
        
        current_x = int(event.position().x())
        current_y = int(event.position().y())
        
        # 키 상태 관련 조정은 mouseMoveEvent와 동일
        if is_ratio_key_pressed:
            # 특정 비율 유지 (16:9 등)
            width = abs(current_x - self.start_point.x())
            height = width / DRAG_ASPECT_RATIO
            
            if current_y >= self.start_point.y():
                current_y = self.start_point.y() + height
            else:
                current_y = self.start_point.y() - height
        else:
            if is_square_key_pressed:
                size = max(abs(current_x - self.start_point.x()), abs(current_y - self.start_point.y()))
                if current_x >= self.start_point.x():
                    current_x = self.start_point.x() + size
                else:
                    current_x = self.start_point.x() - size
                    
                if current_y >= self.start_point.y():
                    current_y = self.start_point.y() + size
                else:
                    current_y = self.start_point.y() - size
                    
            elif is_width_key_pressed and self.fixed_width is not None:
                # 너비 고정
                if current_x >= self.start_point.x():
                    current_x = self.start_point.x() + self.fixed_width
                else:
                    current_x = self.start_point.x() - self.fixed_width
            
            elif is_height_key_pressed and self.fixed_height is not None:
                # 높이 고정
                if current_y >= self.start_point.y():
                    current_y = self.start_point.y() + self.fixed_height
                else:
                    current_y = self.start_point.y() - self.fixed_height
        
        # 다른 비율 조정 코드도 동일...
        
        # 최종 위치 업데이트
        self.current_point = QPoint(current_x, current_y)
        
        # 좌표 정규화
        x1 = min(self.start_point.x(), self.current_point.x())
        y1 = min(self.start_point.y(), self.current_point.y())
        x2 = max(self.start_point.x(), self.current_point.x())
        y2 = max(self.start_point.y(), self.current_point.y())
        
        width = x2 - x1
        height = y2 - y1
        
        # 창 기준 상대 좌표로 변환
        if self.target_window_only and WindowUtil and WindowUtil.is_window_valid():
            # 이미 타겟 윈도우 기준 좌표
            rel_x1, rel_y1, rel_x2, rel_y2 = x1, y1, x2, y2
            left, top, _, _ = self.window_rect
            abs_x1, abs_y1 = x1 + left, y1 + top
            abs_x2, abs_y2 = x2 + left, y2 + top
        else:
            # 화면 기준 절대 좌표
            abs_x1, abs_y1, abs_x2, abs_y2 = x1, y1, x2, y2
            
            # 창 기준 상대 좌표로 변환
            if WindowUtil and WindowUtil.is_window_valid():
                left, top, _, _ = WindowUtil.get_window_rect()
                rel_x1, rel_y1 = abs_x1 - left, abs_y1 - top
                rel_x2, rel_y2 = abs_x2 - left, abs_y2 - top
            else:
                rel_x1, rel_y1, rel_x2, rel_y2 = abs_x1, abs_y1, abs_x2, abs_y2
        
        # 선택된 영역 정보 저장
        self.selected_region = {
            "abs": (abs_x1, abs_y1, abs_x2, abs_y2),  # 절대 좌표 (화면 기준)
            "rel": (rel_x1, rel_y1, rel_x2, rel_y2),  # 상대 좌표 (창 기준)
            "width": width,
            "height": height
        }
        
        # 확대 창 닫기
        if hasattr(self, 'zoom_window') and self.zoom_window:
            self.zoom_window.close()
            self.zoom_window = None
        
        # 마우스 추적 타이머 종료
        if hasattr(self, 'mouse_timer') and self.mouse_timer:
            self.mouse_timer.stop()
        
        # 영역 선택 완료 신호 발생
        self.region_selected.emit(self.selected_region)
        
        # 다이얼로그 종료
        self.accept()
    
    def keyPressEvent(self, event):
        """키 이벤트 처리"""
        if event.key() == Qt.Key_Escape:
            # 확대 창 닫기
            if hasattr(self, 'zoom_window') and self.zoom_window:
                self.zoom_window.close()
                self.zoom_window = None
            
            # 마우스 추적 타이머 종료
            if hasattr(self, 'mouse_timer') and self.mouse_timer:
                self.mouse_timer.stop()
            
            # 취소 시 신호 발생 (None을 전달)
            self.region_selected.emit(None)
            self.reject()  # 취소하고 닫기
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        # print("RegionSelectorDialog.closeEvent()")
        
        """창이 닫힐 때 이벤트"""
        # 확대 창 닫기
        if hasattr(self, 'zoom_window') and self.zoom_window:
            self.zoom_window.close()
            self.zoom_window = None
        
        # 마우스 추적 타이머 종료
        if hasattr(self, 'mouse_timer') and self.mouse_timer:
            self.mouse_timer.stop()
            
        super().closeEvent(event)


class RegionSelector:
    """RegionSelectorDialog를 사용하는 래퍼 클래스"""
    def __init__(self, parent=None):
        self.parent = parent
        self.dialog = None
        self.callback = None
        self.selected_region = None
    
    def start_selection(self, callback=None, target_window_only=False):
        """영역 선택 시작"""
        self.callback = callback
        self.selected_region = None
        
        # 새 다이얼로그 생성
        self.dialog = RegionSelectorDialog(self.parent, target_window_only)
        
        # 결과 처리를 위한 시그널 연결
        self.dialog.region_selected.connect(self._on_region_selected)
        
        # 다이얼로그 표시 (exec 대신 show 사용)
        self.dialog.show()
        
        # 콜백이 없는 경우 바로 결과 리턴
        if not callback:
            return self.selected_region
    
    def _on_region_selected(self, region):
        """영역 선택 결과 처리 (내부용)"""
        self.selected_region = region
        
        # 다이얼로그 참조 정리
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog = None
        
        # 콜백이 설정되어 있으면 호출
        if self.callback:
            self.callback(region)