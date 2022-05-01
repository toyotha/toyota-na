import json
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest

from toyota_na.vehicle.base_vehicle import ApiVehicleGeneration
from toyota_na.vehicle.vehicle import get_vehicles


@pytest.fixture
async def client():

    vehicle_list = open("./samples/user_vehicle_list.json", "r", encoding="utf-8")
    vehicle_status = open("./samples/vehicle_status.json", "r", encoding="utf-8")
    telemetry = open("./samples/vehicle_health_status.json", "r", encoding="utf-8")
    engine_status = open("./samples/engine_status.json", "r", encoding="utf-8")

    mock_client = MagicMock()
    mock_client.get_user_vehicle_list = AsyncMock(return_value=json.load(vehicle_list))
    mock_client.get_vehicle_status = AsyncMock(return_value=json.load(vehicle_status))
    mock_client.get_telemetry = AsyncMock(return_value=json.load(telemetry))
    mock_client.get_engine_status = AsyncMock(return_value=json.load(engine_status))
    return mock_client


class TestBaseVehicle:
    async def test_get_vehicle(self, client):
        vehicles = await get_vehicles(client)
        assert len(vehicles) == 1
        assert vehicles[0].vin == "4T1B11HK4KU2XXXXX"
        assert vehicles[0].generation == ApiVehicleGeneration.SeventeenCYPlus
