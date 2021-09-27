import sys
from datetime import datetime
import json
import aiohttp
from urllib.parse import urlparse, parse_qs, urlencode
import jwt
import logging


class NotLoggedIn(Exception): pass

DEFAULT_AUTH_FILE = ".toyota_na_tokens.json"

class ToyotaOneAuth:
    BASE_URL = "https://login.toyotadriverslogin.com/oauth2/realms/root/realms/tmna-native"

    def __init__(self, auth_file=DEFAULT_AUTH_FILE):
        self._auth_file = auth_file
        self._access_token = None
        self._refresh_token = None
        self._id_token = None
        self._guid = None
        self._expires_at = None
        try:
            if self._auth_file:
                self.load()
        except:
            pass


    def authorize(self):
        from PyQt5.QtCore import QUrl
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlScheme
        from PyQt5.QtWidgets import QApplication

        class MockToyotaAppHandler(QWebEngineUrlSchemeHandler):
            def requestStarted(self, request):
                parsed_url = urlparse(request.requestUrl().url())
                code = parse_qs(parsed_url.query)["code"]
                result["code"] = code[0]
                qtapp.quit()
        
        auth_params = {
            "client_id": "oneappsdkclient",
            "scope": "openid profile write",
            "response_type": "code",
            "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
            "code_challenge": "plain",
            "code_challenge_method": "plain"
        }
        AUTHORIZE_URL = f"{ToyotaOneAuth.BASE_URL}/authorize?{urlencode(auth_params)}"
        qtapp = QApplication(sys.argv[:1])
        browser = QWebEngineView()
        result = {}
        scheme = QWebEngineUrlScheme("com.toyota.oneapp".encode("utf-8"))
        QWebEngineUrlScheme.registerScheme(scheme)
        scheme_handler = MockToyotaAppHandler()
        browser.page().profile().installUrlSchemeHandler("com.toyota.oneapp".encode("utf-8"), scheme_handler)
        browser.load(QUrl(AUTHORIZE_URL))
        browser.show()
        qtapp.exec_()
        if "code" not in result:
            logging.error("Authorization Code not retrieved successfully.")
            raise NotLoggedIn()
        return result["code"]


    async def refresh_tokens(self):
        data = {
            "client_id": "oneappsdkclient",
            "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
            "grant_type": "refresh_token",
            "code_verifier": "plain",
            "refresh_token": self._refresh_token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{ToyotaOneAuth.BASE_URL}/access_token", data=data) as resp:
                self._extract_tokens(resp)

    async def check_tokens(self):
        if self._expires_at is None or self._expires_at < datetime.utcnow().timestamp():
            raise NotLoggedIn()
        if self._expires_at < datetime.utcnow().timestamp() + 300:
            await self.refresh_tokens()


    async def login(self, authorization_code=None):
        if authorization_code is None:
            authorization_code = self.authorize()
        resp = await self._request_tokens(authorization_code)
        self._extract_tokens(resp)


    def logged_in(self):
        return self._expires_at and self._expires_at > datetime.utcnow().timestamp()


    @staticmethod
    async def _request_tokens(code):
        data = {
            "client_id": "oneappsdkclient",
            "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
            "grant_type": "authorization_code",
            "code_verifier": "plain",
            "code": code
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{ToyotaOneAuth.BASE_URL}/access_token", data=data) as resp:
                return await resp.json()

    
    def _extract_tokens(self, token_resp):
        self._id_token = token_resp["id_token"]
        self._access_token = token_resp["access_token"]
        self._refresh_token = token_resp["refresh_token"]
        self._guid = jwt.decode(self._id_token, algorithms=["RS256"], options={"verify_signature": False})["sub"]
        self._expires_at = datetime.utcnow().timestamp() + token_resp["expires_in"]
        self.save()


    async def get_access_token(self):
        await self.check_tokens()
        return self._access_token

    async def get_guid(self):
        await self.check_tokens()
        return self._guid

    def save(self):
        with open(self._auth_file, "w") as fp:
            json.dump(fp=fp, indent=2, obj={
                "access_token": self._access_token,
                "refresh_token": self._refresh_token,
                "id_token": self._id_token,
                "expires_at": self._expires_at,
                "guid": self._guid
            })
    
    def load(self):
        with open(self._auth_file, "r") as fp:
            tokens = json.load(fp)
            self._access_token = tokens["access_token"]
            self._refresh_token = tokens["refresh_token"]
            self._id_token = tokens["id_token"]
            self._expires_at = tokens["expires_at"]
            self._guid = tokens["guid"]
