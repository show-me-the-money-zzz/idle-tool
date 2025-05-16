from dataclasses import dataclass

@dataclass
class BaseNotiItem:
    name: str
    type: str   #discord / telegram

    message_title: str
    acc_server: str     # 계정의 서버 이름
    acc_nickname: str   # 계정 이름
    comment: str
    
    zone: str   # zone item key
    repeat_min: int     # 반복 주기 (분)
    enable: bool        # 사용 여부
    
    @property
    def Print(self): print("BaseNotiItem")
    
@dataclass
class TelegramNoti(BaseNotiItem):
    token: str
    chatid: str
    baseurl: str    # 상수값?
    
@dataclass
class DiscordNoti(BaseNotiItem):
    webhooks: str