import os
import io
import cv2
import requests
import numpy as np
from PIL import Image
from typing import Union, Optional

from core.capture_utils import CaptureManager
import stores.areas as Areas
from grinder_utils.system import GetText_NotiDate

class DiscordNotifier:
    def __init__(self, webhooks: str):
        self.webhooks = webhooks
        self.capture_manager = CaptureManager()
        
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
            data = {}
            
            if caption: data = { "content": caption }
            response = requests.post(self.webhooks, data=data, files=files)
            return response.status_code == 200
            
        except Exception as e:
            print(f"이미지 전송 실패: {e}")
            return False
        finally:
            # 리소스 정리
            if image_data and hasattr(image_data, 'close'):
                image_data.close()
        
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
        
    def Make_Message(title, server, nickname, comment = ""):
        message = f"# {title}" + "\n"
        message += (f"**{server} / {nickname} / {GetText_NotiDate()}**" + "\n\n")
        if comment:
            message += (f"{comment}" + "\n")
        # message += "[자세히 보기(다음)](https://www.daum.net/)"
        return message