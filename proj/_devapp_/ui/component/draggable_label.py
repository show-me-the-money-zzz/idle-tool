from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

import zzz.config as CONFIG

class DraggableLabel(QLabel):
   """드래그 가능한 레이블 위젯"""

   def __init__(self, text="", parent=None):
      super().__init__(text, parent)
      self.setTextInteractionFlags(Qt.TextSelectableByMouse)

      isDarkTheme = CONFIG.APP_THEME == 'Windows'
      color_bg = "#1e1e1e" if isDarkTheme else "#f0f0f0"
      color_board  = "#f0f0f0" if isDarkTheme else "#1e1e1e"
      self.setStyleSheet(f"background-color: {color_bg}; padding: 2px 5px; border: 1px solid {color_board};")

      self.setCursor(Qt.IBeamCursor)
      self.setToolTip("드래그하여 텍스트를 복사할 수 있습니다")