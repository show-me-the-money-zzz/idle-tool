# OpenCV 기반 템플릿 매칭 가이드

템플릿 매칭(template matching)은 특정 이미지 영역(아이콘, 버튼 등)이 화면에 존재하는지를 판별하는 기술입니다. 이 문서는 템플릿 매칭을 구현할 때 OpenCV의 numpy 기반 구조를 사용하는 것이 왜 유리한지를 정리합니다.

---

## ✅ 템플릿 매칭이란?

- 큰 이미지(화면 캡처) 안에서 작은 이미지(템플릿)가 **일치하는 위치를 찾는 알고리즘**입니다.
- 주로 `cv2.matchTemplate()` 함수로 수행됩니다.

---

## ✅ OpenCV (numpy) 기반이 유리한 이유

| 항목 | PIL.Image | OpenCV (numpy.ndarray) |
|------|-----------|-------------------------|
| 처리 속도 | 느림 (Python 레벨 처리) | ✅ 빠름 (C++ 백엔드) |
| 템플릿 매칭 함수 | ❌ 없음 | ✅ `cv2.matchTemplate()` 내장 |
| 채널/색상 제어 | 제한적 | ✅ BGR, 그레이스케일 등 세밀하게 조정 가능 |
| 성능 최적화 | ❌ | ✅ 다양한 매칭 알고리즘 지원 (CCOEFF, SQDIFF 등) |
| OCR, 슬라이싱 연계 | PIL로 변환 필요 | ✅ OCR 등 OpenCV 기반 처리에 바로 연계 가능 |

---

## ✅ 추천 코드 구조

### 단일 템플릿 매칭 예시
```python
result = cv2.matchTemplate(captured_img, template_img, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(result)

if max_val > 0.85:
    print("매칭 성공 위치:", max_loc)
```

### 템플릿 사전 로딩
```python
template_img = cv2.imread("template.png", cv2.IMREAD_COLOR)
```

---

## ✅ 매칭 알고리즘 종류 (`cv2.matchTemplate`)

| 알고리즘 | 설명 |
|----------|------|
| `TM_CCOEFF` | 상관 계수 방식 (기본값) |
| `TM_CCOEFF_NORMED` | 정규화된 상관 계수 (정확도 ↑) |
| `TM_SQDIFF` | 차이 제곱합 방식 (값이 작을수록 유사) |

---

## ✅ 주의할 점

- 템플릿과 대상 이미지의 **크기, 색상 공간(BGR/GRAY)**이 동일해야 함
- 템플릿 이미지가 너무 작거나, 압축되면 인식률 저하 가능
- threshold 값은 실험적으로 조정 (보통 `0.8 ~ 0.95`)

---

## ✅ 결론

> 템플릿 매칭은 OpenCV 기반의 `cv2.matchTemplate()`으로 처리하는 것이 정확도, 속도, 확장성 측면에서 모두 유리합니다.
> PIL.Image 기반보다 numpy 배열(OpenCV 이미지) 기반으로 통일된 흐름을 사용하는 것을 추천합니다.

