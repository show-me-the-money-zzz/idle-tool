import cv2
import numpy as np
import pytesseract
from PIL import Image

def setup_tesseract(tesseract_path):
    """Tesseract OCR 경로 설정"""
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def preprocess_image(image):
    """OCR 인식률 향상을 위한 이미지 전처리"""
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return img

def image_to_text(image, lang='kor+eng'):
    """이미지에서 텍스트 추출"""
    img = preprocess_image(image)
    text = pytesseract.image_to_string(img, lang=lang)
    return text