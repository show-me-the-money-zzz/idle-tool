from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                              QPushButton, QGroupBox, QListWidget,
                              QInputDialog, QMessageBox, QLabel, QWidget,
                              QSplitter, QLineEdit,
                             )
from PySide6.QtCore import Qt

import ui.css as CSS
import grinder_utils.system as SYS_UTIL

class NotiEditor(QDialog):
   def __init__(self, parent):
      super().__init__(parent)
      self.setWindowTitle("알림 에디터")
      self.resize(720, 640)

      # 알림 목록 데이터 (실제 애플리케이션에서는 외부에서 로드할 수 있음)
      self.notification_list = [
         "작업 완료 알림",
         "오류 발생 알림",
         "시스템 상태 알림"
      ]

      self._setup_ui()

   def _setup_ui(self):
      main_layout = QVBoxLayout(self)

      # 상단 제목 라벨
      title_label = QLabel("알림 설정 목록")
      title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
      main_layout.addWidget(title_label)

      # 목록 및 편집 영역을 위한 스플리터 추가
      splitter = QSplitter(Qt.Horizontal)
      main_layout.addWidget(splitter, 1)  # 1은 stretch 비율

      # 목록 그룹
      self._setup_group_list(splitter)

      # 편집 그룹 (선택된 알림 설정 편집용, 필요시 구현)
      edit_group = QGroupBox("알림 설정 편집")
      edit_layout = QVBoxLayout(edit_group)
      edit_layout.addWidget(QLabel("선택한 알림 설정을 편집하세요."))
      edit_layout.addStretch(1)
      splitter.addWidget(edit_group)

      # 스플리터 비율 설정 (1:2)
      splitter.setSizes([250, 500])

      # 최하단 - 버튼 영역
      buttons_layout = QHBoxLayout()
      
      # 왼쪽에 취소 버튼 배치
      self.cancel_btn = QPushButton("닫기")
      self.cancel_btn.setStyleSheet(CSS.BUTTON_CANCEL)
      self.cancel_btn.clicked.connect(self.Close_Editor)
      buttons_layout.addWidget(self.cancel_btn)

      # 오른쪽 버튼들을 위한 공간 추가
      buttons_layout.addStretch(1)

      # 오른쪽에 저장 버튼 추가
      self.save_btn = QPushButton("저장")
      self.save_btn.setStyleSheet(CSS.BUTTON_APPLY_GREEN)
      self.save_btn.clicked.connect(self.save_notifications)
      buttons_layout.addWidget(self.save_btn)

      # buttons_layout.addStretch(1)

      main_layout.addLayout(buttons_layout)

   def _setup_group_list(self, parent):
      """알림 목록 그룹 설정"""
      list_group = QGroupBox("알림 목록")
      list_layout = QVBoxLayout(list_group)

      # 목록 위젯
      self.noti_list = QListWidget()
      # self.noti_list.setStyleSheet("""
      #    QListWidget {
      #          border: 1px solid #cccccc;
      #          border-radius: 4px;
      #          background-color: #ffffff;
      #          font-size: 14px;
      #    }
      #    QListWidget::item {
      #          padding: 6px;
      #          border-bottom: 1px solid #eeeeee;
      #    }
      #    QListWidget::item:selected {
      #          background-color: #e0f0ff;
      #          color: #333333;
      #    }
      # """)
      
      # 초기 항목 추가
      for item in self.notification_list:
         self.noti_list.addItem(item)
         
      # 항목 선택 시 이벤트 처리 (필요시 구현)
      self.noti_list.itemSelectionChanged.connect(self.on_item_selection_changed)
      
      list_layout.addWidget(self.noti_list)
      
      # 버튼 영역
      button_layout = QHBoxLayout()
      
      # 추가 버튼
      self.add_btn = QPushButton("✚")
      self.add_btn.setToolTip("알림 설정 추가")
      self.add_btn.setFixedSize(30, 30)
      # self.add_btn.setStyleSheet("""
      #    QPushButton {
      #          background-color: #4CAF50;
      #          color: white;
      #          font-weight: bold;
      #          border: none;
      #          border-radius: 4px;
      #    }
      #    QPushButton:hover {
      #          background-color: #45a049;
      #    }
      # """)
      self.add_btn.clicked.connect(self.add_notification)
      button_layout.addWidget(self.add_btn)
      
      # 삭제 버튼
      self.del_btn = QPushButton("━")
      self.del_btn.setToolTip("선택한 알림 설정 삭제")
      self.del_btn.setFixedSize(30, 30)
      # self.del_btn.setStyleSheet("""
      #    QPushButton {
      #          background-color: #f44336;
      #          color: white;
      #          font-weight: bold;
      #          border: none;
      #          border-radius: 4px;
      #    }
      #    QPushButton:hover {
      #          background-color: #e53935;
      #    }
      # """)
      self.del_btn.clicked.connect(self.delete_notification)
      button_layout.addWidget(self.del_btn)
      
      # 버튼 영역 오른쪽에 여백 추가
      button_layout.addStretch(1)
      
      # 수정 버튼 추가
      self.edit_btn = QPushButton("수정")
      self.edit_btn.setToolTip("선택한 알림 설정 수정")
      self.edit_btn.setFixedWidth(60)
      # self.edit_btn.setStyleSheet("""
      #    QPushButton {
      #          background-color: #2196F3;
      #          color: white;
      #          font-weight: bold;
      #          border: none;
      #          border-radius: 4px;
      #          padding: 5px;
      #    }
      #    QPushButton:hover {
      #          background-color: #1E88E5;
      #    }
      # """)
      self.edit_btn.clicked.connect(self.edit_notification)
      button_layout.addWidget(self.edit_btn)
      self.edit_btn.setVisible(False)
      
      list_layout.addLayout(button_layout)
      
      # 초기 버튼 상태 설정 (삭제 및 수정 버튼은 항목이 선택되었을 때만 활성화)
      self.update_button_states()
      
      parent.addWidget(list_group)
   
   def update_button_states(self):
      """버튼 활성화 상태 업데이트"""
      has_selection = len(self.noti_list.selectedItems()) > 0
      self.del_btn.setEnabled(has_selection)
      # self.edit_btn.setEnabled(has_selection)
   
   def on_item_selection_changed(self):
      """항목 선택 변경 시 처리"""
      self.update_button_states()
      
      # 여기에 선택된 항목의 세부 정보를 표시하는 코드 추가 가능
   
   def add_notification(self):
      """새 알림 설정 추가"""

      text, ok = QInputDialog.getText(self,
                                      "알림 추가", "알림 설정 이름:",
                                      QLineEdit.Normal, "새 알림 1")
      if ok and text:
         key = SYS_UTIL.GetKey({"noti"})
         # print(key)

         # 중복 검사
         items = [self.noti_list.item(i).text() for i in range(self.noti_list.count())]
         if text in items:
               QMessageBox.warning(self, "중복 항목", "이미 존재하는 알림 설정 이름입니다.")
               return
               
         # 목록에 추가
         self.noti_list.addItem(text, key)
         
         # 새 항목 선택
         for i in range(self.noti_list.count()):
               if self.noti_list.item(i).text() == text:
                  self.noti_list.setCurrentRow(i)
                  break
   
   def delete_notification(self):
      """선택한 알림 설정 삭제"""
      current_row = self.noti_list.currentRow()
      if current_row >= 0:
         item = self.noti_list.item(current_row)
         
         # 확인 메시지
         reply = QMessageBox.question(self, "알림 삭제", 
                                       f"'{item.text()}' 알림 설정을 삭제하시겠습니까?",
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
         
         if reply == QMessageBox.Yes:
               # 목록에서 제거
               self.noti_list.takeItem(current_row)
               
               # 버튼 상태 업데이트
               self.update_button_states()
   
   def edit_notification(self):
      """선택한 알림 설정 수정"""
      current_row = self.noti_list.currentRow()
      if current_row >= 0:
         item = self.noti_list.item(current_row)
         current_text = item.text()
         
         text, ok = QInputDialog.getText(self, "알림 수정", 
                                          "알림 설정 이름:", 
                                          text=current_text)
         
         if ok and text and text != current_text:
               # 중복 검사 (현재 항목 제외)
               items = [self.noti_list.item(i).text() for i in range(self.noti_list.count()) 
                     if i != current_row]
               if text in items:
                  QMessageBox.warning(self, "중복 항목", "이미 존재하는 알림 설정 이름입니다.")
                  return
               
               # 항목 텍스트 업데이트
               item.setText(text)
   
   def save_notifications(self):
      """알림 설정 저장"""
      # 현재 목록의 모든 항목을 가져옴
      notifications = [self.noti_list.item(i).text() for i in range(self.noti_list.count())]
      
      # 여기에 저장 로직 추가 (파일, 데이터베이스 등)
      self.notification_list = notifications
      
      QMessageBox.information(self, "저장 완료", "알림 설정이 저장되었습니다.")

   def Close_Editor(self):
      """에디터 닫기"""
      # 변경 사항이 있는지 확인
      current_notifications = [self.noti_list.item(i).text() for i in range(self.noti_list.count())]
      if current_notifications != self.notification_list:
         reply = QMessageBox.question(self, "변경 사항 저장", 
                                       "변경 사항을 저장하시겠습니까?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                                       QMessageBox.Yes)
         
         if reply == QMessageBox.Yes:
               self.save_notifications()
               self.close()
         elif reply == QMessageBox.No:
               self.close()
         # Cancel은 아무것도 하지 않음
      else:
         self.close()
