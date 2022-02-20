from abc import ABC, abstractmethod
from enum import Enum, auto, unique
from typing import Union

from ..client import ToyotaOneClient
from .entity_types.ToyotaLocation import ToyotaLocation
from .entity_types.ToyotaLockableOpening import ToyotaLockableOpening
from .entity_types.ToyotaNumeric import ToyotaNumeric
from .entity_types.ToyotaOpening import ToyotaOpening
from .entity_types.ToyotaRemoteStart import ToyotaRemoteStart


@unique
class ApiVehicleGeneration(Enum):
    SeventeenCYPlus = "17CYPLUS"
    SeventeenCY = "17CY"


@unique
class VehicleFeatures(Enum):
    # Doors/Windows
    FrontDriverDoor = auto()
    FrontDriverWindow = auto()
    FrontPassengerDoor = auto()
    FrontPassengerWindow = auto()
    RearDriverDoor = auto()
    RearDriverWindow = auto()
    RearPassengerDoor = auto()
    RearPassengerWindow = auto()
    Trunk = auto()
    Moonroof = auto()
    Hood = auto()

    # Numeric values
    DistanceToEmpty = auto()
    FrontDriverTire = auto()
    FrontPassengerTire = auto()
    RearDriverTire = auto()
    RearPassengerTire = auto()
    SpareTirePressure = auto()
    FuelLevel = auto()
    Odometer = auto()
    TripDetailsA = auto()
    TripDetailsB = auto()

    # Engine status
    RemoteStartStatus = auto()

    # Location
    RealTimeLocation = auto()
    ParkingLocation = auto()


@unique
class RemoteRequestCommand(Enum):
    DoorLock = auto()
    DoorUnlock = auto()
    EngineStart = auto()
    EngineStop = auto()
    HazardsOn = auto()
    HazardsOff = auto()


class ToyotaVehicle(ABC):
    """Vehicle control and metadata object."""

    _client: ToyotaOneClient
    _features: dict[
        VehicleFeatures,
        Union[
            ToyotaLocation,
            ToyotaLockableOpening,
            ToyotaNumeric,
            ToyotaRemoteStart,
            ToyotaOpening,
        ],
    ]
    _has_remote_subscription = False
    _model_name: str
    _model_year: str
    _generation: ApiVehicleGeneration
    _vin: str

    def __init__(
        self,
        client: ToyotaOneClient,
        has_remote_subscription,
        model_name: str,
        model_year: str,
        vin: str,
        generation: ApiVehicleGeneration,
    ):
        """
        Initialize a new vehicle object. Must call `vehicle.update()` to fully populate the object.

        :param vin: Vehicle identification number
        """

        self._features = {}
        self._client = client
        self._generation = generation
        self._has_remote_subscription = has_remote_subscription
        self._model_name = model_name
        self._model_year = model_year
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
    def features(
        self,
    ) -> dict[
        VehicleFeatures,
        Union[
            ToyotaLocation,
            ToyotaLockableOpening,
            ToyotaNumeric,
            ToyotaOpening,
            ToyotaRemoteStart,
        ],
    ]:
        """Provides a programmatic representation of all the features of the vehicle and their current states."""
        return self._features

    # We only very sparingly expose direct properties. Most vehicle atrributes should be added to the features dictionary.
    @property
    def generation(self):
        return self._generation

    @property
    def model_name(self):
        return self._model_name

    @property
    def model_year(self):
        return self._model_year

    @property
    def subscribed(self):
        return self._has_remote_subscription

    @property
    def vin(self):
        return self._vin

    def __repr__(self):
        str = f"{self.__class__.__name__}(\n    features=(\n"
        for key, value in self._features.items():
            str += f"       {key}={value}\n"
        return f"{str}  )\n)"
