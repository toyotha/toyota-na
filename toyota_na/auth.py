import sys
from datetime import datetime
import aiohttp
from urllib.parse import urlparse, parse_qs, urlencode
import jwt
import logging

from .exceptions import NotLoggedIn, TokenExpired, LoginError


class ToyotaOneAuth:
    BASE_URL = "https://login.toyotadriverslogin.com/oauth2/realms/root/realms/tmna-native"

    def __init__(self, callback=None, initial_tokens=None, refresh_secs=300):
        self._callback = callback
        self._refresh_secs = refresh_secs
        self._access_token = None
        self._refresh_token = None
        self._id_token = None
        self._guid = None
        self._expires_at = None
        self._updated_at = None
        try:
            if initial_tokens:
                self.set_tokens(initial_tokens)
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
            raise LoginError()
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
                if resp.status != 200:
                    raise LoginError()
                self._extract_tokens(await resp.json())

    async def request_tokens(self, code):
        data = {
            "client_id": "oneappsdkclient",
            "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
            "grant_type": "authorization_code",
            "code_verifier": "plain",
            "code": code
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{ToyotaOneAuth.BASE_URL}/access_token", data=data) as resp:
                if resp.status != 200:
                    raise LoginError()
                self._extract_tokens(await resp.json())

    async def check_tokens(self):
        if self._expires_at is None:
            raise NotLoggedIn()
        elif self._expires_at < datetime.utcnow().timestamp():
            raise TokenExpired()
        elif self._refresh_secs > 0 and datetime.utcnow().timestamp() > self._updated_at + self._refresh_secs:
            await self.refresh_tokens()
        elif self._refresh_secs < 0 and datetime.utcnow().timestamp() > self._expires_at + self._refresh_secs:
            await self.refresh_tokens()
        elif self._refresh_secs == 0:
            await self.refresh_tokens()

    async def login(self, authorization_code=None):
        if authorization_code is None:
            authorization_code = self.authorize()
        await self.request_tokens(authorization_code)

    def logged_in(self):
        return self._expires_at and self._expires_at > datetime.utcnow().timestamp()

    def _extract_tokens(self, token_resp):
        self._id_token = token_resp["id_token"]
        self._access_token = token_resp["access_token"]
        self._refresh_token = token_resp["refresh_token"]
        self._guid = jwt.decode(
            self._id_token,
            algorithms=["RS256"],
            options={"verify_signature": False},
            audience="oneappsdkclient"
        )["sub"]
        self._expires_at = datetime.utcnow().timestamp() + token_resp["expires_in"]
        self._updated_at = datetime.utcnow().timestamp()
        if self._callback:
            try:
                self._callback(self.get_tokens())
            except:
                logging.exception("Callback failed")

    async def get_access_token(self):
        await self.check_tokens()
        return self._access_token

    async def get_guid(self):
        await self.check_tokens()
        return self._guid

    async def get_id_info(self):
        await self.check_tokens()
        return jwt.decode(
            self._id_token,
            algorithms=["RS256"],
            options={"verify_signature": False},
            audience="oneappsdkclient"
        )

    def get_tokens(self):
        return {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "id_token": self._id_token,
            "expires_at": self._expires_at,
            "guid": self._guid
        }

    def set_tokens(self, tokens):
        self._access_token = tokens["access_token"]
        self._refresh_token = tokens["refresh_token"]
        self._id_token = tokens["id_token"]
        self._expires_at = tokens["expires_at"]
        self._guid = tokens["guid"]
