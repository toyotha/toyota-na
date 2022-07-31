import json
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest

from toyota_na.vehicle.base_vehicle import ApiVehicleGeneration
from toyota_na.vehicle.vehicle import get_vehicles


@pytest.fixture
async def base_client():

    eletric_status = open("./samples/electric_status.json", "r", encoding="utf-8")
    engine_status = open("./samples/engine_status.json", "r", encoding="utf-8")
    telemetry = open("./samples/telemetry.json", "r", encoding="utf-8")

    client = MagicMock()
    client.get_electric_status = AsyncMock(return_value=json.load(eletric_status))
    client.get_engine_status = AsyncMock(return_value=json.load(engine_status))
    client.get_telemetry = AsyncMock(return_value=json.load(telemetry))
    return client


@pytest.fixture
async def CY17Plus_client(base_client):

    vehicle_list = open(
        "./samples/17CYPLUS/user_vehicle_list.json", "r", encoding="utf-8"
    )
    vehicle_status = open(
        "./samples/17CYPLUS/vehicle_status.json", "r", encoding="utf-8"
    )

    base_client.get_user_vehicle_list = AsyncMock(return_value=json.load(vehicle_list))
    base_client.get_vehicle_status = AsyncMock(return_value=json.load(vehicle_status))
    return base_client


@pytest.fixture
async def MM21_client(base_client):

    vehicle_list = open("./samples/21MM/user_vehicle_list.json", "r", encoding="utf-8")
    vehicle_status = open(
        "./samples/17CYPLUS/vehicle_status.json", "r", encoding="utf-8"
    )

    base_client.get_user_vehicle_list = AsyncMock(return_value=json.load(vehicle_list))
    base_client.get_vehicle_status = AsyncMock(return_value=json.load(vehicle_status))
    return base_client


class TestBaseVehicle:
    async def test_get_vehicle(self, CY17Plus_client):
        vehicles = await get_vehicles(CY17Plus_client)

        assert len(vehicles) == 1
        assert vehicles[0].vin == "4T1B11HK4KU2XXXXX"
        assert vehicles[0].generation == ApiVehicleGeneration.CY17PLUS

    async def test_mm21_vehicle(self, MM21_client):

        vehicles = await get_vehicles(MM21_client)

        assert len(vehicles) == 1
        # For the time being MM21 is a CY17PLUS in our world :)
        assert vehicles[0].generation == ApiVehicleGeneration.CY17PLUS
