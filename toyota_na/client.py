from datetime import datetime
from urllib.parse import urljoin
import requests

from .auth import login, refresh_token, get_guid


class Client:
    API_GATEWAY = "https://oneapi.telematicsct.com/"
    API_KEY = "Y1aVonEtOa18cDwNLGTjt1zqD7aLahwc30WvvvQE"

    def __init__(self) -> None:
        self.tokens = None
        self.guid = None
        self.expires_at = None

        self.vehicle_list = None
    
    def login(self):
        self.tokens = login()
        self.guid = get_guid(self.tokens["id_token"])
        self.expires_at = datetime.utcnow().timestamp() + self.tokens["expires_in"]

    def refresh_token(self):
        self.tokens = refresh_token(self.tokens["refresh_token"])
        self.guid = get_guid(self.tokens["id_token"])
        self.expires_at = datetime.utcnow().timestamp() + self.tokens["expires_in"]

    def _headers(self):
        return {
            "AUTHORIZATION": "Bearer " + self.tokens["access_token"],
            "X-API-KEY": self.API_KEY,
            "X-GUID": self.guid
        }

    def api_get(self, endpoint, header_params=None):
        if self.tokens is None:
            self.login()
        if datetime.utcnow().timestamp() > self.expires_at - 300:
            self.refresh_token()
        headers = self._headers()
        if header_params:
            headers.update(header_params)
        resp = requests.get(urljoin(self.API_GATEWAY, endpoint), headers=headers)
        resp.raise_for_status()
        resp_json = resp.json()
        try:
            print(resp_json["status"])
            return resp_json["payload"]
        except:
            print(resp.text)

    def get_user_vehicle_list(self):
        self.vehicle_list = self.api_get("/v2/vehicle/guid")
        return self.vehicle_list

    def get_vehicle_detail(self, vin=None):
        if not vin:
            vin = self.vehicle_list[0]["vin"]
        return self.api_get("/v1/one/vehicle", {"VIN": vin})

    def get_vehicle_health_report(self, vin=None):
        if not vin:
            vin = self.vehicle_list[0]["vin"]
        return self.api_get("/v1/vehiclehealth/report", {"VIN": vin})

    def get_vehicle_health_status(self, vin=None):
        if not vin:
            vin = self.vehicle_list[0]["vin"]
        return self.api_get("/v1/vehiclehealth/status", {"VIN": vin})

    def get_vehicle_status(self, vin=None):
        if not vin:
            vin = self.vehicle_list[0]["vin"]
        return self.api_get("/v1/global/remote/status", {"VIN": vin})