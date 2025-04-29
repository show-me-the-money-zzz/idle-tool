from PySide6.QtWidgets import QListWidget

def ChangeText_ListWidget(lisstwidget: QListWidget, old_text: str, new_text: str):
   for index in range(lisstwidget.count()):
      item = lisstwidget.item(index)
      if old_text == item.text():
         item.setText(new_text)