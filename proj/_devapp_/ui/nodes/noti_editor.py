from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QPushButton
                              )

import ui.css as CSS

class NotiEditor(QDialog):
   def __init__(self, parent):
      super().__init__(parent)
      self.setWindowTitle("알림 에디터")
      self.resize(720, 640)

      self._setup_ui()

   def _setup_ui(self):
      main_layout = QVBoxLayout(self)

       # 최하단 - 버튼 영역
      buttons_layout = QHBoxLayout()
      
      # 왼쪽에 취소 버튼 배치
      self.cancel_btn = QPushButton("닫기")
      self.cancel_btn.setStyleSheet(CSS.BUTTON_CANCEL)
      self.cancel_btn.clicked.connect(self.Close_Editor)
      buttons_layout.addWidget(self.cancel_btn)

      buttons_layout.addStretch(1)

      main_layout.addLayout(buttons_layout)

   def Close_Editor(self):
      #   self.save_task()
        self.close()