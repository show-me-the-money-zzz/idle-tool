from datetime import datetime, timedelta

class RepeatTimer:
    """알림 항목을 나타내는 데이터 클래스"""
    # id: str  # 고유 식별자
    # title: str  # 알림 제목
    # message: str  # 알림 메시지
    interval_seconds: int   # 알림 간격 (초)
    # interval_minutes: int  # 알림 간격 (분)
    next_time: datetime  # 다음 알림 시간
    # enabled: bool = True  # 활성화 여부
    
    def __init__(self, interval_seconds):
        # self.interval_minutes = interval_minutes
        self.interval_seconds = interval_seconds
    
    def is_due(self) -> bool:
        """알림 시간이 되었는지 확인"""
        # return self.enabled and datetime.now() >= self.next_time
        return datetime.now() >= self.next_time
    
    def update_next_time(self):
        """다음 알림 시간 업데이트"""
        # self.next_time = datetime.now() + timedelta(minutes=self.interval_minutes)
        self.next_time = datetime.now() + timedelta(seconds=self.interval_seconds)
    
    def get_remaining_time(self) -> timedelta:
        """남은 시간 반환"""
        # if not self.enabled:
        #     return timedelta(seconds=0)
        
        now = datetime.now()
        if now >= self.next_time:
            return timedelta(seconds=0)
        
        return self.next_time - now