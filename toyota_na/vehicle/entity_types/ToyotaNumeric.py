class ToyotaNumeric:
    _value: float
    _unit: str

    def __init__(self, value: float, unit: str):
        self._value = value
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    @value.setter
    def value(self, value: float):
        self._value = value

    @unit.setter
    def unit(self, unit: str):
        self._unit = unit

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self._value}, unit={self._unit})"
