import os
import io
import cv2
import requests
import numpy as np
from PIL import Image
from typing import Union, Optional

from core.capture_utils import CaptureManager
import stores.areas as Areas

class TelegramNotifier:
    """텔레그램 챗봇을 통한 알림 전송 클래스"""
    
    def __init__(self, token: str, chat_id: str):
        """
        텔레그램 봇 초기화
        
        Args:
            token (str): 텔레그램 봇 토큰
            chat_id (str): 메시지를 보낼 채팅 ID
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.capture_manager = CaptureManager()
    
    def send_message(self, message: str) -> bool:
        """
        텍스트 메시지 전송
        
        Args:
            message (str): 전송할 메시지 내용
            
        Returns:
            bool: 전송 성공 여부
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"  # HTML 형식 지원 (굵게, 기울임, 링크 등)
        }
        
        try:
            response = requests.post(url, data=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"메시지 전송 실패: {e}")
            return False
    
    def send_photo(self, 
                  image: Union[np.ndarray, Image.Image, str], 
                  caption: Optional[str] = None) -> bool:
        """
        이미지 전송
        
        Args:
            image: OpenCV 이미지(np.ndarray), PIL 이미지, 또는 이미지 파일 경로
            caption (str, optional): 이미지와 함께 전송할 설명 텍스트
            
        Returns:
            bool: 전송 성공 여부
        """
        url = f"{self.base_url}/sendPhoto"
        
        # 이미지 데이터 준비
        files = None
        image_data = None
        
        try:
            # 이미지 타입에 따라 처리
            if isinstance(image, np.ndarray):  # OpenCV 이미지
                # OpenCV는 BGR 형식이므로 RGB로 변환
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    image_rgb = image
                
                # numpy 배열을 PIL Image로 변환
                pil_image = Image.fromarray(image_rgb)
                
                # PIL Image를 바이트 스트림으로 변환
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                image_data = img_byte_arr
                
            elif isinstance(image, Image.Image):  # PIL 이미지
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                image_data = img_byte_arr
                
            elif isinstance(image, str):  # 파일 경로
                if os.path.exists(image):
                    with open(image, 'rb') as f:
                        image_data = io.BytesIO(f.read())
                else:
                    print(f"파일을 찾을 수 없음: {image}")
                    return False
            else:
                print(f"지원하지 않는 이미지 형식: {type(image)}")
                return False
            
            # 이미지 데이터와 함께 요청 보내기
            files = {'photo': ('image.png', image_data, 'image/png')}
            data = {"chat_id": self.chat_id}
            
            if caption:
                data["caption"] = caption
                # data["parse_mode"] = "HTML"  # 캡션에 HTML 태그 지원
                data["parse_mode"] = "markdown"
            
            response = requests.post(url, data=data, files=files)
            return response.status_code == 200
            
        except Exception as e:
            print(f"이미지 전송 실패: {e}")
            return False
        finally:
            # 리소스 정리
            if image_data and hasattr(image_data, 'close'):
                image_data.close()
    
    def send_screenshot(self, caption: Optional[str] = None) -> bool:
        """
        현재 게임 창의 스크린샷 전송
        
        Args:
            caption (str, optional): 이미지와 함께 전송할 설명 텍스트
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 전체 창 스크린샷 캡처
            screenshot = self.capture_manager.capture_full_window()
            
            if screenshot is None:
                print("스크린샷 캡처 실패")
                return False
            
            # 캡처된 이미지 전송
            return self.send_photo(screenshot, caption)
            
        except Exception as e:
            print(f"스크린샷 전송 실패: {e}")
            return False
    
    def send_area_screenshot(self, area_name: str, caption: Optional[str] = None) -> bool:
        """
        지정된 영역의 스크린샷 전송
        
        Args:
            area_name (str): 캡처할 영역 이름 (stores.areas에 정의된 영역)
            caption (str, optional): 이미지와 함께 전송할 설명 텍스트
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # mss 객체 가져오기
            sct = self.capture_manager.sct
            
            # 영역 정보 가져오기            
            area = Areas.Get_ZoneArea(area_name)
            
            if area is None:
                print(f"정의되지 않은 영역: {area_name}")
                return False
            
            # 영역 캡처
            image = self.capture_manager._capture_crop(
                sct, area.x, area.y, area.width, area.height
            )
            
            if image is None:
                print(f"영역 캡처 실패: {area_name}")
                return False
            
            # 캡처된 이미지 전송
            return self.send_photo(image, caption)
            
        except Exception as e:
            print(f"영역 스크린샷 전송 실패: {e}")
            return False


# # 사용 예시
# if __name__ == "__main__":
#     # 설정값 (실제 사용 시 환경 변수나 설정 파일에서 불러오는 것을 권장)
#     BOT_TOKEN = "YOUR_BOT_TOKEN"
#     CHAT_ID = "YOUR_CHAT_ID"
    
#     # 텔레그램 알림 객체 생성
#     notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID)
    
#     # 예시 1: 텍스트 메시지 전송
#     notifier.send_message("게임 자동화 <b>알림</b>: 물약이 <i>소진</i>되었습니다.")
    
#     # 예시 2: 전체 화면 스크린샷 전송
#     notifier.send_screenshot("현재 게임 상태: 물약 소진")
    
#     # 예시 3: 특정 영역 스크린샷 전송
#     # 'HP_BAR' 영역이 stores.areas에 정의되어 있다고 가정
#     notifier.send_area_screenshot("HP_BAR", "현재 HP 상태")