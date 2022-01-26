from unicodedata import category
from xml.dom.minidom import Attr
from ..client import ToyotaOneClient
from abc import ABC, abstractmethod
from enum import Enum, unique, auto
from typing import cast, Union, Optional

from .doors import ToyotaLockableOpening, ToyotaOpening


@unique
class Generation(Enum):
    SeventeenCYPlus = "17CYPLUS"
    SeventeenCY = "17CY"


@unique
class VehicleFeatures(Enum):
    FrontDriverDoor = auto()
    FrontDriverWindow = auto()
    FrontPassengerDoor = auto()
    FrontPassengerWindow = auto()
    RearDriverDoor = auto()
    RearDriverWindow = auto()
    RearPassengerDoor = auto()
    RearPassengerWindow = auto()
    TrunkDoors = auto()
    MoonroofWindow = auto()
    HoodDoor = auto()


@unique
class RemoteRequestCommand(Enum):
    DOOR_LOCK = auto()
    DOOR_UNLOCK = auto()
    ENGINE_START = auto()
    ENGINE_STOP = auto()
    HAZARD_ON = auto()
    HAZARD_OFF = auto()


class ToyotaVehicle(ABC):
    """Vehicle control and metadata object."""

    _attributes: dict[VehicleFeatures, Union[ToyotaLockableOpening, ToyotaOpening]]
    _client: ToyotaOneClient
    _generation: Generation
    _vin: str

    def __init__(
        self,
        vin: str,
        client: ToyotaOneClient,
        generation: Generation,
    ):
        """
        Initialize a new vehicle object. Must call `vehicle.update()` to fully populate the object.

        :param vin: Vehicle identification number
        """

        self._attributes = {}
        self._client = client
        self._generation = generation
        self._vin = vin

    @abstractmethod
    async def poll_vehicle_refresh(self) -> None:
        """Instructs Toyota's systems to ping the vehicle to upload a fresh status. Useful when certain actions have been taken, such as locking or unlocking doors."""
        pass

    @abstractmethod
    async def send_command(self, command: RemoteRequestCommand) -> None:
        """Start the engine. Periodically refreshes the vehicle status to determine if the engine is running."""
        pass

    @abstractmethod
    async def update(self):
        """Calls the required Toyota APIs and instantiates all the attributes."""
        pass

    @property
    def attributes(
        self,
    ) -> dict[VehicleFeatures, Union[ToyotaLockableOpening, ToyotaOpening]]:
        """Provides a programmatic representation of all the features of the vehicle and their current states."""
        return self._attributes

    #
    # Misc
    #

    @property
    def generation(self):
        return self._generation

    @property
    def vin(self):
        return self._vin

    #
    # Doors
    #

    @property
    def front_driver_door(self) -> Optional[ToyotaLockableOpening]:
        return cast(
            ToyotaLockableOpening,
            self._attributes.get(VehicleFeatures.FrontDriverDoor),
        )

    @property
    def front_passenger_door(self) -> Optional[ToyotaLockableOpening]:
        return cast(
            ToyotaLockableOpening,
            self._attributes.get(VehicleFeatures.FrontPassengerDoor),
        )

    @property
    def rear_driver_door(self) -> Optional[ToyotaLockableOpening]:
        return cast(
            ToyotaLockableOpening, self._attributes.get(VehicleFeatures.RearDriverDoor)
        )

    @property
    def rear_passenger_door(self) -> Optional[ToyotaLockableOpening]:
        return cast(
            ToyotaLockableOpening,
            self._attributes.get(VehicleFeatures.RearPassengerDoor),
        )

    #
    # Windows
    #

    @property
    def front_driver_window(self) -> Optional[ToyotaOpening]:
        return cast(
            ToyotaOpening, self._attributes.get(VehicleFeatures.FrontDriverWindow)
        )

    @property
    def front_passenger_window(self) -> Optional[ToyotaOpening]:
        return cast(
            ToyotaOpening, self._attributes.get(VehicleFeatures.FrontPassengerWindow)
        )

    @property
    def rear_driver_window(self) -> Optional[ToyotaOpening]:
        return cast(
            ToyotaOpening, self._attributes.get(VehicleFeatures.RearDriverWindow)
        )

    @property
    def rear_passenger_window(self) -> Optional[ToyotaOpening]:
        return cast(
            ToyotaOpening, self._attributes.get(VehicleFeatures.RearPassengerWindow)
        )


class SeventeenCYPlusToyotaVehicle(ToyotaVehicle):

    _command_map = {
        RemoteRequestCommand.DOOR_LOCK: "door-lock",
        RemoteRequestCommand.DOOR_UNLOCK: "door-unlock",
        RemoteRequestCommand.ENGINE_START: "engine-start",
        RemoteRequestCommand.ENGINE_STOP: "engine-stop",
        RemoteRequestCommand.HAZARD_ON: "hazard-on",
        RemoteRequestCommand.HAZARD_OFF: "hazard-off",
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
        "Other Hatch": VehicleFeatures.TrunkDoors,
        "Other Moonroof": VehicleFeatures.MoonroofWindow,
        "Other Hood": VehicleFeatures.HoodDoor,
    }

    def __init__(self, vin: str, client: ToyotaOneClient):
        ToyotaVehicle.__init__(self, vin, client, Generation.SeventeenCYPlus)

    async def update(self):

        # vehicle_health_status
        vehicle_status = await self._client.get_vehicle_status(self._vin)
        self._parse_vehicle_status(vehicle_status)

        # vehicle_engine_status
        # etc.

        # vehicle_charge_status
        # etc.

    async def poll_vehicle_refresh(self) -> None:
        """Instructs Toyota's systems to ping the vehicle to upload a fresh status. Useful when certain actions have been taken, such as locking or unlocking doors."""
        await self._client.send_refresh_status(self._vin)

    async def send_command(self, command: RemoteRequestCommand) -> None:
        """Start the engine. Periodically refreshes the vehicle status to determine if the engine is running."""
        await self._client.remote_request(self._vin, self._command_map[command])

    #
    # vehicle_health_status
    #

    def _isClosed(self, section) -> bool:
        return section["values"][0]["value"].lower() == "closed"

    def _isLocked(self, section) -> bool:
        return section["values"][1]["value"].lower() == "locked"

    def _parse_vehicle_status(self, vehicle_status: dict) -> None:
        for category in vehicle_status["vehicleStatus"]:
            for section in category["sections"]:

                category_type = category["category"]
                section_type = section["section"]

                key = f"{category_type} {section_type}"

                # We don't support all features necessarily. So avoid throwing on a key error.
                if self._vehicle_status_category_map.get(key) is not None:

                    # CLOSED is always the first value entry. So we can use it to determine which subtype to instantiate
                    if section["values"].__len__() == 1:
                        self._attributes[
                            self._vehicle_status_category_map[key]
                        ] = ToyotaOpening(self._isClosed(section))
                    else:
                        self._attributes[
                            self._vehicle_status_category_map[key]
                        ] = ToyotaLockableOpening(
                            closed=self._isClosed(section),
                            locked=self._isLocked(section),
                        )


async def get_vehicles(client: ToyotaOneClient) -> list[ToyotaVehicle]:
    api_vehicles = await client.get_user_vehicle_list()

    vehicles = []

    for (i, vehicle) in enumerate(api_vehicles):
        if Generation(vehicle["generation"]) == Generation.SeventeenCYPlus:
            vehicles.append(
                SeventeenCYPlusToyotaVehicle(vin=vehicle["vin"], client=client)
            )

    return vehicles
