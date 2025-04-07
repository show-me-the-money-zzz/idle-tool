import tkinter as tk
from tkinter import ttk

class LogFrame(ttk.LabelFrame):
    """로그 프레임 (이전의 인식된 텍스트 영역)"""
    
    def __init__(self, parent, status_var):
        super().__init__(parent, text="로그", padding="10")
        
        self.status_var = status_var
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 구성요소 초기화"""
        # 버튼 프레임 (상단)
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 로그 초기화 버튼
        self.clear_log_btn = ttk.Button(
            button_frame, 
            text="로그 초기화", 
            command=self.clear_log
        )
        self.clear_log_btn.pack(side=tk.RIGHT, padx=5)
        
        # 텍스트 영역과 스크롤바를 담을 프레임
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 텍스트 영역
        self.log_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(text_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def clear_log(self):
        """로그 텍스트 초기화"""
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("로그가 초기화되었습니다.")
    
    def add_log(self, text):
        """로그에 텍스트 추가"""
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)  # 스크롤을 최신 내용으로 이동