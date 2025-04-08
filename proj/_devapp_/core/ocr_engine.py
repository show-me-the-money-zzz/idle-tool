import cv2
import numpy as np
import pytesseract
import os
import gc
from PIL import Image
from concurrent.futures import ProcessPoolExecutor

def setup_tesseract(tesseract_path):
    """Tesseract OCR 경로 설정"""
    if not os.path.exists(tesseract_path):
        raise FileNotFoundError(f"Tesseract OCR 파일을 찾을 수 없습니다: {tesseract_path}")
    if not tesseract_path.lower().endswith('tesseract.exe'):
        raise ValueError("선택한 파일이 tesseract.exe가 아닙니다.")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
def resize_image(image, scale=2):
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

def preprocess_image(image, filename=None):
    """OCR 인식률 향상을 위한 이미지 전처리"""
    img = np.array(image)
    
    # if zoomin: img = resize_image(image);
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 그레이스케일 변환
    # img = cv2.GaussianBlur(img, (5, 5), 0)  # 노이즈 제거용 블러
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] # 이진화
    
    if filename:
        cv2.imwrite(filename, img)
        print(f"[디버깅] 전처리 이미지 저장됨: {filename}")
    return img

def _image_to_text(img, lang='kor+eng'):
    """내부 OCR 수행 함수"""
    try:
        custom_config = r'--oem 3 --psm 7'
        # OCR Engine Mode: 0=Legacy, 1=LSTM only, 3=Default
        # Page Segmentation Mode: 7=단일 텍스트 라인, 6=블록, 11=스파스 텍스트
        text = pytesseract.image_to_string(img, lang=lang,
                                        #    config=custom_config
                                           )
        return text
    except Exception as e:
        error_msg = str(e)
        if "TesseractNotFoundError" in error_msg:
            return "[OCR 오류: Tesseract OCR을 찾을 수 없습니다. 설정 메뉴에서 경로를 확인해주세요.]"
        else:
            return f"[OCR 오류: {error_msg}]"

def image_to_text(image, lang='kor+eng'):
    """단일 이미지 OCR 실행 (메모리 관리 포함)"""
    img = preprocess_image(image,
                        #    filename="image_to_text.png"
                           )
    text = _image_to_text(img, lang)
    del img
    gc.collect()
    return text

def images_to_text_parallel(image_list, lang='kor+eng'):
    """다수의 이미지에 대해 병렬 OCR 처리"""
    preprocessed = [preprocess_image(img) for img in image_list]
    with ProcessPoolExecutor() as executor:
        results = executor.map(lambda img: _image_to_text(img, lang), preprocessed)
    del preprocessed
    gc.collect()
    return list(results)
