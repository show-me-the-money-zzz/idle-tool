from dataclasses import dataclass

@dataclass
class BaseAreaItem:
    x: int
    y: int
    width: int
    height: int
    
    @property
    def CenterX(self): return self.x + self.width // 2
    @property
    def CneterY(self): return self.y + self.height // 2
    
    @property
    def ClickPoint(self): return (int(self.CenterX), int(self.CneterY))