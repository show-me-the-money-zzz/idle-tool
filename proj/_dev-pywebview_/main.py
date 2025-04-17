import webview
from backend_api import Api

if __name__ == '__main__':
    api = Api()
    window = webview.create_window('쌀먹툴', 'web/index.html', js_api=api)
    webview.start(debug=True)
