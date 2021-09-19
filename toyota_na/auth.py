import sys
import requests
from urllib.parse import urlparse, parse_qs
import jwt

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlScheme
from PyQt5.QtWidgets import QApplication


class MockToyotaAppHandler(QWebEngineUrlSchemeHandler):
    def __init__(self, app, result) -> None:
        super().__init__()
        self.app = app
        self.result = result

    def requestStarted(self, request):
        parsed_url = urlparse(request.requestUrl().url())
        code = parse_qs(parsed_url.query)["code"]
        self.result["code"] = code[0]
        self.app.quit()


def authorize():
    AUTHORIZE_URL = "https://login.toyotadriverslogin.com/oauth2/realms/root/realms/tmna-native/authorize?client_id=oneappsdkclient&scope=openid profile write&response_type=code&code_challenge=plain&redirect_uri=com.toyota.oneapp:/oauth2Callback&code_challenge_method=plain"
    app = QApplication(sys.argv)
    browser = QWebEngineView()
    result = {}
    scheme = QWebEngineUrlScheme("com.toyota.oneapp".encode("utf-8"))
    QWebEngineUrlScheme.registerScheme(scheme)
    scheme_handler = MockToyotaAppHandler(app, result)
    browser.page().profile().installUrlSchemeHandler("com.toyota.oneapp".encode("utf-8"), scheme_handler)
    browser.load(QUrl(AUTHORIZE_URL))
    browser.show()
    app.exec_()
    return result["code"]


def access_token(code):
    ACCESS_TOKEN_URL = "https://login.toyotadriverslogin.com/oauth2/realms/root/realms/tmna-native/access_token"
    data = {
        "client_id": "oneappsdkclient",
        "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
        "grant_type": "authorization_code",
        "code_verifier": "plain",
        "code": code
    }
    resp = requests.post(ACCESS_TOKEN_URL, data=data)
    return resp.json()


def refresh_token(refresh_token):
    ACCESS_TOKEN_URL = "https://login.toyotadriverslogin.com/oauth2/realms/root/realms/tmna-native/access_token"
    data = {
        "client_id": "oneappsdkclient",
        "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
        "grant_type": "refresh_token",
        "code_verifier": "plain",
        "refresh_token": refresh_token
    }
    resp = requests.post(ACCESS_TOKEN_URL, data=data)
    return resp.json()


def login():
    code = authorize()
    return access_token(code)


def get_guid(id_token):
    return jwt.decode(id_token, algorithms=["RS256"], options={"verify_signature": False})["sub"]
