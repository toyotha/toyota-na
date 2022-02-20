import json
import logging
import random
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse

import aiohttp
import jwt

from .exceptions import LoginError, NotLoggedIn, TokenExpired


class ToyotaOneAuth:
    ACCESS_TOKEN_URL = "https://login.toyotadriverslogin.com/oauth2/realms/root/realms/tmna-native/access_token"
    AUTHORIZE_URL = "https://login.toyotadriverslogin.com/oauth2/realms/root/realms/tmna-native/authorize"
    AUTHENTICATE_URL = "https://login.toyotadriverslogin.com/json/realms/root/realms/tmna-native/authenticate"

    def __init__(self, callback=None, initial_tokens=None, refresh_secs=300):
        self._callback = callback
        self._refresh_secs = refresh_secs
        self._access_token = None
        self._refresh_token = None
        self._id_token = None
        self._guid = None
        self._expires_at = None
        self._updated_at = None
        self._device_id = None
        try:
            if initial_tokens:
                self.set_tokens(initial_tokens)
        except:
            pass

    async def authorize(self, username, password):
        async with aiohttp.ClientSession() as session:
            headers = {"Accept-API-Version": "resource=2.1, protocol=1.0"}
            data = {}
            for _ in range(10):
                if "callbacks" in data:
                    for cb in data["callbacks"]:
                        if (
                            cb["type"] == "NameCallback"
                            and cb["output"][0]["value"] == "User Name"
                        ):
                            cb["input"][0]["value"] = username
                        elif cb["type"] == "PasswordCallback":
                            cb["input"][0]["value"] = password
                async with session.post(
                    f"{ToyotaOneAuth.AUTHENTICATE_URL}", json=data, headers=headers
                ) as resp:
                    if resp.status != 200:
                        logging.info(await resp.text())
                        raise LoginError()
                    data = await resp.json()
                    if "tokenId" in data:
                        break
            if "tokenId" not in data:
                logging.error(json.dumps(data))
                raise LoginError()
            headers["Cookie"] = f"iPlanetDirectoryPro={data['tokenId']}"
            auth_params = {
                "client_id": "oneappsdkclient",
                "scope": "openid profile write",
                "response_type": "code",
                "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
                "code_challenge": "plain",
                "code_challenge_method": "plain",
            }
            AUTHORIZE_URL_QS = f"{ToyotaOneAuth.AUTHORIZE_URL}?{urlencode(auth_params)}"
            async with session.get(
                AUTHORIZE_URL_QS, headers=headers, allow_redirects=False
            ) as resp:
                if resp.status != 302:
                    logging.error(resp.text())
                    raise LoginError()
                redir = resp.headers["Location"]
                query = parse_qs(urlparse(redir).query)
                if "code" not in query:
                    logging.error(redir)
                    raise LoginError()
                return query["code"][0]

    async def refresh_tokens(self):
        data = {
            "client_id": "oneappsdkclient",
            "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
            "grant_type": "refresh_token",
            "code_verifier": "plain",
            "refresh_token": self._refresh_token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(ToyotaOneAuth.ACCESS_TOKEN_URL, data=data) as resp:
                if resp.status != 200:
                    raise LoginError()
                self._extract_tokens(await resp.json())

    async def request_tokens(self, code):
        data = {
            "client_id": "oneappsdkclient",
            "redirect_uri": "com.toyota.oneapp:/oauth2Callback",
            "grant_type": "authorization_code",
            "code_verifier": "plain",
            "code": code,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(ToyotaOneAuth.ACCESS_TOKEN_URL, data=data) as resp:
                if resp.status != 200:
                    raise LoginError()
                self._extract_tokens(await resp.json())

    async def check_tokens(self):
        if self._expires_at is None:
            raise NotLoggedIn()
        elif self._expires_at < datetime.utcnow().timestamp():
            try:
                await self.refresh_tokens()
            except LoginError:
                raise TokenExpired()
        elif (
            self._refresh_secs > 0
            and datetime.utcnow().timestamp() > self._updated_at + self._refresh_secs
        ):
            await self.refresh_tokens()
        elif (
            self._refresh_secs < 0
            and datetime.utcnow().timestamp() > self._expires_at + self._refresh_secs
        ):
            await self.refresh_tokens()
        elif self._refresh_secs == 0:
            await self.refresh_tokens()

    async def login(self, username, password):
        authorization_code = await self.authorize(username, password)
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
            audience="oneappsdkclient",
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
            audience="oneappsdkclient",
        )

    def get_tokens(self):
        return {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "id_token": self._id_token,
            "expires_at": self._expires_at,
            "updated_at": self._updated_at,
            "guid": self._guid,
        }

    def set_tokens(self, tokens):
        self._access_token = tokens["access_token"]
        self._refresh_token = tokens["refresh_token"]
        self._id_token = tokens["id_token"]
        self._expires_at = tokens["expires_at"]
        self._updated_at = tokens["updated_at"]
        self._guid = tokens["guid"]

    def get_device_id(self):
        if not self._device_id:
            self._device_id = self._generate_new_device_id()
        return self._device_id

    def set_device_id(self, device_id):
        self._device_id = device_id

    def _generate_new_device_id(self):
        return "%030x" % random.randrange(16**64)
