# requirements:
# pip install paddleocr paddlepaddle opencv-python

from paddleocr import PaddleOCR
import cv2
import re

import logging
logging.getLogger('ppocr').setLevel(logging.ERROR)
# OCR 객체 초기화(객체 생성) (다국어 지원, 회전 보정 포함)
ocr = PaddleOCR(use_angle_cls=True, lang='korean')

def enhance_image(image_path):
    """
    이미지 확대 + 이진화 전처리
    """
    # img = cv2.imread(image_path)
    # img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, threshed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # processed_path = "enhanced_" + image_path
    # cv2.imwrite(processed_path, threshed)
    # return processed_path

    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("enhanced_" + image_path, gray)
    return "enhanced_" + image_path

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
        return []  # OCR 실패 시 빈 결과 반환

    texts = []
    for line in result[0]:
        raw_text = line[1][0]
        confidence = line[1][1]
        fixed_text = normalize_ocr_text(raw_text)
        texts.append((fixed_text, confidence))
    return texts

def read_ocr(path, results):
    # print(f"\n[인식 결과 ({path})]")
    # for text, conf in results:
    #     print(f"- {text} (정확도: {conf:.2f})")

    print(f"[인식 결과 ({path})] {results}")

def Process(path):
    output = extract_text_from_image(path)
    read_ocr(path, output)

if __name__ == "__main__":
    Process("hp.png")
    Process("mp.png")
    Process("potion.png")
    Process("locate-kind.png")
    Process("locate-name.png")
    # path = "hp.png"
    # output = extract_text_from_image(path)
    # read_ocr(path, output)
