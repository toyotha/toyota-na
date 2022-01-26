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


class ToyotaLockableOpening(ToyotaOpening):
    _locked: bool

    def __init__(self, closed: bool = False, locked: bool = False):
        ToyotaOpening.__init__(self, closed)
        self._locked = locked

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value):
        self._locked = value
