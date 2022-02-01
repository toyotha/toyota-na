class ToyotaLocation:
    _lat: float
    _long: float

    def __init__(self, lat: float, long: float):
        self._lat = lat
        self._long = long

    @property
    def lat(self) -> float:
        return self._lat

    @lat.setter
    def lat(self, value: float) -> None:
        self._lat = value

    @property
    def value(self) -> float:
        return self._long

    @value.setter
    def value(self, value: float) -> None:
        self._long = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lat={self._lat}, long={self._long})"
