from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QScrollBar, QWidget, QFrame)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCursor

import os
from datetime import datetime

from stores.task_base_step import TaskStep_Matching

class LogFrame(QGroupBox):
    """로그 프레임 (이전의 인식된 텍스트 영역)"""
    
    def __init__(self, parent, status_signal):
        super().__init__("로그", parent)
        
        self.status_signal = status_signal
        
        self._color_toggle = False

        self.before_step_matching = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 버튼 프레임 (상단)
        button_frame = QWidget(self)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(button_frame)

        self.svae_log_btn = QPushButton("로그 저장")
        self.svae_log_btn.clicked.connect(self.save_log)
        button_layout.addWidget(self.svae_log_btn)
        
        # 버튼 레이아웃에 빈 공간 추가 (왼쪽)
        button_layout.addStretch(1)
        
        # 로그 초기화 버튼
        self.clear_log_btn = QPushButton("로그 초기화")
        self.clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_log_btn)
        
        # 텍스트 영역
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)  # 읽기 전용 설정
        self.log_text.setStyleSheet("background-color: #4a4a4a; color: white;")
        self.log_text.setFontPointSize(11)
        main_layout.addWidget(self.log_text)
        
        # PySide6에서는 QTextEdit이 이미 스크롤바를 내장하고 있음
    
    def save_log(self):
        """현재 로그를 파일로 저장합니다."""
        try:
            # 현재 시간을 요청한 형식으로 변환 (년도 두자리, 날짜_시간)
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            filename = f"gamelog-{timestamp}.log"
            
            # 로그 폴더 생성 (없는 경우)
            log_dir = os.path.join(os.getcwd(), "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # 전체 파일 경로
            file_path = os.path.join(log_dir, filename)
            
            # 로그 내용 가져오기 (HTML 태그 제거)
            log_content = self.log_text.toPlainText()
            
            # 파일에 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
                
            # 성공 메시지
            # self.status_signal.emit(f"로그가 저장되었습니다: {file_path}")
            self.add_notice(f"💾 로그가 저장되었습니다: {filename}")
            
            return True
        except Exception as e:
            self.add_error(f"로그 저장 오류: {str(e)}")
            return False
    
    @Slot()
    def clear_log(self):
        """로그 텍스트 초기화"""
        self.log_text.clear()
        self.status_signal.emit("로그가 초기화되었습니다.")
        
    @property
    def NormalColor(self): return "#b8abab" if self._color_toggle else "#ffffff"
    
    def add_log(self, text):
        self.print_log(self.NormalColor, text)
        
        self._color_toggle = not self._color_toggle

    def add_log_matching(self, __taskkey: str, __stepkey: str, __step: TaskStep_Matching, matched_score: float, issuccess: bool):
        if self.before_step_matching:
            taskkey = self.before_step_matching["taskkey"]
            stepkey = self.before_step_matching["stepkey"]
            
            if __taskkey == taskkey and __stepkey == stepkey:
                step = self.before_step_matching["step"]
                time_begin = self.before_step_matching["time_begin"]
                
                self.before_step_matching["time_end"] = datetime.now()
                
                result = LogFrame.GetText_Result(matched_score, issuccess)
                if result not in self.before_step_matching["resultlist"]:
                    self.before_step_matching["resultlist"].append(result)
                    
                time_end = self.before_step_matching["time_end"]
                resultlist = self.before_step_matching["resultlist"]
                
                color = self.before_step_matching["color"]
                
                logtext = f"[{LogFrame.GetText_Timestamp(time_begin)} ~ {LogFrame.GetText_Timestamp(time_end)}] "
                logtext += f"{step.Get_LogText()}에서: "
                logtext += f"{', '.join(resultlist)}"
                
                self.update_last_log(logtext, color)
            else:
                self.before_step_matching = None
                
        if not self.before_step_matching:
            result = LogFrame.GetText_Result(matched_score, issuccess)
            
            self.before_step_matching = {
                "taskkey": __taskkey,
                "stepkey": __stepkey,
                
                "step": __step,
                
                "time_begin": datetime.now(),
                "time_end": None,
            
                "resultlist": [ result ],
                "color": self.NormalColor,
            }
            
            logtext = f"{__step.Get_LogText()}에서: "
            self.add_log(logtext + result)
        
    def add_log_notmatching(self, text):
        # print(f"add_log_notmatching({text})")
        self.before_step_matching = None
        self.add_log(text)
    
    def add_warning(self, text):
        self.before_step_matching = None
        self.print_log("#ffe88c", text)
        
    def add_error(self, text):
        self.before_step_matching = None
        self.print_log("#ff8c8c", text)
        
    def add_notice(self, text):
        self.before_step_matching = None
        self.print_log("#00ff00", text)

    def add_chnagetaskstep(self, text):
        self.before_step_matching = None
        self.print_log("#afffdc", text)
        
    def print_log(self, color, text):
        timestamp = LogFrame.GetText_Timestamp(datetime.now())
        
        html = LogFrame.Make_HtmlText(color, f"[{timestamp}] {text}")
        self.log_text.append(html)
        
        # 스크롤을 최신으로 이동
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def GetText_Timestamp(time: datetime):
        return time.strftime("%m/%d %H:%M:%S")
        
    def GetText_Result(matched_score: float, issuccess: bool):
        text_success = "성공" if issuccess else "실패"
        return f"{matched_score:.1f}%({text_success})"
    
    def Make_HtmlText(color, text):
        return f'<span style="color:{color}">{text}</span>'
    
    def update_last_log(self, text, color=None, print_timestamp = False):
        """로그의 마지막 줄을 새 텍스트로 업데이트합니다."""
        try:
            # 마지막 항목 삭제
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            
            # 새 로그 추가
            if color is None:
                color = self.NormalColor
            
            logtext = ""
            if print_timestamp:
                timestamp = LogFrame.GetText_Timestamp(datetime.now())
                logtext = f"[{timestamp}] "
            logtext += f" {text}"
                
            html = LogFrame.Make_HtmlText(color, logtext)
            self.log_text.append(html)
            
            # 스크롤 업데이트
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            # 오류 발생 시 새 로그로 추가
            self.add_error(f"로그 업데이트 오류: {e}")
            self.add_log(text)