class ToyotaOpening:
    _closed: bool

    def __init__(self, closed=False):
        self._closed = closed

    @property
    def closed(self):
        return self._closed

    @closed.setter
    def closed(self, value):
        self._closed = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(closed={self._closed})"
