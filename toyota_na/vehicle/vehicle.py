from ..client import ToyotaOneClient
from .base_vehicle import ApiVehicleGeneration, ToyotaVehicle
from .vehicle_generations.seventeen_cy_plus import SeventeenCYPlusToyotaVehicle


async def get_vehicles(client: ToyotaOneClient) -> list[ToyotaVehicle]:
    api_vehicles = await client.get_user_vehicle_list()

    vehicles = []

    for (i, vehicle) in enumerate(api_vehicles):
        if (
            ApiVehicleGeneration(vehicle["generation"])
            == ApiVehicleGeneration.SeventeenCYPlus
        ):
            vehicle = SeventeenCYPlusToyotaVehicle(vin=vehicle["vin"], client=client)

            await vehicle.update()

            vehicles.append(vehicle)

    return vehicles
