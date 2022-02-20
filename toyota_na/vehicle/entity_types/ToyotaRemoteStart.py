from datetime import datetime, timedelta
from typing import Optional

import pytz


class ToyotaRemoteStart:
    _on: bool
    _start_time: Optional[datetime]
    _timer: Optional[float]

    def __init__(self, date: Optional[str], on: bool, timer: Optional[float]):
        if date is not None:
            self._start_time = datetime.strptime(
                f"{date}", "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=pytz.UTC)
        else:
            self._start_time = None
        self._on = on
        self._timer = timer

    @property
    def end_time(self) -> Optional[datetime]:
        if self._start_time is not None and self._timer is not None:
            return self._start_time.__add__(timedelta(minutes=self._timer))

    @property
    def on(self) -> bool:
        """Returns whether or not the vehicle is remote started"""
        return self._on

    @property
    def start_time(self) -> Optional[datetime]:
        return self._start_time

    @property
    def time_left(self) -> Optional[float]:
        """Returns the time left in minutes if the vehicle is on"""
        if self.end_time is not None and self._timer is not None:
            # do it this way to get the convenience of a `timedelta` object for grabbing the seconds
            return (
                self.end_time.__sub__(
                    # bit of a hack to get the tz to match but it works
                    datetime.utcnow().replace(tzinfo=pytz.UTC)
                ).total_seconds()
                / 60
            )

    @property
    def timer(self) -> Optional[float]:
        """Returns the total time the vehicle will run in minutes when remote started"""
        return self._timer

    @on.setter
    def on(self, value: bool) -> None:
        self._on = value

    @start_time.setter
    def start_time(self, value: Optional[datetime]):
        self._start_time = value

    @timer.setter
    def timer(self, value: float):
        self._timer = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(end_time={self.end_time}, on={self._on}, start_time={self.start_time}, time_left={self.time_left})"
