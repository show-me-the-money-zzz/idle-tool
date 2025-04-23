from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QCompleter

class SearchableComboBox(QComboBox):
    """검색 기능이 내장된 콤보박스"""
    
    def __init__(self, parent=None, items=None):
        super().__init__(parent)
        
        # 항목 설정
        if items:
            self.addItems(items)
        
        # 편집 가능하게 설정
        self.setEditable(True)
        
        # 자동 완성 기능 추가
        self.completer = QCompleter(self.model(), self)
        self.completer.setFilterMode(Qt.MatchContains)  # 부분 일치 검색 모드
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)  # 대소문자 구분 없음
        self.setCompleter(self.completer)
        
        # 현재 인덱스가 변경될 때 호출되는 메서드 연결
        self.currentIndexChanged.connect(self._handle_index_changed)
        
        # 편집 완료 시 호출되는 메서드 연결
        self.lineEdit().editingFinished.connect(self._handle_editing_finished)
    
    def _handle_index_changed(self, index):
        """콤보박스 선택이 변경되었을 때 호출"""
        if index >= 0:
            text = self.itemText(index)
            self.setEditText(text)
    
    def _handle_editing_finished(self):
        """편집이 완료되었을 때 호출"""
        text = self.currentText()
        index = self.findText(text, Qt.MatchContains)
        
        # 일치하는 항목이 있으면 그 항목으로 설정
        if index >= 0:
            self.setCurrentIndex(index)
        # 일치하는 항목이 없으면 텍스트만 표시
        else:
            self.setEditText(text)
    
    def get_current_text(self):
        """현재 텍스트 반환 (인덱스가 없어도 작동)"""
        return self.currentText()