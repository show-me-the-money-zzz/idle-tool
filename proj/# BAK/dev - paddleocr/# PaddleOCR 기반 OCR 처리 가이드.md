# PaddleOCR 기반 OCR 처리 가이드

이 문서는 PaddleOCR을 활용하여 이미지에서 텍스트를 인식하고, 정확도를 향상시키기 위한 방법과 Python 코드 예제를 정리한 문서입니다.

---

## 1. 환경 설정

```bash
pip install paddleocr paddlepaddle opencv-python
```

---

## 2. OCR 처리 함수 구조

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='korean')
```

### 텍스트 추출 함수
```python
def extract_text_from_image(image_path):
    result = ocr.ocr(image_path, cls=True)
    texts = []
    for line in result[0]:
        text = line[1][0]
        confidence = line[1][1]
        texts.append((text, confidence))
    return texts
```

### 텍스트만 리스트로 추출
```python
def get_text_list_from_ocr_results(results):
    return [text for text, _ in results]
```

---

## 3. 전처리 함수 (이미지 향상)

```python
import cv2

def enhance_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("enhanced_" + image_path, gray)
    return "enhanced_" + image_path
```

---

## 4. 텍스트 정규화 함수

```python
import re

def normalize_ocr_text(text):
    match = re.findall(r"(\d{4,6})[\D]+(\d{4,6})", text.replace(",", "").replace(" ", ""))
    if match:
        return f"{int(match[0][0]):,} / {int(match[0][1]):,}"
    return text
```

---

## 5. 디버그 로그 제거

```python
import logging
logging.getLogger('ppocr').setLevel(logging.ERROR)
```

또는 전체 로그 억제:
```python
logging.getLogger().setLevel(logging.CRITICAL)
```

---

## 6. 전체 처리 예시

```python
def process_image(path):
    enhanced = enhance_image(path)
    results = extract_text_from_image(enhanced)
    texts = get_text_list_from_ocr_results(results)
    return texts
```

---

## 7. 개선 아이디어 요약

| 개선 항목 | 설명 |
|------------|------|
| 전처리 | 이미지 확대, 그레이스케일, 이진화 |
| 후처리 | 정규표현식 기반 텍스트 재구성 |
| 로그 억제 | 디버그 출력 제거로 깔끔한 실행 |
| 엔진 대안 | EasyOCR, Google Vision 등도 가능 |

---

필요시 Flask API, CLI 도구, 폴더 일괄처리용 OCR 등으로 확장 가능합니다.

