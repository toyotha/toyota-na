from ..client import ToyotaOneClient
from .base_vehicle import ApiVehicleGeneration, ToyotaVehicle
from .vehicle_generations.seventeen_cy import SeventeenCYToyotaVehicle
from .vehicle_generations.seventeen_cy_plus import SeventeenCYPlusToyotaVehicle


async def get_vehicles(client: ToyotaOneClient) -> list[ToyotaVehicle]:
    api_vehicles = await client.get_user_vehicle_list()

    vehicles = []

    for (i, vehicle) in enumerate(api_vehicles):
        if (
            ApiVehicleGeneration(vehicle["generation"])
            == ApiVehicleGeneration.SeventeenCYPlus
        ):
            vehicle = SeventeenCYPlusToyotaVehicle(
                client=client,
                has_remote_subscription=vehicle["remoteSubscriptionStatus"] == "ACTIVE",
                model_name=vehicle["modelName"],
                model_year=vehicle["modelYear"],
                vin=vehicle["vin"],
            )

        elif (
            ApiVehicleGeneration(vehicle["generation"])
            == ApiVehicleGeneration.SeventeenCY
        ):
            vehicle = SeventeenCYToyotaVehicle(
                client=client,
                has_remote_subscription=vehicle["remoteSubscriptionStatus"] == "ACTIVE",
                model_name=vehicle["modelName"],
                model_year=vehicle["modelYear"],
                vin=vehicle["vin"],
            )

        await vehicle.update()
        vehicles.append(vehicle)

    return vehicles
