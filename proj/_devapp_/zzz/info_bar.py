import tkinter as tk
from tkinter import ttk
import stores.def_info as info

class InfoBar(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.label = ttk.Label(self, anchor=tk.W)
        self.label.pack(fill=tk.X)

        self.update_info()

    def update_info(self):
        text = f"HP: {info.HP}   MP: {info.MP}   물약: {info.POTION}   위치: {info.Locate_Kind} / {info.Locate_Name}"
        self.label.config(text=text)

        # 일정 주기로 자동 갱신 (1초 간격)
        self.after(1000, self.update_info)
