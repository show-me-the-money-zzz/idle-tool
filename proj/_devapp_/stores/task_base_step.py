from dataclasses import dataclass

@dataclass
class BaseStep:
    type: str
    seq: int
    waiting: float
    next_step: list[str]
    fail_step: str
    comment: str
    
    @property
    def Print(self): print("BaseStep")
    
@dataclass
class TaskStep_Matching(BaseStep):
    zone: str
    image: str
    score: str
    finded_click: str
   
@dataclass
class TaskStep_MouseWheel(BaseStep):
    amount: int
    
@dataclass
class TaskStep_TeltegramNoti(BaseStep):
    dummy: bool