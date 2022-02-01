import logging
from urllib.parse import urljoin

import aiohttp

from .auth import ToyotaOneAuth


class ToyotaOneClient:
    API_GATEWAY = "https://oneapi.telematicsct.com/"
    API_KEY = "Y1aVonEtOa18cDwNLGTjt1zqD7aLahwc30WvvvQE"

    def __init__(self, auth=None) -> None:
        self.auth = auth or ToyotaOneAuth()

    async def _auth_headers(self):
        return {
            "AUTHORIZATION": "Bearer " + await self.auth.get_access_token(),
            "X-API-KEY": self.API_KEY,
            "X-GUID": await self.auth.get_guid(),
        }

    async def api_request(self, method, endpoint, header_params=None, **kwargs):
        headers = await self._auth_headers()
        if header_params:
            headers.update(header_params)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, urljoin(self.API_GATEWAY, endpoint), headers=headers, **kwargs
            ) as resp:
                resp.raise_for_status()
                try:
                    resp_json = await resp.json()
                    logging.info("Response status: %s", resp_json["status"])
                    return resp_json["payload"]
                except:
                    logging.error("Error parsing response: %s", await resp.text())
                    raise

    async def api_get(self, endpoint, header_params=None):
        return await self.api_request("GET", endpoint, header_params)

    async def api_post(self, endpoint, json, header_params=None):
        return await self.api_request("POST", endpoint, header_params, json=json)

    async def get_user_vehicle_list(self):
        return await self.api_get("v2/vehicle/guid")

    async def get_vehicle_detail(self, vin):
        return await self.api_get("v1/one/vehicle", {"VIN": vin})

    async def get_vehicle_health_report(self, vin):
        return await self.api_get("v1/vehiclehealth/report", {"VIN": vin})

    async def get_vehicle_health_status(self, vin):
        return await self.api_get("v1/vehiclehealth/status", {"VIN": vin})

    async def get_telemetry(self, vin, generation="17CYPLUS"):
        return await self.api_get(
            "/v2/telemetry", {"VIN": vin, "GENERATION": generation, "X-BRAND": "T"}
        )

    async def get_vehicle_status(self, vin, generation="17CYPLUS"):
        if generation == "17CY":
            return await self.get_vehicle_status_17cy(vin)
        elif generation == "17CYPLUS":
            return await self.get_vehicle_status_17cyplus(vin)
        else:
            value = {
                "error": {"code": "400", "message": "Unsupported Vehicle Generation"}
            }
            return value

    async def get_vehicle_status_17cy(self, vin):
        return await self.api_get(
            "v2/legacy/remote/status", {"X-BRAND": "T", "VIN": vin}
        )

    async def get_vehicle_status_17cyplus(self, vin):
        return await self.api_get("v1/global/remote/status", {"VIN": vin})

    async def get_engine_status(self, vin, generation="17CYPLUS"):
        if generation == "17CY":
            return await self.get_engine_status_17cy(vin)
        elif generation == "17CYPLUS":
            return await self.get_engine_status_17cyplus(vin)
        else:
            value = {
                "error": {"code": "400", "message": "Unsupported Vehicle Generation"}
            }
            return value

    async def get_engine_status_17cy(self, vin):
        return await self.api_get(
            "/v1/legacy/remote/engine-status", {"X-BRAND": "T", "VIN": vin}
        )

    async def get_engine_status_17cyplus(self, vin):
        return await self.api_get("v1/global/remote/engine-status", {"VIN": vin})

    async def send_refresh_status(self, vin, generation="17CYPLUS"):
        if generation == "17CY":
            return await self.send_refresh_request_17cy(vin)
        elif generation == "17CYPLUS":
            return await self.send_refresh_request_17cyplus(vin)
        else:
            value = {
                "error": {"code": "400", "message": "Unsupported Vehicle Generation"}
            }
            return value

    async def send_refresh_request_17cy(self, vin):
        return await self.api_post(
            "/v1/legacy/remote/refresh-status",
            {
                "guid": await self.auth.get_guid(),
                "deviceId": self.auth.get_device_id(),
                "deviceType": "Android",
                "vin": vin,
            },
            {"X-BRAND": "T", "VIN": vin},
        )

    async def send_refresh_request_17cyplus(self, vin):
        return await self.api_post(
            "/v1/global/remote/refresh-status",
            {
                "guid": await self.auth.get_guid(),
                "deviceId": self.auth.get_device_id(),
                "vin": vin,
            },
            {"VIN": vin},
        )

    async def remote_request(self, vin, command, value=None, generation="17CYPLUS"):
        """
        Handles the sending of remote commands to generation specific API endpoints.

        17CYPLUS possible commands include:
        "door-lock", "door-unlock", "engine-start", "engine-stop",
        "hazard-on", "hazard-off", "power-window-on", "power-window-off",
        "ac-settings-on", "sound-horn", "buzzer-warning",
        "find-vehicle", "ventilation-on"

        17CY commands require both a String command and an Int value:
        'command': 'DL', 'value': 1 == 'door-lock'
        'command': 'DL', 'value': 2 == 'door-unlock'
        'command': 'RES', 'value': 1 == 'engine-start'
        'command': 'RES', 'value': 2 == 'engine-stop'
        'command': 'HZ', 'value': 1 == 'hazard-on'
        'command': 'HZ', 'value': 2 == 'hazard-off'
        """
        if generation == "17CY":
            return await self.remote_request_17cy(vin, command, value)
        elif generation == "17CYPLUS":
            return await self.remote_request_17cyplus(vin, command)
        else:
            value = {
                "error": {"code": "400", "message": "Unsupported Vehicle Generation"}
            }
            return value

    async def remote_request_17cy(self, vin, command, value):
        """
        Handles remote command request for generation 17CY vehicles

        :param vin: Vehicle Identification Number
        :param command: String for given command set
        :param value: Int value to be passed with command to change state

        Possible Code/Value Combos:
        'command': 'DL', 'value': 1 == 'door-lock'
        'command': 'DL', 'value': 2 == 'door-unlock'
        'command': 'RES', 'value': 1 == 'engine-start'
        'command': 'RES', 'value': 2 == 'engine-stop'
        'command': 'HZ', 'value': 1 == 'hazard-on'
        'command': 'HZ', 'value': 2 == 'hazard-off'
        """
        return await self.api_post(
            "/v1/legacy/remote/command",
            {
                "command": {"code": command, "value": value},
                "guid": await self.auth.get_guid(),
                "deviceId": self.auth.get_device_id(),
                "deviceType": "Android",
                "vin": vin,
            },
            {"X-BRAND": "T", "VIN": vin},
        )

    async def remote_request_17cyplus(self, vin, command):
        """
        Handles remote command request for generation 17CYPLUS vehicles.

        17CYPLUS possible commands include:
        "door-lock", "door-unlock", "engine-start", "engine-stop",
        "hazard-on", "hazard-off", "power-window-on", "power-window-off",
        "ac-settings-on", "sound-horn", "buzzer-warning",
        "find-vehicle", "ventilation-on"
        """
        return await self.api_post(
            "/v1/global/remote/command", {"command": command}, {"VIN": vin}
        )
