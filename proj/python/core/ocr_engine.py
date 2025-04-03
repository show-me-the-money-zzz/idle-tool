import cv2
import numpy as np
import pytesseract
import os
from PIL import Image

def setup_tesseract(tesseract_path):
    """Tesseract OCR 경로 설정"""
    # 경로 유효성 검사
    if not os.path.exists(tesseract_path):
        raise FileNotFoundError(f"Tesseract OCR 파일을 찾을 수 없습니다: {tesseract_path}")
    
    # Tesseract 실행 파일인지 확인 (tesseract.exe 파일명 확인)
    if not tesseract_path.lower().endswith('tesseract.exe'):
        raise ValueError("선택한 파일이 tesseract.exe가 아닙니다.")
    
    # 경로 설정
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
    try:
        text = pytesseract.image_to_string(img, lang=lang)
        return text
    except Exception as e:
        # Tesseract OCR 오류 처리
        error_msg = str(e)
        if "TesseractNotFoundError" in error_msg:
            return "[OCR 오류: Tesseract OCR을 찾을 수 없습니다. 설정 메뉴에서 경로를 확인해주세요.]"
        else:
            return f"[OCR 오류: {error_msg}]"