from ...client import ToyotaOneClient
from ..base_vehicle import (
    ApiVehicleGeneration,
    RemoteRequestCommand,
    ToyotaVehicle,
    VehicleFeatures,
)
from ..entity_types.ToyotaLocation import ToyotaLocation
from ..entity_types.ToyotaLockableOpening import ToyotaLockableOpening
from ..entity_types.ToyotaNumeric import ToyotaNumeric
from ..entity_types.ToyotaOpening import ToyotaOpening
from ..entity_types.ToyotaRemoteStart import ToyotaRemoteStart


class SeventeenCYPlusToyotaVehicle(ToyotaVehicle):

    _command_map = {
        RemoteRequestCommand.DoorLock: "door-lock",
        RemoteRequestCommand.DoorUnlock: "door-unlock",
        RemoteRequestCommand.EngineStart: "engine-start",
        RemoteRequestCommand.EngineStop: "engine-stop",
        RemoteRequestCommand.HazardsOn: "hazard-on",
        RemoteRequestCommand.HazardsOff: "hazard-off",
    }

    #  We'll parse these keys out in the parser by mapping the category and section types to a string literal
    _vehicle_status_category_map = {
        "Driver Side Door": VehicleFeatures.FrontDriverDoor,
        "Driver Side Window": VehicleFeatures.FrontDriverWindow,
        "Passenger Side Door": VehicleFeatures.FrontPassengerDoor,
        "Passenger Side Window": VehicleFeatures.FrontPassengerWindow,
        "Driver Side Rear Door": VehicleFeatures.RearDriverDoor,
        "Driver Side Rear Window": VehicleFeatures.RearDriverWindow,
        "Passenger Side Rear Door": VehicleFeatures.RearPassengerDoor,
        "Passenger Side Rear Window": VehicleFeatures.RearPassengerWindow,
        "Other Hatch": VehicleFeatures.Trunk,
        "Other Moonroof": VehicleFeatures.Moonroof,
        "Other Hood": VehicleFeatures.Hood,
    }

    _vehicle_telemetry_map = {
        "distanceToEmpty": VehicleFeatures.DistanceToEmpty,
        "flTirePressure": VehicleFeatures.FrontDriverTire,
        "frTirePressure": VehicleFeatures.FrontPassengerTire,
        "rlTirePressure": VehicleFeatures.RearDriverTire,
        "rrTirePressure": VehicleFeatures.RearPassengerTire,
        "fuelLevel": VehicleFeatures.FuelLevel,
        "odometer": VehicleFeatures.Odometer,
        "spareTirePressure": VehicleFeatures.SpareTirePressure,
        "tripA": VehicleFeatures.TripDetailsA,
        "tripB": VehicleFeatures.TripDetailsB,
        "vehicleLocation": VehicleFeatures.ParkingLocation,
        "nextService": VehicleFeatures.NextService,
    }

    def __init__(
        self,
        client: ToyotaOneClient,
        has_remote_subscription: bool,
        model_name: str,
        model_year: str,
        vin: str,
    ):
        ToyotaVehicle.__init__(
            self,
            client,
            has_remote_subscription,
            model_name,
            model_year,
            vin,
            ApiVehicleGeneration.SeventeenCYPlus,
        )

    async def update(self):

        # vehicle_health_status
        vehicle_status = await self._client.get_vehicle_status(self._vin)
        self._parse_vehicle_status(vehicle_status)

        # telemetry
        telemetry = await self._client.get_telemetry(self._vin)
        self._parse_telemetry(telemetry)

        # engine_status
        engine_status = await self._client.get_engine_status(self._vin)
        self._parse_engine_status(engine_status)

        # vehicle_charge_status
        # etc.

    async def poll_vehicle_refresh(self) -> None:
        """Instructs Toyota's systems to ping the vehicle to upload a fresh status. Useful when certain actions have been taken, such as locking or unlocking doors."""
        await self._client.send_refresh_status(self._vin)

    async def send_command(self, command: RemoteRequestCommand) -> None:
        """Start the engine. Periodically refreshes the vehicle status to determine if the engine is running."""
        await self._client.remote_request(self._vin, self._command_map[command])

    #
    # engine_status
    #

    def _parse_engine_status(self, engine_status: dict) -> None:

        self._features[VehicleFeatures.RemoteStartStatus] = ToyotaRemoteStart(
            date=engine_status.get("date"),
            on=engine_status["status"] == "1",
            timer=engine_status.get("timer"),
        )

    #
    # vehicle_health_status
    #

    def _isClosed(self, section) -> bool:
        return section["values"][0]["value"].lower() == "closed"

    def _isLocked(self, section) -> bool:
        return section["values"][1]["value"].lower() == "locked"

    def _parse_vehicle_status(self, vehicle_status: dict) -> None:

        # Real-time location is a one-off, so we'll just parse it out here
        if "latitude" in vehicle_status and "longitude" in vehicle_status:
            self._features[VehicleFeatures.ParkingLocation] = ToyotaLocation(
                vehicle_status["latitude"], vehicle_status["longitude"]
            )

        for category in vehicle_status["vehicleStatus"]:
            for section in category["sections"]:

                category_type = category["category"]
                section_type = section["section"]

                key = f"{category_type} {section_type}"

                # We don't support all features necessarily. So avoid throwing on a key error.
                if self._vehicle_status_category_map.get(key) is not None:

                    # CLOSED is always the first value entry. So we can use it to determine which subtype to instantiate
                    if section["values"].__len__() == 1:
                        self._features[
                            self._vehicle_status_category_map[key]
                        ] = ToyotaOpening(self._isClosed(section))
                    else:
                        self._features[
                            self._vehicle_status_category_map[key]
                        ] = ToyotaLockableOpening(
                            closed=self._isClosed(section),
                            locked=self._isLocked(section),
                        )

    #
    # get_telemetry
    #

    def _parse_telemetry(self, telemetry: dict) -> None:
        for key, value in telemetry.items():

            # fuel level is a primitive
            if key == "fuelLevel":
                self._features[VehicleFeatures.FuelLevel] = ToyotaNumeric(value, "%")
                continue

            # vehicle_location has a different shape and different target entity class
            if key == "vehicleLocation":
                self._features[VehicleFeatures.RealTimeLocation] = ToyotaLocation(
                    value["latitude"], value["longitude"]
                )
                continue

            if self._vehicle_telemetry_map.get(key) is not None and value is not None:
                self._features[self._vehicle_telemetry_map[key]] = ToyotaNumeric(
                    value["value"], value["unit"]
                )
                continue
