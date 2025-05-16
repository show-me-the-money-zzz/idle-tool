from dataclasses import dataclass

class BaseNotiItem:
    type: str   #discord / telegram
    title: str
    zone: str   # zone item key
    acc_server: str     # 계정의 서버 이름
    acc_nickname: str   # 계정 이름
    repeat_min: int     # 반복 주기 (분)
    comment: str
    enable: bool        # 사용 여부
    
    @property
    def Print(self): print("BaseNotiItem")
    
@dataclass
class TelegramNoti(BaseNotiItem):
    token: str
    chatid: str
    baseurl: str    # 상수값?
    
class DiscordNoti(BaseNotiItem):
    webhooks: str