import webview
from backend_api import Api

if __name__ == '__main__':
    api = Api()
    window = webview.create_window('PyWebView App', 'web/index.html', js_api=api)
    webview.start(debug=True)
