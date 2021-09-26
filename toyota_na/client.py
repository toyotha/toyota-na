from datetime import datetime
from urllib.parse import urljoin
import requests
import logging

from .auth import ToyotaOneAuth


class ToyotaOneClient:
    API_GATEWAY = "https://oneapi.telematicsct.com/"
    API_KEY = "Y1aVonEtOa18cDwNLGTjt1zqD7aLahwc30WvvvQE"

    def __init__(self) -> None:
        self.auth = ToyotaOneAuth()
        self.vehicle_list = None
    
    def _headers(self):
        return {
            "AUTHORIZATION": "Bearer " + self.auth.get_access_token(),
            "X-API-KEY": self.API_KEY,
            "X-GUID": self.auth.get_guid()
        }

    def api_get(self, endpoint, header_params=None):
        headers = self._headers()
        if header_params:
            headers.update(header_params)
        resp = requests.get(urljoin(self.API_GATEWAY, endpoint), headers=headers)
        resp.raise_for_status()
        try:
            resp_json = resp.json()
            logging.info("Response status: %s", resp_json["status"])
            return resp_json["payload"]
        except:
            logging.error("Error parsing response: %s", resp.text)
            raise

    def get_user_vehicle_list(self):
        self.vehicle_list = self.api_get("/v2/vehicle/guid")
        return self.vehicle_list

    def get_vehicle_detail(self, vin):
        return self.api_get("/v1/one/vehicle", {"VIN": vin})

    def get_vehicle_health_report(self, vin):
        return self.api_get("/v1/vehiclehealth/report", {"VIN": vin})

    def get_vehicle_health_status(self, vin):
        return self.api_get("/v1/vehiclehealth/status", {"VIN": vin})

    def get_vehicle_status(self, vin):
        return self.api_get("/v1/global/remote/status", {"VIN": vin})
    