# from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
#                              QLineEdit, QPushButton, QCheckBox, QMessageBox, QSizePolicy)
# from PySide6.QtCore import Qt, Signal, QSize
# from PySide6.QtGui import QPixmap, QPainter

# import time
# from PIL import Image, ImageQt

# from zzz.config import *
# import core.sanner as Scanner
# from core.window_utils import WindowUtil

# class CaptureAreaFrame(QFrame):
#     """캡처 영역 설정 프레임"""
    
#     def __init__(self, parent, region_selector, capture_manager, status_signal):
#         super().__init__(parent)
        
#         self.region_selector = region_selector
#         self.capture_manager = capture_manager
#         self.status_signal = status_signal
        
#         # 미리보기 이미지 저장 변수
#         self.preview_image = None
#         self.preview_pixmap = None
        
#         self._setup_ui()
    
#     def _setup_ui(self):
#         """UI 구성요소 초기화"""
#         # 메인 레이아웃
#         main_layout = QVBoxLayout(self)
#         self.setLayout(main_layout)
#         self.setFrameStyle(QFrame.Box | QFrame.Raised)
        
#         # 타이틀 설정
#         title_label = QLabel("캡처 영역 설정 (창 내부 좌표)")
#         title_label.setStyleSheet("font-weight: bold;")
#         main_layout.addWidget(title_label)
        
#         # 왼쪽(설정) 및 오른쪽(미리보기) 영역을 나누기 위한 프레임
#         content_layout = QHBoxLayout()
#         main_layout.addLayout(content_layout)
        
#         # 좌측 입력 프레임
#         input_frame = QFrame()
#         input_layout = QGridLayout(input_frame)
#         content_layout.addWidget(input_frame)
        
#         # X 좌표 (상대적)
#         input_layout.addWidget(QLabel("X 좌표:"), 0, 0, Qt.AlignLeft)
#         self.x_edit = QLineEdit(str(DEFAULT_CAPTURE_X))
#         self.x_edit.setFixedWidth(80)
#         input_layout.addWidget(self.x_edit, 0, 1, Qt.AlignLeft)
        
#         # Y 좌표 (상대적)
#         input_layout.addWidget(QLabel("Y 좌표:"), 0, 2, Qt.AlignLeft)
#         self.y_edit = QLineEdit(str(DEFAULT_CAPTURE_Y))
#         self.y_edit.setFixedWidth(80)
#         input_layout.addWidget(self.y_edit, 0, 3, Qt.AlignLeft)
        
#         # 너비
#         input_layout.addWidget(QLabel("너비:"), 1, 0, Qt.AlignLeft)
#         self.width_edit = QLineEdit(str(DEFAULT_CAPTURE_WIDTH))
#         self.width_edit.setFixedWidth(80)
#         input_layout.addWidget(self.width_edit, 1, 1, Qt.AlignLeft)
        
#         # 높이
#         input_layout.addWidget(QLabel("높이:"), 1, 2, Qt.AlignLeft)
#         self.height_edit = QLineEdit(str(DEFAULT_CAPTURE_HEIGHT))
#         self.height_edit.setFixedWidth(80)
#         input_layout.addWidget(self.height_edit, 1, 3, Qt.AlignLeft)
        
#         # 캡처 간격 설정
#         input_layout.addWidget(QLabel("캡처 간격(초):"), 2, 0, Qt.AlignLeft)
#         self.interval_edit = QLineEdit(str(Scanner.Loop_Interval))
#         self.interval_edit.setFixedWidth(80)
#         input_layout.addWidget(self.interval_edit, 2, 1, Qt.AlignLeft)
        
#         # 버튼 프레임
#         button_layout = QHBoxLayout()
#         input_layout.addLayout(button_layout, 3, 0, 1, 4)
        
#         # 영역 선택 버튼 (드래그로 영역 선택)
#         select_area_btn = QPushButton("드래그로 영역 선택")
#         select_area_btn.clicked.connect(self.select_capture_area)
#         button_layout.addWidget(select_area_btn)
        
#         # 캡처 미리보기 업데이트 버튼
#         preview_btn = QPushButton("미리보기 갱신")
#         preview_btn.clicked.connect(self.update_area_preview)
#         button_layout.addWidget(preview_btn)
        
#         # 창 내 영역만 선택 체크박스
#         self.window_only_check = QCheckBox("창 내부만 선택")
#         self.window_only_check.setChecked(True)
#         input_layout.addWidget(self.window_only_check, 4, 0, 1, 4, Qt.AlignLeft)
        
#         # 우측 미리보기 프레임
#         preview_frame = QFrame()
#         preview_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
#         preview_layout = QVBoxLayout(preview_frame)
#         content_layout.addWidget(preview_frame, 1)  # 미리보기가 더 많은 공간을 차지하도록
        
#         # 미리보기 제목
#         preview_title = QLabel("영역 미리보기")
#         preview_title.setAlignment(Qt.AlignCenter)
#         preview_layout.addWidget(preview_title)
        
#         # 미리보기 레이블 (이미지 표시용)
#         self.preview_label = QLabel()
#         self.preview_label.setMinimumSize(200, 150)
#         self.preview_label.setAlignment(Qt.AlignCenter)
#         self.preview_label.setStyleSheet("background-color: lightgray;")
#         self.preview_label.setText("영역을 선택하면\n미리보기가 표시됩니다")
#         preview_layout.addWidget(self.preview_label, 1)
        
#         # 미리보기 정보 레이블
#         self.info_label = QLabel()
#         self.info_label.setAlignment(Qt.AlignCenter)
#         self.info_label.setStyleSheet("color: navy; font-size: 8pt;")
#         preview_layout.addWidget(self.info_label)
    
#     def select_capture_area(self):
#         """드래그로 캡처 영역 선택"""
#         # 창이 연결되어 있고 '창 내부만 선택' 옵션이 활성화된 경우에만 창 내부로 제한
#         target_window_only = self.window_only_check.isChecked() and WindowUtil.is_window_valid()
        
#         if target_window_only and not WindowUtil.is_window_valid():
#             QMessageBox.critical(self, "오류", "창 내부 선택을 위해서는 먼저 창에 연결해주세요.")
#             return
        
#         # 선택 임시 중단을 알림
#         self.status_signal.emit("영역 선택 중... (ESC 키를 누르면 취소)")
        
#         # 창 최소화 (선택 화면이 가려지지 않도록)
#         self.window().showMinimized()
#         time.sleep(0.5)  # 창이 최소화될 시간 확보
        
#         # 영역 선택 시작
#         self.region_selector.start_selection(
#             callback=self.handle_region_selection,
#             target_window_only=target_window_only
#         )
        
#         # 창 복원
#         self.window().showNormal()
    
#     def handle_region_selection(self, region_info):
#         """영역 선택 결과 처리"""
#         if not region_info:
#             self.status_signal.emit("영역 선택이 취소되었습니다.")
#             return
        
#         # 선택된 영역 정보를 UI에 업데이트
#         rel_x1, rel_y1, rel_x2, rel_y2 = region_info["rel"]
#         width = region_info["width"]
#         height = region_info["height"]
        
#         self.x_edit.setText(str(rel_x1))
#         self.y_edit.setText(str(rel_y1))
#         self.width_edit.setText(str(width))
#         self.height_edit.setText(str(height))
        
#         self.status_signal.emit(f"영역이 선택되었습니다: X={rel_x1}, Y={rel_y1}, 너비={width}, 높이={height}")
        
#         # 선택 후 미리보기 업데이트
#         self.update_area_preview()
    
#     def update_area_preview(self):
#         """캡처 영역 미리보기 업데이트"""
#         try:
#             # 창이 연결되어 있는지 확인
#             if not WindowUtil.is_window_valid():
#                 QMessageBox.critical(self, "오류", ERROR_NO_WINDOW)
#                 return
            
#             # 캡처 영역 좌표 가져오기
#             try:
#                 x = int(self.x_edit.text())
#                 y = int(self.y_edit.text())
#                 width = int(self.width_edit.text())
#                 height = int(self.height_edit.text())
                
#                 if width <= 0 or height <= 0:
#                     raise ValueError("너비와 높이는 양수여야 합니다.")
#             except ValueError as e:
#                 QMessageBox.critical(self, "입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
#                 return
            
#             # 전체 창 캡처
#             full_window_img = self.capture_manager.capture_full_window()
#             if not full_window_img:
#                 QMessageBox.critical(self, "오류", "창 캡처에 실패했습니다.")
#                 return
            
#             # 캡처 영역 추출
#             try:
#                 # PIL 이미지에서 영역 추출
#                 crop_region = (x, y, x + width, y + height)
                
#                 # 영역이 이미지 범위를 벗어나는지 확인
#                 img_width, img_height = full_window_img.size
#                 if crop_region[0] < 0 or crop_region[1] < 0 or crop_region[2] > img_width or crop_region[3] > img_height:
#                     QMessageBox.warning(
#                         self, 
#                         "영역 경고", 
#                         "설정한 영역이 창 범위를 벗어납니다. 일부만 표시됩니다."
#                     )
                
#                 # 캔버스 크기 가져오기
#                 preview_width = self.preview_label.width()
#                 preview_height = self.preview_label.height()
                
#                 # 이미지 크기 계산에 너무 작은 값이 사용되지 않도록 제한
#                 if preview_width < 50:
#                     preview_width = 200
#                 if preview_height < 50:
#                     preview_height = 150
                    
#                 # 영역 자르기
#                 cropped_img = full_window_img.crop((
#                     max(0, crop_region[0]),
#                     max(0, crop_region[1]),
#                     min(img_width, crop_region[2]),
#                     min(img_height, crop_region[3])
#                 ))
                
#                 # 캔버스에 맞게 이미지 크기 조정 (비율 유지)
#                 img_width, img_height = cropped_img.size
                
#                 # 비율 계산
#                 width_ratio = preview_width / img_width
#                 height_ratio = preview_height / img_height
#                 scale_ratio = min(width_ratio, height_ratio)
                
#                 # 이미지가 너무 크면 축소
#                 if scale_ratio < 1:
#                     new_width = int(img_width * scale_ratio)
#                     new_height = int(img_height * scale_ratio)
#                     resized_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)
#                 else:
#                     resized_img = cropped_img
                
#                 # PIL 이미지를 QPixmap으로 변환
#                 self.preview_image = resized_img
#                 q_image = ImageQt.ImageQt(resized_img)
#                 self.preview_pixmap = QPixmap.fromImage(q_image)
                
#                 # 미리보기 레이블에 이미지 표시
#                 self.preview_label.setPixmap(self.preview_pixmap)
#                 self.preview_label.setAlignment(Qt.AlignCenter)
                
#                 # 미리보기 정보 표시
#                 info_text = f"{width}x{height} 픽셀"
#                 self.info_label.setText(info_text)
                
#                 self.status_signal.emit("영역 미리보기가 업데이트되었습니다.")
            
#             except Exception as e:
#                 QMessageBox.critical(self, "미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
#         except Exception as e:
#             QMessageBox.critical(self, "미리보기 오류", f"미리보기 생성 중 오류: {str(e)}")
    
#     def get_capture_info(self):
#         """캡처 정보 가져오기"""
#         try:
#             x = int(self.x_edit.text())
#             y = int(self.y_edit.text())
#             width = int(self.width_edit.text())
#             height = int(self.height_edit.text())
#             interval = float(self.interval_edit.text())
            
#             if width <= 0 or height <= 0 or interval <= 0:
#                 raise ValueError("너비, 높이, 간격은 양수여야 합니다.")
                
#             return (x, y, width, height, interval)
#         except ValueError as e:
#             QMessageBox.critical(self, "입력 오류", f"올바른 값을 입력해주세요: {str(e)}")
#             return None