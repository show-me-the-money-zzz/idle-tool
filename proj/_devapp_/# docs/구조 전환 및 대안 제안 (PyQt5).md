
# 📘 OCR 기반 자동 캡처 시스템: 구조 전환 및 대안 제안

이 문서는 기존의 `Tkinter + mss + Tesseract` 구조의 한계를 보완하고,  
더 나은 성능과 안정성, OCR 정확도를 제공할 수 있는 대체 기술 스택을 제안합니다.

---

## ✅ 개선 목표

1. **Tkinter를 벗어나 더 강력한 GUI 프레임워크로 전환**
2. **mss를 대체할 수 있는 안정적이고 유연한 화면 캡처 방식 도입**
3. **Tesseract를 대체할 정확도 높은 최신 OCR 엔진 적용**

---

## ✅ 1. GUI 프레임워크 대안

| 기존 | 대안 | 특징 |
|------|------|------|
| Tkinter | PyQt5 / PySide6 | 강력한 이벤트 시스템, 스레드 관리, 멀티윈도우 등 지원 |
|  | DearPyGui | GPU 기반 고성능 렌더링, 초경량 UI 툴킷 |
|  | Electron (with Python backend) | Web 기술 기반 UI, 확장성 우수 (단, 무겁고 외부 연동 필요) |

📌 **추천**: `PyQt5` 또는 `PySide6`  
→ Python 개발자 친화적이며, `QThread`로 OCR 병렬 처리 가능

---

## ✅ 2. 화면 캡처 방식 대안

| 기존 | 대안 | 설명 |
|------|------|------|
| mss | pyautogui.screenshot(region=...) | 간단하고 안정적인 부분 캡처, PIL 기반 |
|  | win32gui + win32ui + PIL | Windows GDI 기반, 빠르고 정밀한 창 영역 캡처 |
|  | OpenCV + DirectX 또는 GStreamer | 고해상도 영상/게임용, 고속 실시간 처리에 적합 |

📌 **추천**:  
- `pyautogui` → 간단한 부분 캡처  
- `win32gui` → 특정 창, 다중 모니터 대응 포함

---

## ✅ 3. OCR 엔진 대안

| 기존 | 대안 | 장점 |
|------|------|------|
| Tesseract | EasyOCR | 빠르고 정확도 높음, 다국어 지원, GPU 가능 |
|  | PaddleOCR | 한글 인식 최상, 문단 구조 인식, 고성능 |
|  | Google Cloud Vision OCR | 클라우드 기반, 정확도 최상 (유료) |

📌 **추천**:  
- `EasyOCR`: 설치 간단, 성능 우수, 한글도 실용 수준  
- `PaddleOCR`: 한글 OCR 정확도 최상, 단 설치 복잡

---

## ✅ 구조 예시: PyQt + pyautogui + EasyOCR

```python
class CaptureWorker(QThread):
    result_ready = pyqtSignal(str)

    def run(self):
        while self.running:
            img = pyautogui.screenshot(region=(x, y, w, h))
            result = reader.readtext(np.array(img))
            self.result_ready.emit(result)

class MainWindow(QMainWindow):
    def __init__(self):
        ...
        self.capture_worker = CaptureWorker()
        self.capture_worker.result_ready.connect(self.handle_result)
```

---

## ✅ 결론

| 항목 | 기존 기술 | 대안 기술 |
|------|------------|-------------|
| GUI | Tkinter | PyQt5, DearPyGui |
| 캡처 | mss | pyautogui, win32gui |
| OCR | Tesseract | EasyOCR, PaddleOCR |

🎯 전체적으로 `PyQt5 + pyautogui + EasyOCR` 구조가  
성능, 정확도, 안정성 면에서 균형 잡힌 최적의 조합입니다.

---

## 📝 다음 단계 제안

- MVP 구조 구현: PyQt + EasyOCR  
- 다중 영역 캡처 및 OCR 병렬 테스트  
- OCR 결과 시각화 / 저장 기능 확장
