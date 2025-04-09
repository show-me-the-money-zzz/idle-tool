import tkinter as tk
from tkinter import ttk
import stores.def_info as Info

class InfoBar(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)

        # 전체 프레임은 좌우로 나눔
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # 값 표시용 입력창 (비활성)
        self.hp_var = tk.StringVar()
        self.mp_var = tk.StringVar()
        self.potion_var = tk.StringVar()
        self.is_potion0 = tk.StringVar()
        self.loc_kind_var = tk.StringVar()
        self.loc_name_var = tk.StringVar()

        ttk.Label(left_frame, text="HP").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Entry(left_frame, textvariable=self.hp_var, width=6, state="readonly").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(left_frame, text="MP").pack(side=tk.LEFT)
        ttk.Entry(left_frame, textvariable=self.mp_var, width=6, state="readonly").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(left_frame, text="물약").pack(side=tk.LEFT)
        ttk.Entry(left_frame, textvariable=self.potion_var, width=6, state="readonly").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(left_frame, textvariable=self.is_potion0, width=2, state="readonly").pack(side=tk.LEFT, padx=(0, 10))

        # 위치 정보 (Entry 2개로 구분 + 긴 경우 여유 공간 확보)
        ttk.Entry(right_frame, textvariable=self.loc_kind_var, width=7, state="readonly", justify="right").pack(side=tk.LEFT)
        ttk.Label(right_frame, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(right_frame, textvariable=self.loc_name_var, width=12, state="readonly", justify="left").pack(side=tk.LEFT, padx=(0, 15), expand=True, fill=tk.X)

        self.update_info()

    def update_info(self):
        # print(f"tick~~ ({Info.Loop_Interval})")
        def Check_Vital(vital):
            return "Χ" if -1 == vital else str(vital)
        
        self.hp_var.set(Check_Vital(Info.HP))
        self.mp_var.set(Check_Vital(Info.MP))
        self.potion_var.set(Check_Vital(Info.POTION))
        
        # self.is_potion0.set("★" if Info.Is_Potion0 else "○")
        if 1 == Info.Is_Potion0 : self.is_potion0.set("★")
        elif 0 == Info.Is_Potion0 : self.is_potion0.set("○")
        elif -1 == Info.Is_Potion0 : self.is_potion0.set("Χ")
        
        self.loc_kind_var.set(Info.Locate_Kind)
        self.loc_name_var.set(Info.Locate_Name)

        self.after(Info.Loop_Interval_MS, self.update_info)
