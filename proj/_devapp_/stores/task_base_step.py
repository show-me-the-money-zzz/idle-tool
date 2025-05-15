from dataclasses import dataclass
import re

@dataclass
class BaseStep:
    name: str
    type: str
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
    
    def parse_score(self) -> tuple:
        """score 문자열을 (숫자, 연산자, 설명) 형태의 튜플로 반환"""
        match = re.match(r"(<=|>=|<|>|==|!=)?\s*(\d+(?:\.\d+)?)", self.score.strip())
        if not match:
            return (0, "==", "일치")

        op_str, value = match.groups()
        
        # 연산자가 없을 경우 기본값 설정
        if not op_str:
            op_str = "=="
            
        return (float(value), op_str, self.operator_to_desc(op_str))
    
    @staticmethod
    def operator_to_desc(op_str: str) -> str:
        """연산자 문자열을 설명 문자열로 변환"""
        op_map = {
            "<=": "이상",
            ">=": "이하",
            "<": "초과",
            ">": "미만",
            "==": "일치",
            "!=": "다른"
        }
        return op_map.get(op_str, "일치")
    
    @staticmethod
    def desc_to_operator(desc: str) -> str:
        """설명 문자열을 연산자 문자열로 변환"""
        desc_map = {
            "이상": "<=",
            "이하": ">=",
            "초과": "<",
            "미만": ">",
            "일치": "==",
            "다른": "!="
        }
        return desc_map.get(desc, "==")
    
    @staticmethod
    def make_score_string(value: float, desc: str) -> str:
        """숫자와 설명을 받아 score 문자열 생성"""
        op_str = TaskStep_Matching.desc_to_operator(desc)
        return f"{op_str}{value}"

    def evaluate_score_condition(self, actual: float) -> bool:
        """점수 조건 평가: '<=65'는 '실제 점수가 65 이상이면 참'으로 해석"""
        value, op_str, _ = self.parse_score()
        
        # 점수 조건 해석 (매칭 방향과 반대로 해석)
        if op_str == "<=":
            return actual >= value
        elif op_str == ">=":
            return actual <= value
        elif op_str == ">":
            return actual < value
        elif op_str == "<":
            return actual > value
        elif op_str == "==":
            return actual == value
        elif op_str == "!=":
            return actual != value
        else:
            return actual == value
        
    def Print_Score(self) -> str:
        """점수 조건을 한글로 설명하는 함수"""
        value, _, desc = self.parse_score()
        return f"{value}% {desc}"
    
    def Get_LogText(self) -> str:
        ret = "🙏 매칭: "
        if 0 < self.waiting:
            ret += f"(잠깐만 {self.waiting} 초) "
        ret += f"[영역: {self.zone}]의 [이미지: {self.image}]의 [유사도] {self.Print_Score()}"
        return ret
   
@dataclass
class TaskStep_MouseWheel(BaseStep):
    amount: int
    
@dataclass
class TaskStep_TeltegramNoti(BaseStep):
    dummy: bool