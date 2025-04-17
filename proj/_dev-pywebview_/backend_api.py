# backend_api.py
import pytesseract
from PIL import ImageGrab

class Api:
    def read_text(self):
        image = ImageGrab.grab()  # 또는 캡처 영역 지정
        text = pytesseract.image_to_string(image)
        return text
