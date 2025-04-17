# Python 기반 Web UI 프로젝트 정리

Python으로 GUI 애플리케이션을 만들 때, HTML/CSS/JavaScript 기반의 **웹 기술**을 활용할 수 있는 주요 방법들을 정리한 문서입니다.

---

## ✅ 주요 선택지 요약

| 기술 조합 | 설명 | 장점 | 단점 |
|------------|------|------|------|
| **PyWebView** | Python + HTML을 임베드하여 WebView 띄움 | 설치 간단, 가벼움 | 제한된 통신 및 기능 확장성 |
| **Flask/FastAPI + 브라우저** | 로컬서버 띄우고 브라우저를 UI로 사용 | 구조 단순, UI 자유도 높음 | 데스크탑 앱 형태는 아님 |
| **Electron + Python** | Electron (프론트) + Python (백엔드) 분리 | 상업 앱 수준 UI, SPA 지원 | 용량 큼, Node + Python 이중 환경 필요 |
| **Tauri + Python** | Rust 기반 Tauri + Python 백엔드 | Electron보다 훨씬 가볍고 빠름 | Rust 설치 필요, IPC 연동 설계 필요 |

---

## 📁 PyWebView 예제 구조
```
pywebview_app/
├── app.py
└── index.html
```

### 🔸 핵심 코드
```python
# app.py
import webview

class API:
    def say_hello(self, name):
        print(f"Hello, {name}!")

window = webview.create_window("앱", "index.html", js_api=API())
webview.start()
```

---

## 📁 Electron + Python 예제 구조
```
electron_python_app/
├── main.js           # Electron 진입점
├── index.html        # 프론트엔드
├── python_server.py  # Flask 백엔드
└── package.json
```

### 🔸 핵심 코드
```python
# python_server.py
from flask import Flask
app = Flask(__name__)
@app.route('/hello')
def hello():
    return "Hello from Python"
app.run(port=5000)
```
```javascript
// main.js
const { BrowserWindow, app } = require('electron')
app.whenReady().then(() => {
  const win = new BrowserWindow({ width: 800, height: 600 })
  win.loadFile("index.html")
})
```

---

## 📁 Tauri + Python 연동 구조
```
tauri_python_app/
├── src-tauri/           # Tauri 설정 및 빌드 파일
├── frontend/index.html  # HTML 기반 프론트엔드
└── python/app.py        # Python 백엔드 서버 (Flask 등)
```

### 🔸 IPC 또는 Shell 연동
```javascript
import { Command } from '@tauri-apps/api/shell'
const cmd = new Command('python', ['python', './python/app.py'])
cmd.execute().then(console.log)
```

---

## 🚀 추천 가이드

| 목적 | 추천 방식 |
|------|------------|
| 가볍고 빠른 데스크탑 앱 | ✅ PyWebView or Tauri |
| SPA 수준의 풍부한 UI | ✅ Electron + Python 백엔드 |
| 브라우저 기반 도구 | ✅ Flask/FastAPI + 브라우저 |

---

필요 시 각 방식의 템플릿, 배포 스크립트, PyInstaller 연동, Tauri IPC 연동 등도 확장 가능합니다.

