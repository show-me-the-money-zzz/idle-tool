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
    img = resize_image(img, scale=2.0)  # 리사이징. 적절한 배율 조정
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 그레이스케일 변환
    # img = cv2.GaussianBlur(img, (5, 5), 0)  # 노이즈 제거용 가우시안 블러
    
    # img = cv2.equalizeHist(img) # 대비 향상
    
    # 이진화 방법 개선 - 적응형 이진화 추가
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]  # 기존 방식
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    #                            cv2.THRESH_BINARY, 11, 2)
    
    # # 모폴로지 연산으로 노이즈 제거 및 텍스트 선명화
    # kernel = np.ones((1, 1), np.uint8)
    # img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    
    if filename:
        cv2.imwrite(filename, img)
        print(f"[디버깅] 전처리 이미지 저장됨: {filename}")
    return img

def enhanced_image_to_text(image, lang='kor+eng'):
    """여러 전처리 방법을 시도하여 가장 좋은 결과 도출"""
    results = []
    
    # 기본 전처리
    img1 = preprocess_image(image)
    results.append(_image_to_text(img1, lang))
    
    # 리사이징 후 처리 
    img2 = resize_image(np.array(image), scale=2.0)
    img2 = preprocess_image(img2)
    results.append(_image_to_text(img2, lang))
    
    # 적응형 이진화
    img3 = np.array(image)
    img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
    img3 = cv2.adaptiveThreshold(img3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY, 11, 2)
    results.append(_image_to_text(img3, lang))
    
    print(results)
    
def segment_and_recognize(image, lang='kor+eng'):
    """이미지를 여러 영역으로 나누어 인식 후 결과 병합"""
    height, width = image.shape[:2]
    
    # 이미지를 수평 또는 수직으로 분할
    segments = []
    num_segments = 3  # 분할 수 조정
    
    for i in range(num_segments):
        start_y = int(i * height / num_segments)
        end_y = int((i + 1) * height / num_segments)
        segment = image[start_y:end_y, 0:width]
        segments.append(segment)
    
    # 각 세그먼트 OCR 처리
    results = []
    for segment in segments:
        preprocessed = preprocess_image(segment)
        text = _image_to_text(preprocessed, lang)
        results.append(text)
    
    # 결과 병합
    # return '\n'.join([r for r in results if r.strip()])
    print(results)

def _image_to_text(img, lang='kor+eng'):
    """내부 OCR 수행 함수"""
    try:
        # custom_config = r'--oem 3 --psm 7'
        # OCR Engine Mode: 0=Legacy, 1=LSTM only, 3=Default
        # Page Segmentation Mode: 7=단일 텍스트 라인, 6=블록, 11=스파스 텍스트
        
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=가나다라마바사아자차카타파하ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,./'
        # whitelist는 실제 용도에 맞게 조정 필요
        # PSM 모드 다양화 - 텍스트 유형에 따라 적합한 모드 선택
        # 6: 균일한 텍스트 블록
        # 7: 한 줄의 텍스트
        # 11: 불규칙한 텍스트
        # 4: 회전 가능한 페이지의 단일 열
        
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
                        #    filename="claude.png"
                           )
    
    # enhanced_image_to_text(image)
    # segment_and_recognize(image)
    
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
