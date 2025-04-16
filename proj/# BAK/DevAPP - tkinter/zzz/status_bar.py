import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Frame):
    def __init__(self, root):
        """상태바 초기화"""
        super().__init__(root)
        
        # 상태 텍스트 변수
        self.status_var = tk.StringVar()
        
        # 상태바 레이블
        self.label = ttk.Label(
            self, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.label.pack(fill=tk.X)
    
    def set_status(self, text):
        """상태 텍스트 설정"""
        self.status_var.set(text)
    
    def get_status_var(self):
        """상태 텍스트 변수 반환"""
        return self.status_var