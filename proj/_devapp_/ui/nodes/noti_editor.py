from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                              QPushButton, QGroupBox, QListWidget, QListWidgetItem,
                              QInputDialog, QMessageBox, QLabel, QWidget,
                              QSplitter, QLineEdit, QFormLayout, QComboBox,
                              QSpinBox, QCheckBox, QTabWidget, QScrollArea,
                              QTextEdit, QFrame,
                             )
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon

import ui.css as CSS
import grinder_utils.system as SYS_UTIL
from grinder_types.noti_item import BaseNotiItem, TelegramNoti, DiscordNoti
import stores.noti_store as NotiStore
import stores.areas as AreasStore
from ui.component.searchable_comboBox import SearchableComboBox

class NotiEditor(QDialog):
   def __init__(self, parent):
      super().__init__(parent)
      self.setWindowTitle("알리미 에디터")
      self.resize(720, 570)

      # 알림 목록 데이터 (실제 애플리케이션에서는 외부에서 로드할 수 있음)
      self.notification_list = [
         # "작업 완료 알림",
         # "오류 발생 알림",
         # "시스템 상태 알림"
      ]

      # 알림 아이템 저장 딕셔너리
      self.noti_items = {}
      
      # 현재 편집 중인 알림 아이템
      self.current_noti_item = None
      self.current_noti_key = None

      self._setup_ui()

      self.Reload_Data()

   def _setup_ui(self):
      main_layout = QVBoxLayout(self)

      # 상단 제목 라벨
      title_label = QLabel("알림 설정 목록")
      title_label.setStyleSheet(
         "font-size: 16px; font-weight: bold; margin-bottom: 10px;"
      )
      main_layout.addWidget(title_label)

      # 목록 및 편집 영역을 위한 스플리터 추가
      splitter = QSplitter(Qt.Horizontal)
      main_layout.addWidget(splitter, 1)  # 1은 stretch 비율

      # 목록 그룹
      self._setup_group_list(splitter)

      # 편집 그룹 (선택된 알림 설정 편집용)
      self.edit_group = QGroupBox("알림 설정 편집")
      self._setup_edit_panel()
      splitter.addWidget(self.edit_group)

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

      main_layout.addLayout(buttons_layout)

   def Reload_Data(self):
      self.noti_list.clear()
      
      self.noti_items.clear()
      for k, v in NotiStore.GetAll_Notis().items():
         notiitem = NotiStore.Get_Noti(k)
         if notiitem:
            self.noti_items[k] = notiitem
            
            item = QListWidgetItem(notiitem.name)
            item.setData(Qt.UserRole, k)
            self.noti_list.addItem(item)
            
            # if isinstance(v, TelegramNoti):
            #    from typing import cast
            #    tele = cast(TelegramNoti, v)
            
      self.zone_combobox.clear()
      self.zone_combobox.addItem("")
      for k in AreasStore.GetAll_ZoneAreas().keys():
         zone = AreasStore.Get_ZoneArea(k)
         if zone:
            self.zone_combobox.addItem(zone.name)
   
   def _setup_group_list(self, parent):
      """알림 목록 그룹 설정"""
      list_group = QGroupBox("알림 목록")
      list_layout = QVBoxLayout(list_group)

      # 목록 위젯
      self.noti_list = QListWidget()

      # 초기 항목 추가
      for item in self.notification_list:
         self.noti_list.addItem(item)

      # 항목 선택 시 이벤트 처리
      self.noti_list.itemSelectionChanged.connect(self.on_item_selection_changed)

      list_layout.addWidget(self.noti_list)

      # 버튼 영역
      button_layout = QHBoxLayout()

      # 추가 버튼
      self.add_btn = QPushButton("✚")
      self.add_btn.setToolTip("알림 설정 추가")
      self.add_btn.setFixedSize(30, 30)
      self.add_btn.clicked.connect(self.add_notification)
      button_layout.addWidget(self.add_btn)

      # 삭제 버튼
      self.del_btn = QPushButton("━")
      self.del_btn.setToolTip("선택한 알림 설정 삭제")
      self.del_btn.setFixedSize(30, 30)
      self.del_btn.clicked.connect(self.delete_notification)
      button_layout.addWidget(self.del_btn)

      # 버튼 영역 오른쪽에 여백 추가
      button_layout.addStretch(1)

      # 수정 버튼 추가
      self.edit_btn = QPushButton("수정")
      self.edit_btn.setToolTip("선택한 알림 설정 수정")
      self.edit_btn.setFixedWidth(60)
      self.edit_btn.clicked.connect(self.edit_notification)
      button_layout.addWidget(self.edit_btn)
      self.edit_btn.setVisible(False)

      list_layout.addLayout(button_layout)

      # 초기 버튼 상태 설정 (삭제 및 수정 버튼은 항목이 선택되었을 때만 활성화)
      self.update_button_states()

      parent.addWidget(list_group)

   def _setup_edit_panel(self):
      """알림 설정 편집 패널 설정"""
      edit_layout = QVBoxLayout(self.edit_group)

      # 스크롤 영역 생성
      scroll_area = QScrollArea()
      scroll_area.setWidgetResizable(True)
      scroll_area.setFrameShape(QScrollArea.NoFrame)

      # 스크롤 영역에 들어갈 위젯
      scroll_content = QWidget()
      self.form_layout = QFormLayout(scroll_content)
      self.form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

      # 알림 이름 입력
      self.name_edit = QLineEdit()
      self.form_layout.addRow("알림 이름:", self.name_edit)

      # 알림 유형 선택
      self.type_combo = QComboBox()
      self.type_combo.addItems(
         [
               "Discord",
               "Telegram",
         ]
      )
      self.type_combo.currentIndexChanged.connect(self.on_type_changed)
      self.form_layout.addRow("알림 유형:", self.type_combo)

      # 메시지 제목
      self.title_edit = QLineEdit()
      self.form_layout.addRow("메시지 제목:", self.title_edit)

      # 계정 서버
      self.server_edit = QLineEdit()
      self.form_layout.addRow("계정 서버:", self.server_edit)

      # 계정 닉네임
      self.nickname_edit = QLineEdit()
      self.form_layout.addRow("계정 닉네임:", self.nickname_edit)

      # 메시지 내용
      self.comment_edit = QTextEdit()
      self.comment_edit.setMinimumHeight(80)
      self.form_layout.addRow("메시지 내용:", self.comment_edit)

      # 영역 선택
      self.zone_combobox = SearchableComboBox(items=[])
      self.form_layout.addRow("영역:", self.zone_combobox)

      # 반복 주기
      self.repeat_spin = QSpinBox()
      self.repeat_spin.setMinimum(10)
      self.repeat_spin.setMaximum(1440)  # 24시간 (분 단위)
      self.repeat_spin.setValue(60)
      self.repeat_spin.setSingleStep(10)
      self.repeat_spin.setSuffix(" 분")
      self.form_layout.addRow("반복 주기:", self.repeat_spin)

      # 사용 여부
      self.enable_check = QCheckBox("사용")
      self.enable_check.setChecked(True)
      self.form_layout.addRow("사용 여부:", self.enable_check)

      # 구분선
      separator = QFrame()
      separator.setFrameShape(QFrame.HLine)
      separator.setFrameShadow(QFrame.Sunken)
      self.form_layout.addRow(separator)

      # Discord 설정 (기본 표시)
      self.discord_widget = QWidget()
      discord_layout = QFormLayout(self.discord_widget)

      self.webhooks_edit = QLineEdit()
      discord_layout.addRow("Webhook URL:", self.webhooks_edit)

      self.form_layout.addRow(self.discord_widget)

      # Telegram 설정 (기본 숨김)
      self.telegram_widget = QWidget()
      telegram_layout = QFormLayout(self.telegram_widget)

      self.token_edit = QLineEdit()
      telegram_layout.addRow("API 토큰:", self.token_edit)

      self.chatid_edit = QLineEdit()
      telegram_layout.addRow("채팅 ID:", self.chatid_edit)

      self.baseurl_edit = QLineEdit("https://api.telegram.org/bot")
      telegram_layout.addRow("기본 URL:", self.baseurl_edit)

      self.form_layout.addRow(self.telegram_widget)
      self.telegram_widget.setVisible(False)

      # 스크롤 영역에 폼 추가
      scroll_area.setWidget(scroll_content)
      edit_layout.addWidget(scroll_area)

      # 상태 메시지
      self.status_label = QLabel("알림 설정을 편집하거나 새 알림을 추가하세요.")
      self.status_label.setStyleSheet("color: #666666; font-style: italic;")
      edit_layout.addWidget(self.status_label)

      # 모든 입력 필드 비활성화 (초기 상태)
      self.set_form_enabled(False)

   def set_form_enabled(self, enabled):
      """폼 필드 활성화/비활성화"""
      # 기본 필드
      self.name_edit.setEnabled(enabled)
      self.type_combo.setEnabled(False)
      self.title_edit.setEnabled(enabled)
      self.server_edit.setEnabled(enabled)
      self.nickname_edit.setEnabled(enabled)
      self.comment_edit.setEnabled(enabled)
      self.zone_combobox.setEnabled(enabled)
      self.repeat_spin.setEnabled(enabled)
      self.enable_check.setEnabled(enabled)

      # Telegram 필드
      self.token_edit.setEnabled(enabled)
      self.chatid_edit.setEnabled(enabled)
      self.baseurl_edit.setEnabled(enabled)

      # Discord 필드
      self.webhooks_edit.setEnabled(enabled)

   def update_button_states(self):
      """버튼 활성화 상태 업데이트"""
      has_selection = len(self.noti_list.selectedItems()) > 0
      self.del_btn.setEnabled(has_selection)

   @Slot(int)
   def on_type_changed(self, index):
      """알림 유형 변경 시 처리"""
      if index == 0:  # Telegram
         self.telegram_widget.setVisible(True)
         self.discord_widget.setVisible(False)
      else:  # Discord
         self.telegram_widget.setVisible(False)
         self.discord_widget.setVisible(True)

   def on_item_selection_changed(self):
      """항목 선택 변경 시 처리"""
      self.update_button_states()

      selected_items = self.noti_list.selectedItems()
      if not selected_items:
         # 선택된 항목이 없으면 폼 비활성화
         self.set_form_enabled(False)
         self.status_label.setText("알림 설정을 선택하세요.")
         self.current_noti_item = None
         self.current_noti_key = None
         return

      # 선택된 항목 정보 표시
      selected_item = selected_items[0]
      item_text = selected_item.text()
      item_key = selected_item.data(Qt.UserRole)

      # 선택된 항목의 데이터 가져오기
      self.current_noti_key = item_key
      self.current_noti_item = self.noti_items.get(item_key)
      # print(f"on_item_selection_changed(): [{item_key}] {item_text}")

      if self.current_noti_item:
         # 기존 데이터 폼에 채우기
         self.fill_form_with_data(self.current_noti_item)
         self.set_form_enabled(True)
         self.status_label.setText(f"'{item_text}' 알림 설정을 편집 중입니다.")
      else:
         # 새 항목이면 기본값으로 초기화
         self.reset_form()
         self.set_form_enabled(True)
         self.name_edit.setText(item_text)  # 이름만 설정
         self.status_label.setText(f"'{item_text}' 알림 설정을 생성 중입니다.")

   def fill_form_with_data(self, noti_item):
      """알림 항목 데이터로 폼 채우기"""
      # 기본 필드
      self.name_edit.setText(noti_item.name)

      # 유형 설정
      type_index = 0 if noti_item.type.lower() == "discord" else 1
      self.type_combo.setCurrentIndex(type_index)

      self.title_edit.setText(noti_item.message_title)
      self.server_edit.setText(noti_item.acc_server)
      self.nickname_edit.setText(noti_item.acc_nickname)
      self.comment_edit.setText(noti_item.comment)
      zonetext = ""
      if noti_item.zone:
         zone = AreasStore.Get_ZoneArea(noti_item.zone)
         if zone: zonetext = zone.name
      self.zone_combobox.setCurrentText(zonetext)
      self.repeat_spin.setValue(noti_item.repeat_min)
      self.enable_check.setChecked(noti_item.enable)

      # 유형별 필드
      if isinstance(noti_item, TelegramNoti):
         self.token_edit.setText(noti_item.token)
         self.chatid_edit.setText(noti_item.chatid)
         self.baseurl_edit.setText(noti_item.baseurl)
      elif isinstance(noti_item, DiscordNoti):
         self.webhooks_edit.setText(noti_item.webhooks)

   def reset_form(self):
      """폼 필드 초기화"""
      # 기본 필드
      self.name_edit.clear()
      self.type_combo.setCurrentIndex(0)  # 기본값: Telegram
      self.title_edit.clear()
      self.server_edit.clear()
      self.nickname_edit.clear()
      self.comment_edit.clear()
      self.zone_combobox.setCurrentText("")
      self.repeat_spin.setValue(60)  # 기본값: 30분
      self.enable_check.setChecked(True)  # 기본값: 사용

      # Telegram 필드
      self.token_edit.clear()
      self.chatid_edit.clear()
      self.baseurl_edit.setText("https://api.telegram.org/bot")

      # Discord 필드
      self.webhooks_edit.clear()

   def add_notification(self):
      """새 알림 설정 추가"""
      count = self.noti_list.count()

      text, ok = QInputDialog.getText(
         self,
         "알림 추가",
         "알림 설정 이름:",
         QLineEdit.Normal,
         f"새 알림 {count + 1}",
      )
      if ok and text:
         # 중복 검사
         items = [
               self.noti_list.item(i).text() for i in range(self.noti_list.count())
         ]
         if text in items:
               QMessageBox.warning(
                  self, "중복 항목", "이미 존재하는 알림 설정 이름입니다."
               )
               return

         # 고유 키 생성
         key = SYS_UTIL.GetKey("noti")
         # print(key)

         # 목록에 추가
         item = QListWidgetItem(text)
         item.setData(Qt.UserRole, key)
         self.noti_list.addItem(item)
         # current = self.noti_list.currentItem()
         # print(f"[{current.data(Qt.UserRole)}] {current.text()}")

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
         item_key = item.data(Qt.UserRole)

         # 확인 메시지
         reply = QMessageBox.question(
               self,
               "알림 삭제",
               f"'{item.text()}' 알림 설정을 삭제하시겠습니까?",
               QMessageBox.Yes | QMessageBox.No,
               QMessageBox.No,
         )

         if reply == QMessageBox.Yes:
               NotiStore.Delete_Noti(item_key)
               
               # 목록에서 제거
               self.noti_list.takeItem(current_row)

               # 데이터에서도 제거
               if item_key in self.noti_items:
                  del self.noti_items[item_key]

               # 폼 초기화
               self.reset_form()
               self.set_form_enabled(False)
               self.status_label.setText("알림 설정을 선택하세요.")

               # 버튼 상태 업데이트
               self.update_button_states()

   def edit_notification(self):
      """선택한 알림 설정 수정"""
      current_row = self.noti_list.currentRow()
      if current_row >= 0:
         item = self.noti_list.item(current_row)
         current_text = item.text()

         text, ok = QInputDialog.getText(
               self, "알림 수정", "알림 설정 이름:", text=current_text
         )

         if ok and text and text != current_text:
               # 중복 검사 (현재 항목 제외)
               items = [
                  self.noti_list.item(i).text()
                  for i in range(self.noti_list.count())
                  if i != current_row
               ]
               if text in items:
                  QMessageBox.warning(
                     self, "중복 항목", "이미 존재하는 알림 설정 이름입니다."
                  )
                  return

               # 항목 텍스트 업데이트
               item.setText(text)

               # 현재 편집 중인 항목이 있으면 이름도 업데이트
               if self.current_noti_item:
                  self.current_noti_item.name = text
                  self.name_edit.setText(text)

   def save_current_form(self):
      """현재 폼 데이터 저장"""
      if not self.current_noti_key:
         return False

      # 폼 데이터 가져오기
      name = self.name_edit.text()
      type_str = "discord" if self.type_combo.currentIndex() == 0 else "telegram"
      message_title = self.title_edit.text()
      acc_server = self.server_edit.text()
      acc_nickname = self.nickname_edit.text()
      comment = self.comment_edit.toPlainText()
      zonetext = self.zone_combobox.currentText()
      zonekey = ""
      if zonetext:
         zonedata = AreasStore.Get_ZoneArea_byName(zonetext, default=None)
         if zonedata is not None:
            key, _ = zonedata
            zonekey = key
      # else:
      #    QMessageBox.warning(
      #       self,
      #       "입력 오류",
      #       "캡처할 영역을 설정해 주세요",
      #    )
      #    if not token:
      #       self.token_edit.setFocus()
      #    else:
      #       self.chatid_edit.setFocus()
      #    return False
      repeat_min = self.repeat_spin.value()
      enable = self.enable_check.isChecked()

      def Get_DefaultInfo():
         ret = {}
         ret["name"] = name
         ret["type"] = type_str
         ret["message_title"] = message_title
         ret["acc_server"] = acc_server
         ret["acc_nickname"] = acc_nickname
         ret["comment"] = comment
         ret["zone"] = zonekey
         ret["repeat_min"] = repeat_min
         ret["enable"] = enable
         return ret

      # 필수 필드 검증
      if not name:
         QMessageBox.warning(self, "입력 오류", "알림 이름은 필수 입력 항목입니다.")
         self.name_edit.setFocus()
         return False

      noti_item = {}
      # 유형에 따라 알림 객체 생성
      if type_str == "telegram":
         token = self.token_edit.text()
         chatid = self.chatid_edit.text()
         baseurl = self.baseurl_edit.text()

         # 필수 필드 검증
         if not token or not chatid:
               QMessageBox.warning(
                  self,
                  "입력 오류",
                  "Telegram API 토큰과 채팅 ID는 필수 입력 항목입니다.",
               )
               if not token:
                  self.token_edit.setFocus()
               else:
                  self.chatid_edit.setFocus()
               return False
         noti_item = Get_DefaultInfo()
         noti_item["token"] = token
         noti_item["chatid"] = chatid
         noti_item["baseurl"] = baseurl
         
         self.noti_items[self.current_noti_key] = TelegramNoti(**noti_item)
      else:  # Discord
         webhooks = self.webhooks_edit.text()

         # 필수 필드 검증
         if not webhooks:
               QMessageBox.warning(
                  self, "입력 오류", "Discord Webhook URL은 필수 입력 항목입니다."
               )
               self.webhooks_edit.setFocus()
               return False
         noti_item = Get_DefaultInfo()
         noti_item["webhooks"] = webhooks
         
         self.noti_items[self.current_noti_key] = DiscordNoti(**noti_item)
      
      NotiStore.Add_Noti(self.current_noti_key, noti_item)

      self.status_label.setText(f"'{name}' 알림 설정이 저장되었습니다.")
      return True

   def save_notifications(self):
      """알림 설정 저장"""
      # 현재 편집 중인 폼 저장
      if self.current_noti_key and self.name_edit.isEnabled():
         if not self.save_current_form():
               return

      # 알림 목록 저장
      notifications = []
      for i in range(self.noti_list.count()):
         item = self.noti_list.item(i)
         notifications.append(item.text())

      # 알림 목록 데이터 업데이트
      self.notification_list = notifications

      # TODO: 알림 아이템 데이터를 외부 저장소에 저장하는 코드 추가

      QMessageBox.information(self, "저장 완료", "알림 설정이 저장되었습니다.")

   def Close_Editor(self):
      """에디터 닫기"""
      # 현재 편집 중인 폼에 변경 사항이 있는지 확인
      if self.current_noti_key and self.name_edit.isEnabled():
         reply = QMessageBox.question(
               self,
               "변경 사항 저장",
               "현재 편집 중인 알림 설정의 변경 사항을 저장하시겠습니까?",
               QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
               QMessageBox.Yes,
         )

         if reply == QMessageBox.Yes:
               if self.save_current_form():
                  self.close()
         elif reply == QMessageBox.No:
               self.close()
         # Cancel은 아무것도 하지 않음
      else:
         # 목록의 변경 사항 확인
         current_notifications = [
               self.noti_list.item(i).text() for i in range(self.noti_list.count())
         ]
         if current_notifications != self.notification_list:
               reply = QMessageBox.question(
                  self,
                  "변경 사항 저장",
                  "알림 목록의 변경 사항을 저장하시겠습니까?",
                  QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                  QMessageBox.Yes,
               )

               if reply == QMessageBox.Yes:
                  self.save_notifications()
                  self.close()
               elif reply == QMessageBox.No:
                  self.close()
               # Cancel은 아무것도 하지 않음
         else:
               self.close()
