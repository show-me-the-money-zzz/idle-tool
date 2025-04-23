from dataclasses import dataclass

@dataclass
class BaseAreaItem:
    x: int
    y: int
    width: int
    height: int
    clickx: int
    clicky: int
    
    @property
    def CenterX(self): return self.x + self.width // 2
    @property
    def CneterY(self): return self.y + self.height // 2
    
    @property
    def ClickPoint(self): return (self.x + self.clickx, self.y + self.clicky)