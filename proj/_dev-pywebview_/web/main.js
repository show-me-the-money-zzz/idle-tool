function readOCR() {
    window.pywebview.api.read_text().then(result => {
      document.getElementById('ocr-result').innerText = result;
    });
  }
  