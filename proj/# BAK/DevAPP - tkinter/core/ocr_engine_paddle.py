# import cv2
# import re
# import numpy as np
# from paddleocr import PaddleOCR
# import logging

# # 디버그 로그 끄기
# logging.getLogger('ppocr').setLevel(logging.ERROR)

# # PaddleOCR 객체 초기화 (회전 보정 및 다국어 포함)
# ocr = PaddleOCR(use_angle_cls=True, lang='korean')

# def enhance_image_obj(image):
#     """
#     이미지 배열 기반 전처리 (확대 + 그레이스케일)
#     """
#     if not isinstance(image, np.ndarray):
#         raise ValueError("image는 OpenCV 이미지(numpy.ndarray)여야 합니다.")
#     img = cv2.resize(image, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     return gray

# def normalize_ocr_text(text):
#     """
#     숫자/슬래시가 병합되거나 잘못된 경우 복원 시도
#     예: 864078640 -> 8,640 / 8,640
#     """
#     match = re.findall(r"(\d{4,6})[\D]+(\d{4,6})", text.replace(",", "").replace(" ", ""))
#     if match:
#         return f"{int(match[0][0]):,} / {int(match[0][1]):,}"
#     return text

# def extract_text_from_image_obj(image):
#     """
#     PaddleOCR을 사용한 이미지 객체 텍스트 추출 + 후처리
#     :param image: OpenCV 이미지 또는 PIL.Image (자동 변환)
#     :return: [(text, confidence), ...]
#     """
#     # PIL.Image인 경우 numpy로 변환
#     if not isinstance(image, np.ndarray):
#         try:
#             import PIL.Image
#             if isinstance(image, PIL.Image.Image):
#                 image = np.array(image)
#             else:
#                 raise ValueError("지원되지 않는 이미지 타입입니다.")
#         except ImportError:
#             raise ValueError("PIL 이미지 변환을 위해 Pillow가 필요합니다.")

#     try:
#         processed = enhance_image_obj(image)
#         result = ocr.ocr(processed, cls=True)
#     except Exception as e:
#         print(f"[OCR 오류]: {e}")
#         return []

#     if not result or result[0] is None:
#         return []

#     texts = []
#     for line in result[0]:
#         raw_text = line[1][0]
#         confidence = line[1][1]
#         fixed_text = normalize_ocr_text(raw_text)
#         texts.append((fixed_text, confidence))
#     return texts

def extract_text_list_from_image(image):
    # """
    # 텍스트 리스트만 반환하는 경량 함수
    # """
    # results = extract_text_from_image_obj(image)
    # return [text for text, _ in results]

    return []
