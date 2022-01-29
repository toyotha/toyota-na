from datetime import datetime
from typing import Optional


class ToyotaRemoteStart:
    _date: Optional[datetime]
    _on: bool
    _time_left: Optional[float]

    def __init__(self, date: Optional[datetime], on: bool, time_left: Optional[float]):
        self._date = date
        self._on = on
        self._time_left = time_left

    @property
    def date(self) -> Optional[datetime]:
        return self._date

    @property
    def on(self) -> bool:
        return self._on

    @property
    def time_left(self) -> Optional[float]:
        return self._time_left

    @date.setter
    def date(self, value: Optional[str]):
        if value is None:
            self._date = None
        else:
            self._date = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

    @on.setter
    def on(self, value: bool) -> None:
        self._on = value

    @time_left.setter
    def time_left(self, value: float):
        self._time_left = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(date={self._date}, on={self._on}, time_left={self._time_left})"
