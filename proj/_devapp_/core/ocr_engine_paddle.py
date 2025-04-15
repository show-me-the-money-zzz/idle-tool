import cv2
import re
from paddleocr import PaddleOCR
import logging

# 디버그 로그 끄기
logging.getLogger('ppocr').setLevel(logging.ERROR)

# PaddleOCR 객체 초기화 (회전 보정 및 다국어 포함)
ocr = PaddleOCR(use_angle_cls=True, lang='korean')

def enhance_image(image_path):
    """
    이미지 확대 + 그레이스케일 전처리 (이진화는 비활성화)
    """
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced_path = "enhanced_" + image_path
    cv2.imwrite(enhanced_path, gray)
    return enhanced_path

def normalize_ocr_text(text):
    """
    숫자/슬래시가 병합되거나 잘못된 경우 복원 시도
    예: 864078640 -> 8,640 / 8,640
    """
    match = re.findall(r"(\d{4,6})[\D]+(\d{4,6})", text.replace(",", "").replace(" ", ""))
    if match:
        return f"{int(match[0][0]):,} / {int(match[0][1]):,}"
    return text

def extract_text_from_image(image_path):
    """
    PaddleOCR을 사용한 이미지 텍스트 추출 + 후처리
    """
    enhanced_path = enhance_image(image_path)
    result = ocr.ocr(enhanced_path, cls=True)

    if not result or result[0] is None:
        return []

    texts = []
    for line in result[0]:
        raw_text = line[1][0]
        confidence = line[1][1]
        fixed_text = normalize_ocr_text(raw_text)
        texts.append((fixed_text, confidence))
    return texts

def extract_text_list(image_path):
    """
    텍스트 리스트만 반환하는 경량 함수
    """
    results = extract_text_from_image(image_path)
    return [text for text, _ in results]
