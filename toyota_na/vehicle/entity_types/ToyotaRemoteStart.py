from datetime import datetime, timedelta
from typing import Optional


class ToyotaRemoteStart:
    _date: Optional[datetime]
    _on: bool
    _timer: Optional[float]

    def __init__(self, date: Optional[str], on: bool, timer: Optional[float]):
        if date is not None:
            self._date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self._date = None
        self._on = on
        self._timer = timer

    @property
    def date(self) -> Optional[datetime]:
        return self._date

    @property
    def on(self) -> bool:
        """Returns whether or not the vehicle is remote started"""
        return self._on

    @property
    def time_left(self) -> Optional[float]:
        """Returns the time left in minutes if the vehicle is on"""
        if self._date is not None and self._timer is not None:
            # do it this way to get the convenience of a `timedelta` object for grabbing the seconds
            datetime_ending = self._date.__sub__(timedelta(minutes=self._timer))
            return self._date.__sub__(datetime_ending).total_seconds() / 60
        return None

    @property
    def timer(self) -> Optional[float]:
        """Returns the total time the vehicle will run in minutes when remote started"""
        return self._timer

    @date.setter
    def date(self, value: Optional[datetime]):
        self._date = value

    @on.setter
    def on(self, value: bool) -> None:
        self._on = value

    @timer.setter
    def timer(self, value: float):
        self._timer = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(date={self._date}, on={self._on}, time_left={self._time_left})"
